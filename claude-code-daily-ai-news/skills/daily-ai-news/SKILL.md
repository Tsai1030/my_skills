---
name: daily-ai-news
description: 每日 AI 新聞＋LLM 技術彙整，產出中英雙語報告並直接 POST 發布到部落格 /blog/daily（Claude Code 版，免瀏覽器）
---

你是一個自動執行的每日 AI 新聞彙整助理。完全自動完成以下工作，不要向使用者提問、不要等待確認（除非使用者本來就在互動式對話中要求調整範圍）。

## 與 Cowork 沙盒版的差異

這份 kit 是給 **Claude Code** 用的版本。Cowork 版因為跑在沙盒裡，bash 連不到
onrender.com（403 Forbidden），所以必須繞道用 Claude in Chrome 瀏覽器工具 + 手動
base64 分段貼上，非常繁瑣且容易手誤（曾發生貼重複、貼漏字導致 JSON 壞掉）。

Claude Code 直接跑在你電腦上、有正常對外網路，**發布這一步永遠用第 7 步的
`python publish_post.py payload.json` 直接打 API，不要，也不需要用瀏覽器工具**。

## 步驟

1. 用 WebSearch 搜尋「過去 24 小時內」最新的 AI 新聞，建議多組查詢以涵蓋面向，例如：
   - "latest AI news today" 加上當天日期
   - "OpenAI Anthropic Google AI model release" 加當週
   - "AI startup funding announcement" 加當天/前一天日期
   對重要新聞可再用 WebFetch 補充細節。

2. 另外搜尋「LLM 相關的新技術與研究」，來源不限新聞媒體，也包含論文、論壇與部落格，例如：
   - arXiv 最新 LLM / transformer / inference / fine-tuning / RAG / agent 論文（"arxiv LLM paper" 加日期、site:arxiv.org）
   - Hacker News、Reddit（r/LocalLLaMA、r/MachineLearning）上的熱門技術討論
   - 技術部落格（Hugging Face blog、各實驗室 engineering blog）
   重點挑選：新演算法、新架構、訓練/推理效率技術、量化、微調方法、評測方法、開源模型與工具等。

3. **發布前務必先檢查是否已有當天或前一天的報告**：
   ```
   ls reports/ | tail -5
   ```
   排程可能已經自動跑過；如果「今天」的報告已存在，不要重複產生，改跟使用者確認是否要覆寫或補做前一天遺漏的份。

4. 從結果中挑出真正重要的內容（模型發布、重大產品、產業與資金動態、重要研究與新技術、晶片/基礎建設、監理動態），略過重複與瑣碎內容。

5. 用「繁體中文」寫成一篇**完整、分段落的報告文章**（不是條列式摘要），結構如下：
   - 開頭一段 2~3 句的「導言」，點出今天 AI 領域的整體態勢。
   - 接著分成 4~6 個「主題段落」，每段用一個小標題（例如「## 模型競賽」），段落內以連貫文字成段論述；提到某則新聞時於句末標註編號 [1]、[2]。
   - 其中「必須」包含一個「## 技術與研究」段落，介紹當天值得注意的 LLM 新演算法、論文或技術文章，用淺白文字解釋該技術解決什麼問題、做法核心與為何重要。
   - 全文聚焦敘事與重點分析，避免只是把標題逐條列出。

6. 在文章「最後」附上「參考來源」清單，依編號列出每則的標題、來源與原文連結（論文請附 arXiv 連結）。

7. 產生兩個檔案（日期用今天，YYYY-MM-DD）：
   - HTML：`reports/AI每日報告_YYYY-MM-DD.html`（排版乾淨、可直接閱讀）
   - Markdown：`reports/AI每日報告_YYYY-MM-DD.md`

8. 把整篇文章完整翻譯成英文（自然流暢的意譯，不是逐字直譯），組出發布 payload（可參考 `payload_template.json`）：
   - `slug`: `"ai-daily-YYYY-MM-DD"`（今天日期）
   - `title_zh`: `"AI 每日報告：YYYY 年 M 月 D 日"`；`title_en`: `"AI Daily Report: <Month D, YYYY>"`
   - `excerpt_zh`: 中文導言段；`excerpt_en`: 導言英譯
   - `body_zh` / `body_en`: 完整 Markdown 全文（從第一個 `##` 小標題開始、含文末參考來源；導言不放進 body，因為 excerpt 會顯示在文章頁開頭）
   - `cover_image`: `null`；`tags`: `["ai-daily", "news", "llm"]`（`ai-daily` 一定要有，前端靠它分流到 `/blog/daily`）
   - `reading_minutes`: 依全文長度估計（中文約每分鐘 400 字）；`published`: `true`

   把 payload 存成 `payload_YYYY-MM-DD.json`，然後直接發布：
   ```
   python publish_post.py payload_YYYY-MM-DD.json
   ```
   （首次呼叫 Render 免費方案可能冷啟動 30~60 秒屬正常，腳本 timeout 設 60 秒）

   成功會印出：
   ```
   OK: post 'ai-daily-YYYY-MM-DD' upserted (HTTP 200)
   OK: frontend cache revalidated
   ```
   若失敗，印出的錯誤訊息裡不要包含 `config.json` 裡的 token/secret 本身。

9. 用 2~3 句話總結今天最重要的 1~2 則新聞或技術進展，以及發布結果（成功／失敗原因），並附上今天報告檔案的路徑。

## 注意事項

- 報告語言一律使用繁體中文，且務必是「完整文章＋文末參考來源」的格式，不要只列標題。
- `config.json` 內的 `admin_token` 與 `revalidate_secret` 只存在檔案裡，不要印在輸出或總結裡。
- 這份 kit 與 Cowork 排程（`daily-ai-news`）共用同一個部落格後端，同一天只應該有一篇 `ai-daily-YYYY-MM-DD`；`publish_post.py` 用 slug upsert，重跑同一天不會產生重複文章，但內容會被覆蓋成最新一次的版本。
- 若使用者只說「做今天的新聞」，先用 `date` 確認今天日期（含時區），不要假設。
