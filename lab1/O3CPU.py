import m5
from m5.objects import *
import argparse

class L1ICache(Cache):
    """L1 I-Cache"""
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    size = '32KiB'

class L1DCache(Cache):
    """L1 D-Cache"""
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    size = '64KiB'

class L2Cache(Cache):
    """L2 Cache"""
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12
    size = '256KiB'

parser = argparse.ArgumentParser()
def add_options(parser):
    parser.add_argument("-c", "--cmd", required=True, help="The binary to run.")
    parser.add_argument("--num-rob-entries", type=int, default=192)
    parser.add_argument("--num-iq-entries", type=int, default=64)
    parser.add_argument("--num-phys-int-regs", type=int, default=256)

    # 防止gdb卡住的
    parser.add_argument("--gdb-port", type=int, default=0,
                        help="Enable remote GDB on this port (0 = disable).")
    parser.add_argument("--gdb-wait", action="store_true",
                        help="Wait for GDB to attach before running.")
add_options(parser)
args = parser.parse_args()

# Create System
system = System()
system.clk_domain = SrcClockDomain(clock = '2GHz', voltage_domain = VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('2GiB')]
# RISC-V O3 CPU
system.cpu = RiscvO3CPU()
system.cpu.createInterruptController()
# Set CPU parameters
system.cpu.numROBEntries = args.num_rob_entries
system.cpu.numIQEntries = args.num_iq_entries
system.cpu.numPhysIntRegs = args.num_phys_int_regs
system.cpu.numPhysFloatRegs = 64
# Add buses
system.membus = SystemXBar()
system.l2bus = L2XBar()
# Add caches
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()
system.l2cache = L2Cache()
# Connect all components
system.cpu.icache_port = system.cpu.icache.cpu_side
system.cpu.dcache_port = system.cpu.dcache.cpu_side
system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports
system.l2bus.mem_side_ports = system.l2cache.cpu_side
system.l2cache.mem_side = system.membus.cpu_side_ports
system.system_port = system.membus.cpu_side_ports
# Create a memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8(range = system.mem_ranges[0])
system.mem_ctrl.port = system.membus.mem_side_ports

# Setup workload
process = Process()
process.cmd = [args.cmd]
system.workload = SEWorkload.init_compatible(args.cmd)
system.cpu.workload = process
system.cpu.createThreads()

# ===== 强制关闭 GDB 等待（无论谁把它打开过） =====
# 1) 等待标志 一律 False
if hasattr(system.cpu, "wait_for_remote_gdb"):
    system.cpu.wait_for_remote_gdb = False
if hasattr(system, "workload") and hasattr(system.workload, "wait_for_remote_gdb"):
    system.workload.wait_for_remote_gdb = False

# 2) 如果真的存在 remote_gdb 对象，直接移除
try:
    if hasattr(system, "remote_gdb"):
        delattr(system, "remote_gdb")  # 某些版本允许删除；不行也不会报错
except Exception:
    pass

# 3) 打印状态，方便你一眼确认
print(f"[GDB] wait_on_cpu={getattr(system.cpu,'wait_for_remote_gdb',None)} "
      f"wait_on_workload={getattr(system.workload,'wait_for_remote_gdb',None)} "
      f"has_remote_gdb={hasattr(system,'remote_gdb')}")
# ===============================================



# Instantiate and run
root = Root(full_system=False, system=system)
m5.instantiate()

print("--- Begin Simulation!!! ---")
print(f"  Binary: {args.cmd}")
print(f"  CPU: {type(system.cpu).__name__}")
print(f"  ROB Entries: {args.num_rob_entries}")
print(f"  IQ Entries: {args.num_iq_entries}")
print(f"  Physical Int Regs: {args.num_phys_int_regs}")
print("-----------------------------------")

exit_event = m5.simulate()

print('Exit @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))