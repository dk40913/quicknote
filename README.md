# QuickNote 隨手筆記

給定任意 URL，自動偵測內容類型、擷取內容、生成摘要，存入 Obsidian `/隨手筆記/` 資料夾。

## 支援的 URL 類型

| 類型 | 處理方式 |
|------|---------|
| YouTube | NotebookLM 直接分析 |
| Instagram Reels | yt-dlp 下載 → ffmpeg 抽影格 → Gemma 4 分析 |
| Instagram 文字貼文 | OpenCLI 抓取 → Gemma 4 摘要 |
| Threads / Facebook | 同 Instagram |
| 一般網頁 | NotebookLM（失敗則 OpenCLI fallback）|
| 直接影片 URL | yt-dlp 下載 → ffmpeg → Gemma 4 |

## 需求

- Python 3.11+（安裝方式見下方）
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/)
- [opencli](https://github.com/opencli/opencli)
- [notebooklm-py](https://github.com/lspahija/notebooklm-py)
- Google API Key（免費，申請於 [Google AI Studio](https://aistudio.google.com)）

## 安裝 Python

**macOS 建議用 pyenv 管理 Python 版本：**

```bash
# 安裝 pyenv
brew install pyenv

# 安裝 Python 3.11
pyenv install 3.11.8

# 在專案目錄設定版本
cd quicknote
pyenv local 3.11.8
```

或直接從 [python.org](https://www.python.org/downloads/) 下載安裝 3.11+。

安裝完成後確認版本：
```bash
python3 --version  # 應顯示 Python 3.11.x
```

## 安裝

### 1. Clone 專案
```bash
git clone https://github.com/dk40913/quicknote
cd quicknote
```

### 2. 建立 Python 虛擬環境並安裝套件
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> 之後每次使用前需要先啟動虛擬環境：`source .venv/bin/activate`

### 3. 安裝外部工具
```bash
brew install yt-dlp ffmpeg
uv tool install opencli
uv tool install notebooklm-py
```

### 4. 設定環境變數
```bash
cp .env.example .env
# 編輯 .env，填入：
# GOOGLE_API_KEY=你的 API Key
# OBSIDIAN_PATH=/你的/Obsidian/vault路徑
```

## 使用方法

```bash
# 啟動虛擬環境（每次使用前）
source .venv/bin/activate

# 基本用法
python3 quicknote.py https://...

# 英文摘要
python3 quicknote.py https://... --lang en

# 指定模型
python3 quicknote.py https://... --model gemma-4-31b-it
```

## Claude Code Skill 安裝

安裝後可以在 Claude Code 對話中直接說「幫我整理這個網址 https://...」來觸發。

```bash
mkdir -p ~/.claude/plugins/quicknote
cp skill.md ~/.claude/plugins/quicknote/
```

編輯 `~/.claude/plugins/quicknote/skill.md`，把路徑改成你的專案實際位置：

```
/你的路徑/quicknote/.venv/bin/python3 /你的路徑/quicknote/quicknote.py <URL>
```

> 注意：路徑要指向虛擬環境裡的 python3（`.venv/bin/python3`），不是系統的 `python3`，這樣才能使用安裝好的套件。
