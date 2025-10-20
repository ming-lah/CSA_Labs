# CSA_LAB

该项目为计算机体系结构课程项目，包含多个实验项目内容

## 环境配置

项目使用**gem5**进行仿真实验，**gem5**需要Linux环境，可以在以下3种环境中进行部署：
- 虚拟机 (VMWare, VirtualBox)
- Docker容器
- WSL

本项目使用**Docker**部署，并使用Vscode进行远程连接，较为方便，下面给出Docker容器部署gem5的流程，其他部署可以参考[官方教程](https://www.gem5.org/documentation/general_docs/building)

### 准备

首先需要确认虚拟化开启，随后以管理员身份启动命令提示符，输入`wsl --install`安装WSL。随后安装Docker，Vscode中安装Dev-Containers插件。

### Docker容器处理
在powershell下载Docker镜像
```powershell
docker pull ghcr.io/gem5/ubuntu-24.04_all-dependencies:latest
```

启动Docker容器
```powershell
docker run -it -v [lab1 directory]:/lab1 [image]
```
参数：
1. `-v [lab1 directory]:/lab1`
这是数据卷挂载 (volume mount)：
- 左边： [lab1 directory] ->Windows主机上的目录
- 右边： /lab1 ->容器内部的目录
挂载后，你在容器`/lab1`里看到的文件，就是`Windows`目录`[lab1 directory]`的内容，修改也会实时同步
2. `[image]`
指定要运行的Docker镜像

### 连接容器

在Vscode中Ctrl+Shift+P → Dev Containers: Attach to Running Container选择启动的容器即可。

### 使用Scons构建gem5

首先克隆gem5仓库，注意可能涉及到代理的问题，如果docker中的代理被错误设置，如下：
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
同时需要注意，不建议在windows本地克隆代码，否则可能因linux与windos的不兼容问题导致代码错误，安全的做法是在容器内clone代码。

clone完成后，cd进入gem5的根目录构建：
```powershell
scons build/RISCV/gem5.opt -j 2
```
构造过程比较久，大约需要2小时。

### 检验安装

完成构建后可以进行简单的检验，查看是否正确安装，使用如下命令，如果终端出现Hello world!则郑明明正确安装。
```powershell
cd ~/gem5
build/RISCV/gem5.opt configs/deprecated/example/se.py  -c tests/test-progs/hello/bin/riscv/linux/hello
```