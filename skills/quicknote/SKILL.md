---
name: quicknote
description: 給定 URL，自動擷取內容、生成摘要，存入 Obsidian 隨手筆記資料夾
---

# 隨手筆記 Skill

當使用者說「幫我整理這個網址」、「把這個存到筆記」、或直接貼上 URL 時，使用這個 skill。

## 前置檢查（每次執行前）

1. 確認 [obsidian-skills](https://github.com/kepano/obsidian-skills) 已安裝，包含以下依賴：
   - `obsidian:obsidian-markdown`：格式化為 Obsidian Flavored Markdown
   - `obsidian:obsidian-cli`：寫入 Obsidian vault
   - `obsidian:defuddle`（需 defuddle CLI）：清理網頁 HTML
     → 若 `which defuddle` 無結果則執行 `npm install -g defuddle`
   - 若 obsidian-skills 未安裝，提示使用者參考 [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) 安裝
2. 確認 opencli daemon 在跑：`opencli status` → 若無則執行 `opencli daemon start`
3. 找到 quicknote 安裝位置並設定變數：
   ```bash
   QUICKNOTE_PY=$(find ~ -maxdepth 8 -name quicknote.py -path "*/quicknote/*" 2>/dev/null | head -1)
   VENV_PYTHON=$(dirname $QUICKNOTE_PY)/.venv/bin/python3
   ```
   → 若 `QUICKNOTE_PY` 為空，提示使用者先完成安裝步驟

## 執行步驟

1. 從使用者訊息取出 URL
2. 執行（不設 timeout，由程式碼內部控制）：
   ```bash
   $VENV_PYTHON $QUICKNOTE_PY <URL>
   ```
3. 讀取輸出中 `=== QUICKNOTE ===` 和 `=== END ===` 之間的 JSON
4. 使用 `obsidian:obsidian-markdown` skill 將 JSON 的 `summary` 格式化為 Obsidian Flavored Markdown，包含：
   - frontmatter（title、source、type、date、tags、processed_by）
   - 適當的 callout、section 結構
   - 若有 `attachment` 欄位，加入 `![[filename]]` embed
5. 使用 Write tool 將格式化後的內容寫入：`<OBSIDIAN_PATH>/隨手筆記/YYYY-MM-DD_<title>.md`
6. 執行：`obsidian open path="隨手筆記/YYYY-MM-DD_<title>.md" silent`
7. 回報筆記存入位置

## 可選參數

- `--lang en`：英文摘要
- `--model gemma-4-31b-it`：使用較強的模型
