# QuickNote 隨手筆記

給定任意 URL，自動偵測內容類型、擷取內容、生成摘要，以 Obsidian Flavored Markdown 存入 Obsidian `/隨手筆記/` 資料夾。

## 支援的 URL 類型

| 類型 | 處理方式 |
|------|---------|
| YouTube | NotebookLM 分析 |
| Meta 貼文（Instagram / Facebook / Threads）| OpenCLI 抓取 → defuddle 清理 → Gemma 4 摘要 |
| Meta 影片（Reels / FB 影片）| 同時抓文字 + yt-dlp 下載影片 → ffmpeg 抽影格 → Gemma 4 視覺+文字分析 |
| 一般網頁 | NotebookLM（失敗則 defuddle → Gemma 4 fallback）|
| 直接影片 URL（.mp4 / .mov） | yt-dlp 下載 → ffmpeg → Gemma 4 |

## 安裝

### 讓 AI 幫你安裝（推薦）

把以下訊息貼給你的 AI agent（Claude Code、Codex CLI 等）：

> 請幫我安裝這個 quicknote skill：https://github.com/dk40913/quicknote
> 需要 clone 專案、建立 Python venv、安裝依賴、設定 .env，並安裝為 plugin。

AI 會引導你完成所有步驟，包含詢問你的 API Key 和 Obsidian vault 路徑。

### 前置需求

AI 安裝過程中會協助確認以下工具是否已安裝：

| 工具 | 用途 |
|------|------|
| [obsidian-skills](https://github.com/kepano/obsidian-skills) | 筆記格式化與寫入（含 defuddle） |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) + [ffmpeg](https://ffmpeg.org/) | 影片下載與抽影格 |
| [opencli](https://github.com/opencli/opencli) | 瀏覽器控制（Instagram / Facebook） |
| [notebooklm-py](https://github.com/lspahija/notebooklm-py) | YouTube / 網頁分析 |
| Python 3.11+ | 執行環境 |
| Google API Key | [Google AI Studio](https://aistudio.google.com) 免費申請 |

### 手動安裝

如果你偏好自己動手：

**1. Clone 專案**
```bash
git clone https://github.com/dk40913/quicknote
cd quicknote
```

**2. 建立 Python 虛擬環境**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. 安裝外部工具**
```bash
brew install yt-dlp ffmpeg
brew install uv
uv tool install opencli
uv tool install notebooklm-py
```

安裝 obsidian-skills：請參考 [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)

**4. 設定環境變數**
```bash
cp .env.example .env
# 填入：
# GOOGLE_API_KEY=你的 API Key
# OBSIDIAN_PATH=/你的/Obsidian/vault路徑
```

**5. 安裝 plugin**
```
/plugin marketplace add dk40913/quicknote
/plugin install quicknote@dk40913-quicknote
```

## 使用

安裝完成後，直接對你的 AI agent 說：

```
幫我整理這個網址 https://...
```

AI 會自動抓取、摘要，並以 Obsidian Flavored Markdown 存入你的 Obsidian 筆記庫。
