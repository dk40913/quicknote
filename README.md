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

## 安裝

### 1. Clone 專案
```bash
git clone https://github.com/dk40913/quicknote
cd quicknote
```

### 2. 安裝 Python 依賴
```bash
pip install -r requirements.txt
```

### 3. 安裝外部工具
```bash
brew install yt-dlp ffmpeg
uv tool install opencli
uv tool install notebooklm-py
```

### 4. 設定環境變數
```bash
cp .env.example .env
# 編輯 .env，填入 GOOGLE_API_KEY 和 OBSIDIAN_PATH
```

## 使用方法

```bash
# 基本用法
python3 quicknote.py https://...

# 英文摘要
python3 quicknote.py https://... --lang en

# 指定模型
python3 quicknote.py https://... --model gemma-4-31b-it
```

## Claude Code Skill 安裝

```bash
mkdir -p ~/.claude/plugins/quicknote
cp skill.md ~/.claude/plugins/quicknote/
```

安裝後，編輯 `~/.claude/plugins/quicknote/skill.md`，把路徑改成你的專案位置：

```
python3 /你的路徑/quicknote/quicknote.py <URL>
```

然後在 Claude Code 對話中說：「幫我整理這個網址 https://...」
