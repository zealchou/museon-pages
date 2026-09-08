#!/usr/bin/env python3
"""
平衡模擬器 — 改動 SCENES 的 e:{rev,trust} 之後必須跑這支。

這個遊戲的教學效果整個押在三個數字上：
  盲投 ~5%    第一輪的處境（禁語，各投各的）
  隨機 ~23%   有討論但沒真的交換資訊
  知情 ~99%   攤開角色卡、挑對場次

如果改了數值讓這三個數字跑掉，課程設計就毀了——
「溝通只能把你帶到 23%，交換資訊才會到 99%」那句話會變成謊話。

用法：
    python3 tools/balance_sim.py
    python3 tools/balance_sim.py --from-html public/index.html   # 直接讀線上版數值
"""
import argparse
import itertools
import json
import random
import re
import sys

# 目標門檻：這一年營收要多 28，信任最多只能少 28
TARGET_REV, TARGET_TRUST = 128, 72
START = 100

# 「該衝的場」——資訊互通後才看得出來這幾場衝的代價低
PUSH_SCENES = {0, 4, 7, 9}      # R1-1 整戶大單、R1-5 展示品、R2-3 建商、R2-5 明年
TRAP_SCENES = {1, 2, 3, 8}      # R1-2 三公分、R1-3 櫃期、R1-4 電梯、R2-4 刮痕

# 現行數值（與 public/index.html 的 SCENES 同步）
# 每一項是 (A, B, C)，每個選項是 (rev, trust)
EFFECTS = [
    ((9, -2), (4, 3), (-2, 5)),    # 1  整戶的那張單   ← 該衝
    ((3, -8), (-1, 6), (2, -2)),   # 2  那三公分       ← 陷阱
    ((3, -8), (-2, 7), (-1, 5)),   # 3  櫃期           ← 陷阱
    ((4, -7), (2, 3), (-3, 7)),    # 4  電梯           ← 陷阱／伏筆
    ((8, -2), (4, 2), (-2, 4)),    # 5  展示品         ← 該衝
    ((5, -4), (2, 5), (-3, 7)),    # 6  卡住的那張單
    ((3, 2), (-1, 7), (4, -5)),    # 7  安裝主管       ← 回收第 4 場
    ((9, -3), (5, 2), (-3, 4)),    # 8  建商           ← 該衝
    ((-2, 3), (-1, 7), (3, -9)),   # 9  那道刮痕       ← 陷阱
    ((8, -2), (4, 3), (-2, 5)),    # 10 明年           ← 該衝
]

# 內耗指數：只看票數分裂程度，跟選了什麼無關。
# 這是他們自己造出來的數字，也是全場唯一只會往上的指標。
FRICTION = {"5": 0, "4-1": 2, "3-2": 4, "3-1-1": 6, "2-2-1": 8}


def friction_of(counts):
    shape = "-".join(str(n) for n in sorted((c for c in counts if c > 0), reverse=True))
    return FRICTION.get(shape, 4)


def parse_html(path):
    """從 public/index.html 抽出實際上線的數值，確保模擬跟線上一致。"""
    src = open(path, encoding="utf-8").read()
    pairs = re.findall(r"e:\{rev:(-?\d+),trust:(-?\d+)\}", src)
    if len(pairs) != 30:
        sys.exit(f"預期 30 組數值，實際抓到 {len(pairs)} 組——SCENES 結構可能被改過")
    nums = [(int(r), int(t)) for r, t in pairs]
    return [tuple(nums[i * 3:i * 3 + 3]) for i in range(10)]


def play(effects, picks):
    rev = trust = START
    for scene, choice in zip(effects, picks):
        rev += scene[choice][0]
        trust += scene[choice][1]
    return rev, trust


def hit(rev, trust):
    return rev >= TARGET_REV and trust >= TARGET_TRUST


def tier_blind(effects, n=40000, seed=5):
    """第一輪：五個人各投各的，完全沒有交換資訊。
    每一場的影響是五票的加權平均，不是加總。"""
    rnd = random.Random(seed)
    wins = 0
    for _ in range(n):
        rev = trust = float(START)
        for scene in effects:
            votes = [rnd.randrange(3) for _ in range(5)]
            rev += sum(scene[v][0] for v in votes) / 5
            trust += sum(scene[v][1] for v in votes) / 5
        if hit(round(rev), round(trust)):
            wins += 1
    return wins / n * 100


