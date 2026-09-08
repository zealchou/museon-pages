# 這一年 — 莉凱傢俱體驗遊戲

## 部署（兩個指令）

```bash
npx wrangler login     # 開瀏覽器授權，只要做一次
npx wrangler deploy
```

deploy 完會印出網址，例如 `https://likai-thisyear.<你的帳號>.workers.dev`

## 三個畫面

| 網址 | 裝置 |
|---|---|
| `/?v=screen` | 投影機 |
| `/?v=play`   | 五支手機（lobby 有 QR 可以掃） |
| `/?v=host`   | 主持人 |

## 重跑一場

主持台 →「緊急處理」→「整場重置」。
或改 `src/index.js` 的 `ROOM_NAME` 再 deploy，等於開一個全新房間。

## 為什麼用 Durable Object

同一個房間的請求會被序列化執行，五個人同時送出投票不會互相覆蓋。
KV 是最終一致性，會掉票；D1 要多建一個資料庫。SQLite-backed DO 在免費方案內。
