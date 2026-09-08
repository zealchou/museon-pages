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