def tier_random_path(effects):
    """有討論、但沒交換資訊：等於在 3^10 條路徑裡隨便挑一條。"""
    total = wins = 0
    for picks in itertools.product(range(3), repeat=10):
        total += 1
        if hit(*play(effects, picks)):
            wins += 1
    return wins / total * 100


def tier_informed(effects, n=20000, seed=7):
    """攤開角色卡之後：知道哪幾場該衝，其餘場次在 B/C 之間收斂。"""
    rnd = random.Random(seed)
    wins = 0
    for _ in range(n):
        rev = trust = float(START)
        for k, scene in enumerate(effects):
            votes = [0 if k in PUSH_SCENES else rnd.choice([1, 2]) for _ in range(5)]
            rev += sum(scene[v][0] for v in votes) / 5
            trust += sum(scene[v][1] for v in votes) / 5
        if hit(round(rev), round(trust)):
            wins += 1
    return wins / n * 100


def check_shape(effects):
    """設計不變式：每個選項兩軸都不能是 0（否則看起來像沒有代價），
    而且每一場至少要有一個選項在營收為負、一個在信任為負。"""
    bad = []
    for i, scene in enumerate(effects, 1):
        if any(o[0] == 0 or o[1] == 0 for o in scene):
            bad.append(f"第 {i} 場有零值選項")
        if not any(o[0] < 0 for o in scene):
            bad.append(f"第 {i} 場沒有營收為負的選項")
        if not any(o[1] < 0 for o in scene):
            bad.append(f"第 {i} 場沒有信任為負的選項")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-html", metavar="PATH",
                    help="改讀 public/index.html 的實際數值")
    ap.add_argument("--json", action="store_true", help="輸出 JSON")
    args = ap.parse_args()

    effects = parse_html(args.from_html) if args.from_html else EFFECTS
    source = args.from_html or "tools/balance_sim.py 內建常數"

    blind = tier_blind(effects)
    rnd_path = tier_random_path(effects)
    informed = tier_informed(effects)
    problems = check_shape(effects)

    pure = {}
    for name, idx in (("全衝 A", 0), ("全平衡 B", 1), ("全保守 C", 2)):
        r, t = play(effects, [idx] * 10)
        verdict = "雙達標" if hit(r, t) else ("營收不足" if r < TARGET_REV else "信任崩")
        pure[name] = {"rev": r, "trust": t, "verdict": verdict}

    if args.json:
        print(json.dumps({"source": source, "blind": blind, "random_path": rnd_path,
                          "informed": informed, "pure": pure, "problems": problems},
                         ensure_ascii=False, indent=2))
        return

    print(f"數值來源：{source}")
    print(f"門檻：營收 ≥{TARGET_REV}（多 28）　信任 ≥{TARGET_TRUST}（最多少 28）\n")
    print("三層對比（課程的核心論證）")
    print(f"  第一層　五人盲投　　　　　　　{blind:5.1f}%   目標 ~5%")
    print(f"  第二層　有討論、沒交換資訊　　{rnd_path:5.1f}%   目標 ~23%")
    print(f"  第三層　攤開角色卡、挑對場次　{informed:5.1f}%   目標 ~99%\n")
    print("單一策略走到底（三條都必須失敗，否則遊戲太好破）")
    for name, v in pure.items():
        print(f"  {name}: 營收 {v['rev']:3d}({v['rev']-100:+d})"
              f"  信任 {v['trust']:3d}({v['trust']-100:+d})  → {v['verdict']}")

    print("\n設計不變式：", "✅ 通過" if not problems else "❌ " + "；".join(problems))

    ok = (3.5 <= blind <= 7) and (18 <= rnd_path <= 30) and (informed >= 95) and not problems
    print("\n" + ("✅ 平衡在容許範圍內" if ok else "❌ 平衡跑掉了，不要就這樣上課"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
