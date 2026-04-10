# QuickNote 隨手筆記 Design Spec

> **For agentic workers:** Use superpowers:executing-plans to implement this plan.

**Goal:** 給定任意 URL，自動偵測內容類型、擷取內容、生成摘要，存入 Obsidian `/隨手筆記/` 資料夾。

**Architecture:** 模組化 Python 專案（方案 B）。`router.py` 判斷 URL 類型，各 `handlers/` 處理不同來源，`summarizer.py` 統一呼叫 LLM，`obsidian.py` 寫入筆記。

**Tech Stack:** Python、google-genai（Gemma 4）、notebooklm-py、yt-dlp、ffmpeg、OpenCLI

---

## 專案結構

```
quicknote/
├── quicknote.py          ← CLI 入口：quicknote <URL> [--lang zh-tw]
├── router.py             ← URL 類型偵測
├── handlers/
│   ├── __init__.py
│   ├── youtube.py        ← YouTube → NotebookLM
│   ├── instagram.py      ← IG/Threads/FB 影片 → yt-dlp + ffmpeg + Gemma
│   │                        IG/Threads/FB 文字 → OpenCLI + Gemma
│   ├── webpage.py        ← 一般網頁 → NotebookLM（失敗則 OpenCLI fallback）
│   └── video.py          ← 直接影片 URL → yt-dlp + ffmpeg + Gemma
├── summarizer.py         ← 統一摘要介面（Gemma / NotebookLM）
├── obsidian.py           ← 寫入 Obsidian 筆記
├── config.py             ← 設定（Obsidian 路徑、API key、預設語言）
├── requirements.txt
└── README.md
```

---

## URL 路由邏輯

`router.py` 依照以下優先順序判斷：

| URL 特徵 | 類型 | Handler |
|---------|------|---------|
| `youtube.com`, `youtu.be` | YouTube | `youtube.py` |
| `instagram.com/reels/`, `instagram.com/p/` | IG 貼文/影片 | `instagram.py` |
| `threads.net`, `facebook.com` | Threads/FB | `instagram.py`（共用）|
| URL 結尾 `.mp4`, `.mov`, `.webm` | 直接影片 | `video.py` |
| 其他 | 一般網頁 | `webpage.py` |

---

## 各 Handler 流程

### YouTube（`youtube.py`）
```
URL → notebooklm create → notebooklm source add URL
    → notebooklm ask "請用繁體中文摘要..."
    → yt-dlp 下載縮圖（thumbnail）
    → 回傳摘要 + 縮圖路徑
```

### Instagram / Threads / FB（`instagram.py`）
```
偵測是否為影片 URL
  ├─ 是影片：
  │     yt-dlp 下載影片（--cookies-from-browser chrome）
  │     ffmpeg 抽全部影格（fps=1）
  │     Gemma 4 26B MoE 分析影格序列
  │     ffmpeg 抽第 1 張影格作為縮圖
  │     回傳摘要 + 縮圖路徑
  └─ 是文字貼文：
        OpenCLI browser open URL
        OpenCLI browser eval "document.body.innerText"
        Gemma 4 26B MoE 摘要文字內容
        OpenCLI browser screenshot → 截圖
        回傳摘要 + 截圖路徑
```

### 一般網頁（`webpage.py`）
```
嘗試 NotebookLM：
  notebooklm source add URL
  ├─ 成功：notebooklm ask "摘要..." → 回傳摘要
  └─ 失敗（SOURCE_ID 拿不到）：
        OpenCLI browser open URL
        OpenCLI browser eval "document.body.innerText"
        Gemma 4 26B MoE 摘要
        OpenCLI browser screenshot → 截圖
        回傳摘要 + 截圖路徑
```

### 直接影片（`video.py`）
```
yt-dlp 下載影片
ffmpeg 抽全部影格（fps=1）
Gemma 4 26B MoE 分析影格序列
ffmpeg 抽第 1 張影格作為縮圖
回傳摘要 + 縮圖路徑
```

---

## Summarizer 介面（`summarizer.py`）

統一摘要入口，所有 handler 都呼叫這裡：

```python
def summarize_with_gemma(content: str | list[Path], lang: str = "zh-tw") -> str:
    """
    content: 文字字串 或 影格圖片路徑列表
    lang: 輸出語言（預設繁體中文）
    回傳摘要字串
    """

def summarize_with_notebooklm(url: str, lang: str = "zh-tw") -> str:
    """
    直接用 URL 問 NotebookLM
    回傳摘要字串
    """
```

rate limit 自動 retry（最多 3 次，每次等 60 秒）。

---

## Obsidian 筆記格式（`obsidian.py`）

存入路徑：`/Users/herb/Documents/Obsidian/隨手筆記/YYYY-MM-DD_<slug>.md`

```markdown
---
title: <從摘要第一句自動產生>
source: <原始 URL>
type: <youtube | ig-video | ig-post | webpage | video>
date: <YYYY-MM-DD>
tags:
  - 隨手筆記
processed_by: <gemma-4-26b-a4b-it | notebooklm>
---

# <title>

![[<縮圖或截圖檔名>]]

## 摘要
<3-5 句話>

## 關鍵內容
> <原文重要段落或畫面文字>
```

圖片存到：`/Users/herb/Documents/Obsidian/隨手筆記/attachments/`

---

## 錯誤處理

| 情境 | 處理方式 |
|------|---------|
| NotebookLM 無法讀取 URL | 自動切換 OpenCLI + Gemma |
| yt-dlp 下載失敗（需登入）| 提示使用者：`請確認 Chrome 已登入該帳號` |
| Gemma rate limit（429）| 等 60 秒自動 retry，最多 3 次 |
| OpenCLI browser 無回應 | 提示使用者開啟 OpenCLI daemon |
| 全部失敗 | 存「待處理」筆記，記錄 URL + 錯誤原因 |

---

## CLI 介面

```bash
# 基本用法
quicknote https://www.youtube.com/watch?v=xxx

# 指定語言
quicknote https://... --lang en

# 指定模型
quicknote https://... --model gemma-4-31b-it

# 查看版本
quicknote --version
```

---

## Claude Code Skill 整合

Skill 檔案：`~/.claude/plugins/quicknote/skill.md`

呼叫方式：在對話中說「幫我整理這個網址 https://...」

Skill 內部執行：`python3 ~/quicknote/quicknote.py <URL>`

---

## 安裝說明（README 用）

```bash
# 1. Clone 專案
git clone https://github.com/dk40913/quicknote

# 2. 安裝 Python 依賴
pip install -r requirements.txt

# 3. 安裝外部工具
brew install yt-dlp ffmpeg
uv tool install opencli
uv tool install notebooklm-py

# 4. 設定 API Key
cp config.example.py config.py
# 編輯 config.py，填入 GOOGLE_API_KEY

# 5. 設定 Obsidian 路徑
# 編輯 config.py，填入 OBSIDIAN_PATH
```

---

## 不在此版本範圍內（YAGNI）

- 多使用者支援
- Web UI
- 排程自動抓取
- 向量搜尋 / RAG
