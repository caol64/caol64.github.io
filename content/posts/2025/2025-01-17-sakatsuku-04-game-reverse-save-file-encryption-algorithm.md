---
author: "路边的阿不"
title: 球会04游戏逆向-存档加密算法
slug: sakatsuku-04-game-reverse-save-file-encryption-algorithm
description: ""
date: 2025-01-17 09:04:50
draft: false
ShowToc: true
TocOpen: true
tags:
  - Reverse
categories:
  - Sakatsuku04
---
![](imgs/posts/2025-01-14-sakatsuku-04-game-reverse-save-file-analysis/cover.jpg)

话接上回，文章提到“主存档文件使用`Bit-Packing`技术进行压缩，再使用`BlowFish`算法进行加密”。我们是如何确定加密算法的呢？

## 工具选择

“工欲善其事，必先利其器”，既然我们要对`PS2`游戏进行逆向，适合的工具是必不可少的。本文需要使用以下两个工具：

- [PSCX2](https://pcsx2.net/) -- `PS2`模拟器，带`debug`功能
- [Ghidra](https://ghidra-sre.org/) -- 逆向神器

`PSCX2`挑最新稳定版安装，`GHDIRA`安装说明如下：

- 确保本机已安装`JDK21`
- [下载`Ghidra 11.2.1`](https://github.com/NationalSecurityAgency/ghidra/releases)。
- [下载`emotionengine`插件](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/releases)，注意匹配`Ghidra`版本。
- 将插件解压缩，得到`ghidra-emotionengine-reloaded`目录，将该目录复制到`Ghidra`根目录下的`Ghidra/Extensions/`目录下。
- 运行`./ghidraRun`命令启动。

`PSCX2`配置说明如下：

- 菜单“工具”下勾选“显示高级设置“。
- 进入“设置”界面，选择“高级”，在“即时存档设置“选项卡中将“压缩模式”从“ZStandard“改成“未压缩”。（注意这一步是非必须的，这样做会导致游戏即时存档变大）

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/1.jpg)

## Dump游戏内存

启动`PSCX2`，进入游戏，在游戏进入到读取存档界面时暂停。

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/2.jpg)

选择“保存即时存档”。

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/3.jpg)

转到`PSCX2`安装目录下的`sstates`目录，找到刚才保存的即时存档。

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/4.jpg)

注意看03和04两个文件，03是使用`ZStandard`压缩过的，04是未压缩的。

在`MAC`环境下，可以直接使用“归档实用工具”解包。

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/5.jpg)

在解包目录下，找到`eeMemory.bin`，这就是我们今天要分析的游戏内存。

## 内存逆向

将`eeMemory.bin`拖拽进`Ghidra`，此时会弹出目标语言选择界面：

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/6.jpg)

如果之前的插件安装步骤正确完成，应该可以出现`MIPS-R5900`选项，选择它。之后出现的`Analysis`选项保留默认即可。

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/7.jpg)

之后点击`Analyze`进行分析，分析完毕后会出现如下界面：

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/8.jpg)

恭喜你，你获得了游戏中的部分函数代码。但是这些函数是由反编译引擎反编译出来的，可读性非常差，懂得都懂。

## 搜索加密函数

回到`PSCX2`，在菜单栏选择“调试”-“打开调试器“。

在调试器中选中“函数”选项卡，在下面的输入框中输入`BF_`，此时出现在最上方的两个函数即是我们感兴趣的，记住它们的内存位置。

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/9.jpg)

切换到`Ghidra`，在键盘按下`G`，出现对话框，输入内存地址`378f10`。此时会定位到一个函数，函数名为`Fun_`后面跟地址偏移量。

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/10.jpg)

点击函数，右键`Edit Function Signature`，将函数名改为游戏中的`BF_En`。

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/11.jpg)

![](imgs/posts/2025-01-17-sakatsuku-04-game-reverse-save-file-encryption-algorithm/12.jpg)

这样就顺眼多了。

## 破解加密函数

到了这一步是真正考验你编程技术的时刻了，读懂函数逻辑并将其改写为你自己熟悉的语言是这一步的目标。

根据函数名和函数逻辑大致可以判断出加密算法是`BlowFish`，当然你可以借助`ChatGPT`进一步确认。

## 最后

如果你对球会04游戏逆向感兴趣，欢迎关注[Github](https://github.com/caol64/sakatsuku04)，我之后会将逆向代码逐步上传，目标是完成一个存档查看甚至是编辑器。