# 這一年 — 莉凱傢俱體驗遊戲

2026/9/9 莉凱傢俱一日課程的上午段：一個五人同時上線的體驗式決策遊戲。
十場情境、兩輪（第一輪禁語、第二輪可討論）、三個指數（營收／信任／內耗）。

**線上網址**：https://likai-thisyear.zeal-chou.workers.dev
（公開，不用登入，學員手機直接開）

---

## 先看哪一份

**要接手這個專案** → `docs/06-待辦與已知問題.md`
誠實清單：上課前檢查項、還沒決定的三件事、已知限制、施工留下的教訓。

**當天要帶課** → `docs/05-帶課手冊.md`

**要改東西** → 根目錄 `CLAUDE.md`（工作規則），再照下表挑對應文件。

| 你要改 | 先讀 |
|---|---|
| 數值、機率、選項效果 | `docs/03-數值與平衡.md` ← **最不能亂動的地方** |
| 情境文案、角色卡、結局 | `docs/02-遊戲設計.md` |
| 顏色、字型、質感 | `docs/04-視覺語言.md` |
| 下午的課 | `docs/01-課程設計.md` |

完整索引在 `docs/README.md`。

---

## 專案結構

```
public/index.html      整個前端。單檔，三個畫面靠 ?v= 參數切換
src/index.js           Worker 入口：/api/* 進 Durable Object，其餘走靜態資源
src/room.js            Durable Object：房間狀態（state / seats / votes）
tools/balance_sim.py   平衡模擬器。改完數值必跑
wrangler.toml          Cloudflare 設定
docs/                  設計文件（6 份 + 索引）
CLAUDE.md              工作規則
HANDOFF.md / REPORT.md 跨 session 交接的歷史紀錄，留作稽核軌跡
```

## 三個畫面

| 網址 | 裝置 |
|---|---|
| `/?v=screen` | 投影機 |
| `/?v=play`   | 五支手機（lobby 有 QR 可以掃） |
| `/?v=host`   | 主持人 ← **不要把這個給學員** |

---

## 常用指令

```bash
# 本地跑（含 Durable Object 模擬）
npx wrangler dev --local

# 部署
npx wrangler login        # 只要做一次
npx wrangler deploy

# 改完數值一定要跑這個，直接從線上那份 HTML 抽數值
python3 tools/balance_sim.py --from-html public/index.html

# 確認場上是乾淨的
curl -s https://likai-thisyear.zeal-chou.workers.dev/api
# 應該回 {"state":null,"seats":{},"votes":{}}
```

平衡模擬器現況（對著 `public/index.html` 跑出來的）：

```
三層對比：盲投 5.1% / 隨機路徑 23.5% / 知情 99.9%
設計不變式：✅ 通過   退出碼 0
```

這三個數字下午要當證據講出來，**跑掉了就不要上課**。

## 重跑一場

主持台 →「緊急處理」→「整場重置」。
或改 `src/index.js` 的 `ROOM_NAME` 再 deploy，等於開一個全新房間。

## 為什麼用 Durable Object

同一個房間的請求會被序列化執行，五個人同時送出投票不會互相覆蓋。
KV 是最終一致性，會掉票；D1 要多建一個資料庫。SQLite-backed DO 在免費方案內。

## 兩條紅線

1. **不要動 `gh-pages` 分支**——那是 MUSEON 正式網站。這個專案在獨立的 orphan branch `likai-thisyear` 上。
2. **改完前端一定要用真實瀏覽器開一次**。curl 回 200 不等於頁面能看；這個專案為此出過一次黑畫面的事故（`docs/06` 有始末）。
