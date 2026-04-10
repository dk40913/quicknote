---
name: quicknote
description: 給定 URL，自動擷取內容、生成摘要，存入 Obsidian 隨手筆記資料夾
---

# 隨手筆記 Skill

當使用者說「幫我整理這個網址」、「把這個存到筆記」、或直接貼上 URL 時，使用這個 skill。

## 執行步驟

1. 從使用者訊息取出 URL
2. 執行：`python3 ~/Documents/Claude/Projects/quicknote/quicknote.py <URL>`
3. 回報筆記存入位置

## 可選參數

- `--lang en`：英文摘要
- `--model gemma-4-31b-it`：使用較強的模型

## 範例

使用者：「幫我整理 https://www.youtube.com/watch?v=xxx」
執行：`python3 ~/Documents/Claude/Projects/quicknote/quicknote.py https://www.youtube.com/watch?v=xxx`
