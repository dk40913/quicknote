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

複製以下訊息，貼給你的 AI agent（Claude Code、Codex CLI 等）：

---

請幫我安裝 quicknote plugin：https://github.com/dk40913/quicknote

步驟：
1. claude plugin marketplace add dk40913/quicknote
2. claude plugin install quicknote@dk40913-quicknote
3. 進入 ~/.claude/plugins/marketplaces/quicknote/ 建立 Python venv 並安裝依賴
4. 複製 .env.example 為 .env，詢問我的 GOOGLE_API_KEY 和 OBSIDIAN_PATH 後填入

---

AI 會在過程中詢問你的 Google API Key 和 Obsidian vault 路徑。

### 依賴工具

以下工具由 AI 安裝時自動處理，無需手動安裝：

| 工具 | 用途 |
|------|------|
| [obsidian-skills](https://github.com/kepano/obsidian-skills) | 筆記格式化與寫入（含 defuddle） |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) + [ffmpeg](https://ffmpeg.org/) | 影片下載與抽影格 |
| [opencli](https://github.com/opencli/opencli) | 瀏覽器控制（Instagram / Facebook） |
| [notebooklm-py](https://github.com/lspahija/notebooklm-py) | YouTube / 網頁分析 |
| Python 3.11+ | 執行環境 |

唯一需要手動準備的是 **Google API Key**：[Google AI Studio](https://aistudio.google.com) 免費申請。

### 手動安裝

如果你偏好自己動手：

**1. 安裝外部工具**
```bash
brew install yt-dlp ffmpeg
brew install uv
uv tool install opencli
uv tool install notebooklm-py
```

安裝 obsidian-skills（參考 [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)）：
```
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills
```

**2. 安裝 plugin（在 Claude Code 對話中執行）**
```
/plugin marketplace add dk40913/quicknote
/plugin install quicknote@dk40913-quicknote
```

**3. 建立 Python 虛擬環境**

plugin 安裝後，進入系統自動 clone 的目錄：
```bash
cd ~/.claude/plugins/marketplaces/quicknote
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**4. 設定環境變數**
```bash
cp .env.example .env
# 填入：
# GOOGLE_API_KEY=你的 API Key
# OBSIDIAN_PATH=/你的/Obsidian/vault路徑
```

## 使用

安裝完成後，直接對你的 AI agent 說：

```
幫我整理這個網址 https://...
```

AI 會自動抓取、摘要，並以 Obsidian Flavored Markdown 存入你的 Obsidian 筆記庫。

### 可選參數

| 參數 | 說明 | 範例說法 |
|------|------|---------|
| `--lang en` | 英文摘要 | 幫我整理這個網址 https://...（英文） |
| `--model gemma-4-31b-it` | 使用較強的模型 | 幫我整理這個網址 https://...（用較強的模型） |

## 進階說明

### Plugin 安裝原理

執行 `claude plugin install` 時，Claude Code 會自動把 repo clone 到：

```
~/.claude/plugins/marketplaces/quicknote/
```

這是 plugin 系統實際執行 skill 時讀取程式碼的地方。因此 Python venv 也必須建在這個目錄下，skill 才能正確找到執行環境。

你自己的開發 repo（如果有的話）和這個目錄是獨立的，兩者都是同一個 GitHub repo 的 clone。

### 更新原理

執行 `claude plugin update` 時，plugin 系統會從 GitHub pull 最新版本到 `marketplaces/` 目錄，並更新 cache。版本號由 `plugin.json` 的 `version` 欄位決定。

## 更新

當新版本發布後，在 Claude Code 對話中執行：

```
/plugin update quicknote@quicknote
```

或使用終端機：

```bash
claude plugin update quicknote@quicknote
```

更新後需要重啟 Claude Code 讓新版本生效。

## 版本紀錄

### v0.3.1
- 前置檢查加入 `.venv` 初始化步驟，若不存在則自動建立並安裝依賴，避免 exit code 127

### v0.3.0
- 修正 SKILL.md 錯誤指令（opencli status → opencli doctor）
- SKILL.md 加入 yt-dlp / ffmpeg / notebooklm-py 前置檢查
- 修正 URL 含特殊字元時的 zsh 引號問題
- 改善 README：依賴工具說明、可選參數、安裝流程

### v0.2.0
- 修正 scroll 偵測（regex 精確化 + fallback 固定滾 3 次）
- 修正多個 critical / important 穩定性問題
- 修正兩個 suggestion 問題

### v0.1.0
- 初始版本，支援 YouTube、Meta、一般網頁、直接影片 URL
- Claude Code plugin 結構，支援 `/plugin install` 安裝
