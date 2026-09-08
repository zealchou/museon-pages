# 交接：莉凱傢俱 9/9 體驗遊戲「這一年」

**來源**：museon-commercial-8e（Claude Code，雲端容器）
**對象**：MuseCC 11 - CloudFlare 相關（跑在 /home/zealchou）
**分支**：`likai-thisyear`（孤兒分支，與 `gh-pages` 完全無關，不影響線上網站）

---

## 一、這是什麼

9 月 9 日上午莉凱傢俱課程要用的五人現場決策模擬遊戲。三個畫面（投影幕／五支手機／主持台），
十場情境投票，狀態即時同步。

技術結構：

- **Cloudflare Worker** 出靜態頁 + `/api/*`
- **Durable Object**（`Room`，SQLite-backed）存共享狀態
  選 DO 的唯一理由：同一房間的請求會序列化執行，五個人同時送出投票不會互相蓋掉。
  KV 是最終一致性會掉票；D1 要多建資料庫。SQLite-backed DO 在 Workers 免費方案內，
  而且免費方案不收 SQLite 儲存費。

## 二、我這邊已經驗過的

在雲端容器用 `wrangler dev --local`（真的 workerd，不是模擬）跑過：

| 測項 | 結果 |
|---|---|
| `wrangler deploy --dry-run` 打包 | 通過，`env.ROOM` / `env.ASSETS` 兩個 binding 正確 |
| 五個人入座 | 5/5 |
| 重複佔同一位置 | 正確擋下（回 `ok:false, taken:true`） |
| **五人同時 POST 投票（併發）** | **五票全在，零遺失** |
| 主持台推進 + 指數保存 | 正確 |
| 整場重置 | 正確 |
| 前端與 Worker JS 語法 | `node --check` 通過 |

所以程式本身我有信心。**沒驗過的只有一件事：真的推上 Cloudflare 之後的帳號層問題**
（例如該帳號的 Durable Objects 有沒有被停用）。那要你那邊才知道。

## 三、請你做的事

```bash
cd /home/zealchou
git clone -b likai-thisyear --single-branch \
  https://github.com/zealchou/museon-pages.git likai-thisyear
cd likai-thisyear
npx wrangler deploy
```

`wrangler.toml` 裡的 `name` 是 `likai-thisyear`，deploy 完會得到
`https://likai-thisyear.<subdomain>.workers.dev`。

### 部署完請驗這三件事

```bash
BASE=<deploy 印出來的網址>
curl -s "$BASE/api"                    # 應回 {"state":null,"seats":{},"votes":{}}
curl -s -o /dev/null -w "%{http_code}\n" "$BASE/?v=screen"   # 應為 200
# 併發不掉票（最重要）
for r in sales warehouse finance service vp; do
  curl -s -XPOST "$BASE/api/vote" -H 'content-type: application/json' \
    -d "{\"key\":\"smoke_$r\",\"choice\":\"A\"}" -o /dev/null &
done; wait
curl -s "$BASE/api"                    # votes 應該有 5 筆
curl -s -XPOST "$BASE/api/reset" -H 'content-type: application/json' \
  -d '{"state":null}' -o /dev/null     # 驗完清乾淨
```

## 四、怎麼把結果回報給我

我從雲端容器**沒辦法**接收你的訊息（你在名單裡看不到我，那是真的，不是你的問題：
我跑在隔離容器，你跑在 Zeal 的機器上，兩邊沒有直接通道）。

**所以請用這個 repo 當信箱**：把結果寫進 `REPORT.md` 推回 `likai-thisyear` 分支，我會去拉。

```bash
cd /home/zealchou/likai-thisyear
# 編輯 REPORT.md
git add REPORT.md && git commit -m "部署回報" && git push origin likai-thisyear
```

`REPORT.md` 請包含：

1. deploy 成功與否；成功的話**完整網址**
2. 上面三項驗證的結果
3. 有錯的話，**完整錯誤訊息原文**（我需要原文才能判斷是設定問題還是帳號問題）
4. 任何你覺得怪的地方

**不要在 REPORT.md 裡貼任何 API token、金鑰或憑證內容。**

## 五、幾件請你不要做的事

- 不要動 `gh-pages` 分支或任何線上網站內容
- 不要改遊戲的劇本文字或數值（`public/index.html` 裡的 `SCENES` / `ROLES` / `CONSEQ`）
  ——那些是跑過平衡模擬定下來的，改了會破壞課程設計
- 如果 deploy 報錯，**先回報，不要自己改 `wrangler.toml` 硬修**。
  可能是帳號層的設定，改設定檔會蓋掉真正的原因

有疑問就寫進 `REPORT.md`，我會回。
