#!/usr/bin/env bash
set -euo pipefail

GEM5="/root/gem5/build/RISCV/gem5.opt --remote-gdb-port=0 --listener-mode=off"
CFG=/lab1/O3CPU.py
BIN=/lab1/daxpy

OUTROOT=/lab1/sweep_out
mkdir -p "$OUTROOT"
echo "PR,IQ,ROB,numCycles,committedInsts,IPC,ROBFull,IQFull,RegFull" > "$OUTROOT/summary.csv"

# 参数设置
PRS=(64 256 1024)
IQS=(4 16 64 256)
ROBS=(4 16 64 256)

for PR in "${PRS[@]}"; do
  for IQ in "${IQS[@]}"; do
    for ROB in "${ROBS[@]}"; do
      OUTDIR="${OUTROOT}/pr${PR}_iq${IQ}_rob${ROB}"
      echo "==> PR=$PR IQ=$IQ ROB=$ROB"
      eval $GEM5 --outdir="$OUTDIR" "$CFG" -c "$BIN" \
        --num-phys-int-regs=$PR --num-iq-entries=$IQ --num-rob-entries=$ROB

      STATS="$OUTDIR/stats.txt"
      CYC=$(awk '/^system\.cpu\.numCycles/{print $2}'                          "$STATS")
      CI=$(awk  '/^system\.cpu\..*committed.*Insts/{print $2}'                 "$STATS")
      ROBF=$(awk '/^system\.cpu\..*(ROB).*Full.*Events/{print $2}'             "$STATS")
      IQF=$(awk  '/^system\.cpu\..*(IQ).*Full.*Events/{print $2}'              "$STATS")
      REGF=$(awk '/^system\.cpu\..*(Reg|Registers).*Full.*Events/{print $2}'   "$STATS")
      IPC=$(awk -v ci="${CI:-0}" -v cy="${CYC:-1}" 'BEGIN{printf "%.6f", (cy==0?0:ci/cy)}')

      echo "${PR},${IQ},${ROB},${CYC},${CI},${IPC},${ROBF},${IQF},${REGF}" >> "$OUTROOT/summary.csv"
    done
  done
done

echo "Done -> $OUTROOT/summary.csv"
