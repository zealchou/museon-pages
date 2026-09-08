# 部署回報：莉凱傢俱 9/9「這一年」

回報者：MuseCC 11 - CloudFlare 網站（跑在 /home/zealchou）
時間：2026-09-07（部署當下）

## 1. Deploy 結果

成功。網址：

**https://likai-thisyear.zeal-chou.workers.dev**

## 2. 三項驗證結果

| 測項 | 結果 |
|---|---|
| `GET /api` 初始狀態 | 通過，回 `{"state":null,"seats":{},"votes":{}}` |
| `GET /?v=screen` 回 200 | 通過（見下方備註） |
| 五人併發投票不掉票 | 通過，五筆全部到齊：`smoke_sales`／`smoke_warehouse`／`smoke_finance`／`smoke_service`／`smoke_vp` 皆在，choice 皆為 A |

驗完已呼叫 `/api/reset` 清空測試資料，確認 `votes` 回空物件，正式上課前是乾淨狀態。

**備註（不是缺陷，記錄一下過程）**：`GET /?v=screen` 部署後立刻測第一次回 404、第二次回 Cloudflare
edge 錯誤頁（error code 1042），重試幾次（約 20-30 秒內）後穩定回 200，內容正確（`<title>這一年</title>`）。
判斷是 Workers 新部署後 edge 傳播的正常延遲，不是程式或設定問題——根路徑 `/`（不帶 query string）
從一開始就正常回 200，且 `?v=screen` 的路由邏輯（`src/index.js`）本來就跟 `/` 走同一條 assets 分支，
邏輯上不該有差異。**明天上課前建議提早幾分鐘先開一次頁面**，避免萬一又遇到這種短暫延遲。

## 3. 錯誤原文

無——deploy 與三項驗證全部一次成功，沒有需要回報的錯誤。

## 4. 我覺得怪的地方

沒有。程式碼在部署前已經看過一遍（`src/index.js`、`src/room.js`、`package.json`、`wrangler.toml`），
乾淨，跟 HANDOFF.md 描述的架構一致，沒有可疑的對外連線或安裝腳本。部署時 Cloudflare 回報的兩個
binding（`env.ROOM`、`env.ASSETS`）都正確接上。

## 補充：帳號層確認

wrangler 用的是 Zeal 本人帳號（zeal.chou@gmail.com），Durable Objects 沒有被停用——部署與
併發投票測試都成功就是最直接的證明，沒有另外查帳號設定頁面。

沒有動 `gh-pages` 分支，沒有改劇本文字或數值（`SCENES`／`ROLES`／`CONSEQ` 皆未觸碰）。

## 5. 追加修復：黑畫面（2026-09-08）

Zeal 回報手機與電腦都是黑畫面。用真實瀏覽器（Chrome，之前只用 curl 驗過 HTTP 狀態碼，
沒有真的執行過 JS——這是這次才發現的驗證缺口）打開後，console 出現：

```
SyntaxError: Unexpected identifier '蝚'  (public/index.html:556:17)
```

根因：`public/index.html` 原本**完全沒有 `<meta charset="utf-8">`**，瀏覽器猜編碼猜錯，
把 inline `<script>` 裡的中文字串猜壞，語法直接爛掉、整支 script 停擺，畫面永遠是空的
（`#app` 從未被填入內容）。跟部署本身、跟 Durable Object 邏輯都無關。

修法：在 `<title>` 前加了

```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
```

只加這兩行，`SCENES`／`ROLES`／`CONSEQ` 及其他任何文字/數值一個字未動。

**重新部署並重驗過**：
- 真瀏覽器開 `?v=screen` 與 `?v=play`，畫面正常渲染，console 無錯誤（清空後重新整理再測一次仍乾淨）。
- `GET /api` 初始狀態正常。
- `GET /?v=screen` 回 200。
- 五人併發投票（`smoke_sales`／`smoke_warehouse`／`smoke_finance`／`smoke_service`／`smoke_vp`，
  choice 皆 A）五筆全數到齊、零掉票，測完 `/api/reset` 清空確認乾淨。

現在的 https://likai-thisyear.zeal-chou.workers.dev 應該是正常的了。
