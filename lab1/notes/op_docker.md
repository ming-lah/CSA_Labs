## 命令

- **重命名命令**
```powershell
# 在 PowerShell（Windows）里
docker ps -a   # 找到现在这个容器的 NAME
docker rename 旧名字 gem5-dev
```

- **启动命令**
```powershell
# 纯命令进入模式
docker start -ai gem5-dev

# Vscode交互模式
docker start gem5-dev
# 随后VS Code → Ctrl+Shift+P → Dev Containers: Attach to Running Container... → 选 gem5-dev
``` 

- **停止/退出**
容器内输入exit或者关闭Vscode连接窗口即可

## 代理解决

针对docker中被错误设置的代理情况，如下
```powershell
root@86bcef818dae:~# git config --global --get http.proxy
http://127.0.0.1:7897
```
进行下面的操作，将容器中的代理关闭：
```powershell
# 移除 git 里的代理设置
git config --global --unset http.proxy
git config --global --unset https.proxy

# 确保成功移除
git config -l | grep -i proxy || echo "no git proxy now"

# 进行克隆
git clone https://github.com/gem5/gem5.git
```
如果想要设置容器走clash代理，如下操作：
1. 在宿主机的代理工具里开启允许局域网
2. 进行如下配置修改，使其正确指向宿主机
```powershell
export http_proxy=http://host.docker.internal:7897
export https_proxy=http://host.docker.internal:7897
git config --global http.proxy http://host.docker.internal:7897
git config --global https.proxy http://host.docker.internal:7897

apt update && apt install -y ca-certificates curl
curl -I https://github.com

git clone https://github.com/gem5/gem5.git
```

## 注意

- **测试过程**
说明文档中的测试是否正确代码复制时存在问题，文件夹`test-progs`可能会少复制符号`-`，可参考如下命令确认：
```powershell
# 确认命令存在
ls tests/test-progs/hello/bin/riscv/linux/

# 进行hello world的测试
build/RISCV/gem5.opt configs/deprecated/example/se.py  -c tests/test-progs/hello/bin/riscv/linux/hello
```


- **编译**
进行如下的操作：
```powershell
cd /lab1

# 安装相应的工具包
sudo apt update
sudo apt install -y g++-riscv64-linux-gnu

# 编译
riscv64-linux-gnu-g++ --static -O2 -o daxpy daxpy.cpp
```

- **执行文件转换**

```powershell
# 仿真
/root/gem5/build/RISCV/gem5.opt --outdir=/lab1/m5out_try /lab1/O3CPU.py -c /lab1/daxpy --num-phys-int-regs=256 --num-iq-entries=64 --num-rob-entries=192

# 查看关键指标
grep -E '^system\.cpu\.numCycles' /lab1/m5out_try/stats.txt
```

