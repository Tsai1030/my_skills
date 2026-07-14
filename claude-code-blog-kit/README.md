# claude-code-blog-kit

把「研究技術主題 → 用底層教學風格寫中英雙語深文 → 發佈到我的部落格資料庫」這整套，
打包成可直接丟進 **Claude Code 新 session** 的工具包。這是**複製**出來的獨立一份，
原本的檔案（blog-publisher/）沒有動。

## 內容
```
claude-code-blog-kit/
├── README.md                                   ← 你正在看的這份
├── publish_post.py                             ← 發佈腳本（POST /posts + revalidate）
├── config.json                                 ← API 端點與金鑰（admin_token / revalidate_secret）
└── skills/
    ├── deep-mechanism-tutor/SKILL.md           ← 「怎麼寫」：底層先行教學風格
    └── blog-deep-dive-publisher/
        ├── SKILL.md                            ← 「整條流程」：研究→寫→產payload→發佈（Claude Code 版）
        └── payload_template.json               ← payload 欄位範本
```

## 在 Claude Code 怎麼用
1. 把整個 `claude-code-blog-kit/` 複製到你的專案。
2. 讓兩支 skill 被 Claude Code 讀到：把 `skills/deep-mechanism-tutor/` 與
   `skills/blog-deep-dive-publisher/` 放到 Claude Code 的 skills 目錄（通常是專案的
   `.claude/skills/`）。
3. 開一個新 session，直接說：
   > 幫我在部落格寫一篇介紹 <主題> 的文章，用底層邏輯講清楚，發佈上線。
   Claude 會觸發 `blog-deep-dive-publisher`（並讀 `deep-mechanism-tutor` 定風格），
   研究→寫雙語文→產 payload→發佈。

## 發佈（本機直接跑，免瀏覽器）
Claude Code 在你電腦上跑、可直接連外網，所以：
```
python publish_post.py payload_<主題>.json
```
成功會印 `OK: post '<slug>' upserted` 與 `OK: frontend cache revalidated`。
（Render 免費方案首次請求冷啟動約 30~50 秒屬正常。）

## 需要的內建能力（Claude Code 都有）
- WebSearch / WebFetch：研究與核對引用
- Bash + Python 3.9+：寫檔、組 payload、發佈
- （選用）TodoWrite：進度追蹤

## 慣例速記
- 文章放 ARTICLES：tags 首字大寫（如 `["RAG","Retrieval","Deep Dive"]`），slug 不要用 `ai-daily-*`。
- 視覺化用 ```code fence``` 內的 ASCII 圖／表（不要 GFM 表格）。
- 內文 `[n]` 引用 + 文末參考來源，每個連結都查證過。
- 預設 `published:true` 直接上線（除非指定先存草稿）。

## 安全提醒
`config.json` 內含 admin_token 與 revalidate_secret，等同你部落格後端的寫入權限。
這份 kit 請當機密保管，別提交到公開 repo。
