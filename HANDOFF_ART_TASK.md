# 交接：莉凱「這一年」場景背景圖任務（進行中，context 快滿時中斷寫的）

## 現況（2026-09-07）

- 遊戲已上線並驗證過：https://likai-thisyear.zeal-chou.workers.dev
- 已派一支背景 codex 工作單（單一張抽象水墨氛圍背景圖，不含人物），
  work order 存於 `/tmp/claude-1000/-home-zealchou/a3e4d27d-ca34-4024-a9ef-3b403337fe7b/scratchpad/likai_art/work_order.md`，
  執行中 PID 1676463（`codex exec -m gpt-5.6-terra`），log 在
  `/home/zealchou/likai-thisyear/logs_art_gen.log`。**這支工作單已經過期/範圍不符最新需求，
  等它跑完後可以參考但不必採用，見下方「Zeal 最新指示」。**

## Zeal 最新指示（中途補充，優先於上面那支工作單）

「我要十個情境的情境背景圖，是可以有人物的（勾勒）」

即：**不是一張抽象氛圍圖，是十張——對應 `public/index.html` 裡 `SCENES` 陣列的十個情境
（r1 no1-5、r2 no1-5，各有 `ti` 標題與 `st` 情境文字），每張圖對應那個情境的內容，
且可以有人物（用 editorial-ink-watercolor 技能講的「勾勒／人物省略」畫法——不是完整寫實
人物，是省略大半輪廓、只留關鍵姿態線索的水墨畫法，技能裡叫「human situation」或
「narrative scene」模式，不是先前那支工作單用的「abstract transition」無人物模式）。

## 下一步（接手時照做）

1. 讀 `/home/zealchou/likai-thisyear/public/index.html` 的 `SCENES` 陣列（第 201-281 行），
   逐一列出十個情境的 `ti`（標題）與 `st`（情境描述），各自對應一張圖。
2. 讀技能 `~/.claude/skills/editorial-ink-watercolor/SKILL.md`（已讀過一次，內容摘要：
   人物採「錨點/軌跡/消失」結構，35-65% 留白過人物，2-4 個高完成度區域，其餘省略；
   subject mode 依內容選 human situation 或 narrative scene；八項自我評分校準表）。
3. 寫一支新工作單（比照 `work_order.md` 的格式，含完整校準表文字，因 codex 沒裝這個 skill
   plugin，判準要整段複製進工作單），十個情境各給一段對應描述＋畫面用途（16:9，用在投影幕；
   構圖要幫文字留出安全區——版面是左側故事文字、右側指數面板）。
4. 存檔路徑建議：`public/art/scene-01.png` ~ `scene-10.png`（依 SCENES 陣列順序，
   r1no1=scene-01…r2no5=scene-10）。
5. 派 codex terra high 執行，背景派工＋Monitor 等待，不要卡在前台等。
6. 完工後我（或接手的 session）要做：讀 `INTEGRATION_NOTES.md`、把圖接進
   `renderScreen()` 的 `PH.STORY` 分支（`public/index.html` 約第 429-432 行），
   依 `state.idx` 對應當前情境切換背景圖，做成 CSS `background-image` 切換或
   `<img>` 淡入淡出，不改動 `SCENES`／`ROLES`／`CONSEQ` 任何文字或數值。
7. 改完要重新部署（`npx wrangler deploy`）並重跑三項驗證（尤其併發投票），
   確認視覺改動沒有動到遊戲邏輯。課程在 9/9 上午，還有緩衝時間但不要拖到最後一刻。

## 硬性限制（延續整場對話的規矩）

- 絕對不改 `SCENES`／`ROLES`／`CONSEQ` 的文字或數值（museon-commercial-8e 明確交代過）。
- 不碰 R5 staging 的任何 process。
- 生圖走 codex terra high，不是我自己畫；藍圖/審計走 codex sol high（若這批需要獨立審圖）。
