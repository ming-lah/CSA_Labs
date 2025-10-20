# -*- coding: utf-8 -*-
# plot_sweep.py  —— Windows 本地版
# 生成图表到 LAB1\images\，并输出“收益递减”表与透视表

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------- 路径设置（相对脚本自身）--------
BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "summary.csv"              # 你的汇总表
OUTDIR   = BASE / "images"                   # 输出图表文件夹
OUTDIR.mkdir(parents=True, exist_ok=True)

print(f"[INFO] CSV: {CSV_PATH}")
if not CSV_PATH.exists():
    print("[ERROR] 找不到 summary.csv，请确认放在 LAB1 同目录。")
    sys.exit(1)

df = pd.read_csv(CSV_PATH)

# -------- 列名兼容映射 --------
def pick(df, *names):
    m = {c.lower(): c for c in df.columns}
    for n in names:
        if n in df.columns: return n
        if n.lower() in m:  return m[n.lower()]
    return None

col_pr   = pick(df, "PR","pr","num_phys_int_regs","num-phys-int-regs","phys_int","PhysInt")
col_iq   = pick(df, "IQ","iq","num_iq_entries","num-iq-entries","IQEntries")
col_rob  = pick(df, "ROB","rob","num_rob_entries","num-rob-entries","ROBEntries")
col_cyc  = pick(df, "Cycles","cycles","numCycles","system.cpu.numCycles","system.cpu.numcycles")
col_iqev = pick(df, "system.cpu.rename.IQFullEvents","IQFullEvents","iq_full_events","iqfull")
col_robev= pick(df, "system.cpu.rename.ROBFullEvents","ROBFullEvents","rob_full_events","robfull")
col_prev = pick(df, "system.cpu.rename.fullRegistersEvents","fullRegistersEvents","full_regs_events","regfull")

print("[INFO] 列映射：", {"PR":col_pr,"IQ":col_iq,"ROB":col_rob,"Cycles":col_cyc,
                   "IQFullEvents":col_iqev,"ROBFullEvents":col_robev,"fullRegistersEvents":col_prev})

# 数值化
for c in [col_pr, col_iq, col_rob, col_cyc, col_iqev, col_robev, col_prev]:
    if c and df[c].dtype.kind not in "biufc":
        df[c] = pd.to_numeric(df[c], errors="coerce")

# 必要列
essential = [x for x in [col_iq, col_rob, col_cyc] if x]
df = df.dropna(subset=essential).copy()

# -------- 工具函数 --------
def avg_series(xcol, ycol):
    return df.groupby(xcol)[ycol].mean().sort_index()

def save_line(series, title, xlabel, ylabel, fname):
    plt.figure()
    series.plot(marker="o")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    out = OUTDIR / fname
    plt.savefig(out)
    plt.close()
    print("[PLOT]", out)

def improvements(series):
    arr = series.values.astype(float)
    xs  = series.index.values.astype(float)
    if len(arr) < 2:
        return pd.DataFrame(columns=["from","to","rel_improve(%)"])
    rel_imp = -np.diff(arr) / arr[:-1] * 100.0  # cycles 下降 => 正向改善
    return pd.DataFrame({"from": xs[:-1], "to": xs[1:], "rel_improve(%)": rel_imp})

# -------- 1) IQ vs Cycles --------
if col_iq and col_cyc:
    g_iq = avg_series(col_iq, col_cyc)
    save_line(g_iq, "Average numCycles vs IQ entries", "IQ entries", "Average numCycles", "iq_vs_cycles.png")
    imp_iq = improvements(g_iq)
    imp_iq.to_csv(OUTDIR / "iq_diminishing_returns.csv", index=False)
    print("\n[IQ 收益递减表]\n", imp_iq)

# -------- 2) ROB vs Cycles --------
if col_rob and col_cyc:
    g_rob = avg_series(col_rob, col_cyc)
    save_line(g_rob, "Average numCycles vs ROB entries", "ROB entries", "Average numCycles", "rob_vs_cycles.png")
    imp_rob = improvements(g_rob)
    imp_rob.to_csv(OUTDIR / "rob_diminishing_returns.csv", index=False)
    print("\n[ROB 收益递减表]\n", imp_rob)

# -------- 3) ROB × IQ 热力图 --------
if col_rob and col_iq and col_cyc:
    pivot = df.pivot_table(index=col_rob, columns=col_iq, values=col_cyc, aggfunc="mean").sort_index().sort_index(axis=1)
    pivot_path = OUTDIR / "pivot_rob_by_iq_cycles.csv"
    pivot.to_csv(pivot_path)
    print("[CSV] 透视表：", pivot_path)

    plt.figure()
    plt.imshow(pivot.values, aspect="auto", origin="lower")
    plt.title("numCycles heatmap (rows=ROB, cols=IQ)")
    plt.xlabel("IQ entries")
    plt.ylabel("ROB entries")
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=0)
    plt.yticks(range(len(pivot.index)),  pivot.index)
    plt.tight_layout()
    heat = OUTDIR / "heatmap_rob_iq_cycles.png"
    plt.savefig(heat); plt.close()
    print("[PLOT]", heat)

# -------- 4) PR vs Cycles（若有 PR） --------
if col_pr and col_cyc:
    g_pr = avg_series(col_pr, col_cyc)
    save_line(g_pr, "Average numCycles vs Phys Int Regs (PR)", "Phys Int Regs (PR)", "Average numCycles", "pr_vs_cycles.png")
    imp_pr = improvements(g_pr)
    imp_pr.to_csv(OUTDIR / "pr_diminishing_returns.csv", index=False)
    print("\n[PR 收益递减表]\n", imp_pr)

# -------- 5) *FullEvents 趋势（若有） --------
if col_iq and col_iqev:
    s = avg_series(col_iq, col_iqev)
    save_line(s, "Avg IQFullEvents vs IQ", "IQ entries", "Avg IQFullEvents", "iq_events_vs_iq.png")
if col_rob and col_robev:
    s = avg_series(col_rob, col_robev)
    save_line(s, "Avg ROBFullEvents vs ROB", "ROB entries", "Avg ROBFullEvents", "rob_events_vs_rob.png")
if col_pr and col_prev:
    s = avg_series(col_pr, col_prev)
    save_line(s, "Avg fullRegistersEvents vs PR", "Phys Int Regs (PR)", "Avg fullRegistersEvents", "pr_events_vs_pr.png")

print("\n[DONE] 所有图和表已输出到：", OUTDIR)
