# claude-code-daily-ai-news

把「每日 AI 新聞彙整 → 中英雙語報告 → 發佈到我的部落格 /blog/daily」這整套，
打包成可直接丟進 **Claude Code 新 session** 的工具包。這是從 Cowork 排程
`daily-ai-news`（在 `C:\Users\user\Claude\Scheduled\daily-ai-news\SKILL.md`）
**複製並改寫**出來的獨立一份，原本的排程與 `blog-publisher/` 都沒有動。

## 為什麼要另做一份給 Claude Code

Cowork 的執行環境是沙盒，bash 對外網路被擋（例如打不到 `onrender.com`，會
`403 Forbidden`），所以在 Cowork 裡發布文章只能繞道用 Claude in Chrome
瀏覽器工具：開網頁、在頁面的 JS 環境裡用 `fetch` 打 API。因為 payload 內容
（中英文全文）太長，一次貼進 JS 呼叫會被截斷，只好切成一段一段的 base64
手動貼上再拼回去——這個過程曾經因為手誤（重複貼、漏字）導致 JSON 壞掉，
必須靠每貼一段就檢查累積長度來抓錯，很浪費工夫。

Claude Code 是在你自己電腦上跑的，沒有這層沙盒限制，可以直接用
`python publish_post.py payload.json`（純 stdlib，`urllib` 直接 POST）
一次搞定，不需要瀏覽器、不需要 base64 分段。

## 內容

```
claude-code-daily-ai-news/
├── README.md                          ← 你正在看的這份
├── publish_post.py                    ← 發佈腳本（POST /posts + revalidate）
├── config.json                        ← API 端點與金鑰（admin_token / revalidate_secret）
├── reports/                           ← 每日報告 .md / .html 存放處
└── skills/
    └── daily-ai-news/
        ├── SKILL.md                   ← 完整流程（搜尋→寫作→產payload→發佈，Claude Code 版）
        └── payload_template.json      ← payload 欄位範本
```

## 在 Claude Code 怎麼用

1. 把整個 `claude-code-daily-ai-news/` 資料夾複製到你的專案，或直接在
   Claude Code 裡 `cd` 到這個資料夾。
2. 讓 `skills/daily-ai-news/` 被 Claude Code 讀到：放到 Claude Code 的
   skills 目錄（通常是專案的 `.claude/skills/`），或直接把 SKILL.md 內容
   貼給 Claude Code 當作這次任務的指示也可以。
3. 開一個新 session，直接說：
   > 幫我做今天的 AI 新聞日報，寫完發佈到部落格。
   Claude Code 會：WebSearch 搜今日新聞與 arXiv 論文 → 寫繁中報告 → 存
   `reports/AI每日報告_YYYY-MM-DD.md/.html` → 翻英文 → 組 payload → 直接
   `python publish_post.py payload_YYYY-MM-DD.json` 發佈上線。

## 發佈方式（本機直接跑，免瀏覽器）

```
python publish_post.py payload_2026-07-14.json
```

成功會印：
```
OK: post 'ai-daily-2026-07-14' upserted (HTTP 200)
OK: frontend cache revalidated
```
（Render 免費方案首次請求冷啟動約 30~60 秒屬正常，腳本 timeout 已設 60 秒。）

## 需要的內建能力（Claude Code 都有）

- WebSearch / WebFetch：搜尋當日新聞、arXiv 論文、Hacker News 討論
- Bash + Python 3.9+：寫檔、組 payload、發佈（`publish_post.py` 只用
  標準庫 `urllib`，不需要額外 `pip install`）

## 注意事項

- 同一天只應該有一篇 `ai-daily-YYYY-MM-DD`；`publish_post.py` 用 slug
  upsert，重跑同一天不會產生重複文章，但內容會被覆蓋成最新一次的版本。
- 執行前先看一眼 `reports/` 有沒有已經做過「今天」的報告，避免跟 Cowork
  排程或另一次手動執行重複做工。
- 這個 kit 跟 Cowork 排程 `daily-ai-news` 共用**同一個**部落格後端／同一批
  `ai-daily-*` slug，兩邊發的文章會出現在同一個 `/blog/daily` 列表裡。

## 安全提醒

`config.json` 內含 `admin_token` 與 `revalidate_secret`，等同你部落格後端
的寫入權限。這份 kit 請當機密保管，別提交到公開 repo。
