---
name: blog-deep-dive-publisher
description: >
  研究一個技術主題，用「底層先行」的教學風格寫成中英雙語深度文章，並發佈到 Tsai
  Cheng-Hung 部落格（FastAPI + Supabase/pgvector 後端）的 /blog ARTICLES 分頁。當使用者說
  「幫我在部落格寫一篇 X」「研究 X 並發成文章」「介紹 X 的底層邏輯放到 blog」「更新一篇
  技術文章到資料庫」時使用。負責「研究 → 用 deep-mechanism-tutor 風格寫雙語文 → 產生
  payload → 發佈到部落格資料庫」整條流程；教學風格細節交給 deep-mechanism-tutor skill。
---

# Blog Deep-Dive Publisher（Claude Code 版）

把一個技術主題，變成一篇可以放上 tsai-cheng-hung 部落格的中英雙語深度文章，並發佈進資料庫。
本版本針對 **Claude Code / 本機環境**：可直接對外連線，發佈只要跑一支腳本，不需瀏覽器。

## 什麼時候用
- 使用者給一個技術主題（embedding、RAG、tokenizer、向量庫……），要求「研究並寫成部落格文章」。
- 文章放在 `/blog` 的 **ARTICLES** 分頁（不是 AI DAILY 每日新聞）。
- 要求底層原理、要有引用、要有視覺化。

教學「怎麼寫」的規範在同捆的 `deep-mechanism-tutor` skill；本 skill 規範「研究流程 + 部落格格式 + 發佈」。兩個一起用。

## 專案背景
- 後端 FastAPI + SQLAlchemy，資料庫 Supabase（PostgreSQL + pgvector）；文章存 `posts` 表，依 slug upsert。
- 前端 Next.js（Vercel），中英雙語、Markdown 呈現、ISR 快取。
- 發佈設定與腳本（同捆）：`config.json`（api_base / admin_token / frontend_base / revalidate_secret）、`publish_post.py`。

## 流程

### 1. 先探索、再問澄清問題
用 GET 看線上現有文章風格：`GET {api_base}/posts`（清單）、`GET {api_base}/posts/<slug>`（單篇 body 慣例）。
接著（除非使用者已講明）用 3 個問題確認：語言（預設中英雙語）、視覺化（預設終端風 ASCII 圖＋表格，最穩、合站上 TSAI.SYS 美學）、發佈狀態（**預設直接上線 published:true**，使用者已表明「寫完就直接上傳」；只有明講要先審才存 false）。

### 2. 研究 + 核對引用（研究先行）
用 WebSearch / WebFetch / MCP 蒐集一手來源（arXiv、官方文件、論文 PDF）。底層原理可直接深講，但**版本相關事實與 arXiv 編號一定要查證**，每個引用連結都 fetch 過確認可達、標題正確。整理成 `[n]` 編號的參考清單。

### 3. 寫雙語 body（套 deep-mechanism-tutor）
先讀 `deep-mechanism-tutor` skill，照「底層先行＋機制／訓練目標／產物三層框架＋每個名詞不留黑箱＋對照組＋收束邏輯鏈」寫。文章慣例（對齊站上 ARTICLES）：
- 用 `## 小標`；正文以能講清因果的散文為主，條列只在真正並列時用。
- 視覺化放在 ```code fence``` 裡（ASCII 圖、矩陣圖、對照表），保證 render；**不要用 GFM 表格**（前端不一定開 remark-gfm，一律改 code-fence ASCII 表）。
- 內文用 `[n]` 引用，文末 `## 參考來源` / `## References` 列 `[n] 作者 (年). 標題. — URL`。
- 舉例貼近使用者領域（製造業 MES、料號語義、Oracle、pgvector RAG）。
- 分別寫 `body_zh_<topic>.md` 與 `body_en_<topic>.md`。

⚠️ 若你用的檔案寫入工具有長度上限、長文可能被截斷：寫完務必**驗證檔尾完整**（grep 最後一個參考編號），必要時分段補寫。用 shell heredoc（`cat > file <<'EOF' … EOF`）寫長檔最穩。

### 4. 產生 payload JSON
用 Python `json.dumps(..., ensure_ascii=False)` 從兩個 md 檔組出 payload（避免手動跳脫錯誤），欄位：
```
slug             kebab-case，唯一；不要用 "ai-daily-*"（那是每日新聞分頁）
title_zh/title_en
excerpt_zh/excerpt_en   一段摘要（顯示在清單卡片）
body_zh/body_en         Markdown 全文
cover_image      通常 null
tags             list，首字大寫如 ["Embeddings","RAG","Deep Dive"]（AI DAILY 才用 ai-daily/news/llm）
reading_minutes  int
published        bool（預設 true）
```
存成 `payload_<topic>.json`。驗證：JSON 合法、``` 成對、`[n]` 引用與參考清單齊全、`published` 正確。

### 5. 發佈（Claude Code 本機，直接跑）
Claude Code 跑在本機、可直接對外連線，所以**直接跑腳本即可**（不需瀏覽器）：
```
python publish_post.py payload_<topic>.json
```
成功印 `OK: post '<slug>' upserted` 與 `OK: frontend cache revalidated`。
腳本會 POST `{api_base}/posts`（Bearer admin_token，依 slug upsert）→ POST `{frontend_base}/api/revalidate?secret=...` 刷新前端 ISR。

或不用腳本，直接 curl：
```
curl -X POST "$API_BASE/posts" -H "Content-Type: application/json" \
     -H "Authorization: Bearer $ADMIN_TOKEN" --data @payload_<topic>.json
curl -X POST "$FRONTEND_BASE/api/revalidate?secret=$REVALIDATE_SECRET"
```
（Render 免費方案首次請求會冷啟動約 30~50 秒，屬正常。）

草稿要上線時把 `published` 改 true 重跑同一指令即可（同 slug upsert）。

## 驗證清單（收尾必做）
- [ ] 每個引用 URL 都 fetch 過、可達、標題對得上。
- [ ] 三層框架、公式／機制敘述正確（可請 subagent 覆核）。
- [ ] body 檔尾未被截斷（最後一個參考編號在）。
- [ ] payload JSON 合法、``` 成對、`published` 如使用者所選。
- [ ] 發佈後 `GET {api_base}/posts/<slug>` 回 200 且 body 長度/tags/published 正確；revalidate 回 `{"revalidated":true}`；到 `{frontend_base}/blog` 確認顯示。

## 參考檔案（同捆）
- `../../publish_post.py`、`../../config.json` — 發佈腳本與設定（放在 kit 根目錄）。
- `payload_template.json` — payload 欄位範本。
- `../deep-mechanism-tutor/SKILL.md` — 教學風格 skill，寫文章前先讀。

## 備註：沙箱環境的替代發佈法
若日後在**網路受限的沙箱**（例如某些代管環境）跑不動直接連線，可改用瀏覽器工具在本機頁面 JS 環境 fetch：先開 API 同源頁（避 CORS），把 payload 用 gzip+base64 分段送進頁面、以 SHA-256 校驗完整性後解碼 POST，再到前端同源打 revalidate。Claude Code 本機一般不需要這套。
