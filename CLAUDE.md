# 這一年 — 給接手 Claude 的工作規則

莉凱傢俱 2026/9/9 課程用的五人現場決策模擬遊戲。這個分支（`likai-thisyear`）是
`museon-pages` 的**孤兒分支**，跟 `gh-pages` 沒有共同祖先。

---

## 1. 絕對不要做的事

**不要動 `gh-pages` 分支。** 那是線上網站。這個分支跟它完全隔離，切換分支時要確認。

**不要在沒跑模擬的情況下改遊戲數值。** `public/index.html` 裡的 `SCENES` 每個選項都有
`e:{rev,trust}`，那 30 個數字是跑過 59049 種打法反推出來的。改完必須跑：

```bash
python3 tools/balance_sim.py --from-html public/index.html
```

三個數字要維持在 **盲投 ~5% / 隨機路徑 ~23% / 知情 ~99%**。跑掉了整堂課的核心論證就是假的
（見 `docs/03-數值與平衡.md`）。模擬器失敗會回非零退出碼。

**不要「順手優化」劇本文字。** 十場情境是照莉凱真實痛點寫的（丈量差三公分、義大利櫃期、
出貨單沒有電梯尺寸、季底展示品、安裝刮傷實木地板）。第 4 場跟第 7 場之間有伏筆回收關係，
改了會斷。動之前先讀 `docs/02-遊戲設計.md`。

**不要在文件或 commit 裡貼任何 API token、金鑰、憑證。**

---

## 2. 驗證的規矩

**curl 不算驗過。** 這個專案已經因為這件事出過一次事：`public/index.html` 少了
`<meta charset="utf-8">`，curl 測 HTTP 200 全過，但真實瀏覽器會編碼誤判 → inline script
的中文字串損壞 → SyntaxError → 整支腳本死掉 → 黑畫面。

**改完前端一定要用真實瀏覽器開一次**，至少確認：

- 三個畫面都渲染得出來（`?v=screen` / `?v=play` / `?v=host`）
- 中文沒有變亂碼
- Console 沒有 error

後端／API 才適合用 curl 驗，其中**併發不掉票**是最關鍵的一項：

```bash
BASE=https://likai-thisyear.zeal-chou.workers.dev
for r in a b c d e; do
  curl -s -XPOST "$BASE/api/vote" -H 'content-type: application/json' \
    -d "{\"key\":\"smoke_$r\",\"choice\":\"A\"}" -o /dev/null &
done; wait
curl -s "$BASE/api"    # votes 應該有 5 筆
curl -s -XPOST "$BASE/api/reset" -H 'content-type: application/json' -d '{"state":null}'
```

**驗完一定要 reset**，否則上課時場上會有殘留的測試票。

---

## 3. 部署

```bash
npx wrangler deploy
```

線上網址：`https://likai-thisyear.zeal-chou.workers.dev`

新部署後 edge 傳播約需 20–30 秒，期間可能出現 404 或 Cloudflare error 1042。**這是正常的**，
不要因此去改設定。上課前提早幾分鐘先開一次頁面熱身。

---

## 4. 架構為什麼長這樣

**Durable Object 而不是 KV**：同一個房間的請求會被序列化執行，五個人同時送出投票不會互相
覆蓋。KV 是最終一致性會掉票，D1 要多建一個資料庫。SQLite-backed DO 在 Workers 免費方案內。

**輪詢而不是 WebSocket**：只有 6 個 client、每 1.2 秒一次，負載微不足道，而且出事時好除錯十倍。
現場出問題時你會感謝這個決定。

**內容全部寫死在前端**：不呼叫任何模型。現場延遲和不可預測性是課程的天敵。

---

## 5. 課程設計已定的決策（不要重新發明）

- **下午走「修復 + 點燃希望」路線**，不是保持張力
- **副總會在場，而且他就是來聽真話的**（老闆不在）。他不是風險，是資源
- 完整設計見 `docs/01-課程設計.md`，主持人現場用 `docs/05-帶課手冊.md`

---

## 6. 檔案地圖

| 路徑 | 是什麼 |
|---|---|
| `public/index.html` | 整個遊戲前端（單檔，含全部劇本與數值） |
| `src/index.js` | Worker 路由：`/api/*` 進 DO，其餘走靜態資產 |
| `src/room.js` | Durable Object，房間狀態 |
| `tools/balance_sim.py` | 平衡模擬器，改數值必跑 |
| `docs/` | 設計文件，見 `docs/README.md` 索引 |
| `HANDOFF.md` `REPORT.md` | 跨 session 交接與部署回報的歷史紀錄 |
