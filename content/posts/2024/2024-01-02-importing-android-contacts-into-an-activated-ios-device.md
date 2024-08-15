---
author: 路边的阿不
title: 将Android通讯录导入已激活IOS设备
slug: importing-android-contacts-into-an-activated-ios-device
description: Learn how to import Android contacts into an activated iOS device without 'Move to iOS' app. Overcome the challenges of vCard version constraints with proven solutions.
date: 2024-01-02 10:10:24
draft: false
ShowToc: true
TocOpen: true
tags:
  - Github
categories:
  - 教程
---
那天，家里的长辈的`Android`手机坏了，正好我这里有台闲置的苹果手机。你可能想：哦，这挺简单的吧，启动新手机，下载`转移到 iOS`的APP，一键迁移就完事了。然而往往事情都不会这么顺利，正所谓“第一步错，步步错”来形容一点不为过。

## 安卓的倔强

我之前没做过这方面的迁移，因此随性而来：先安装微信，然后迁移微信数据。安装阿里云盘，然后迁移相册。直到迁移通讯录，发现阿里云盘不能迁移。网上一搜，看到苹果有个官方应用：`转移到 iOS`，兴高采烈安装，打开。等等，为什么没反应？

原来**用`转移到 iOS`来迁移数据必须在iPhone激活之前进行。** 已经到了现在这一步，为时已晚。

老人家的安卓手机早已苍老，只能导出通讯录文件到本地，保存为`.vcf`文件，也不支持蓝牙互传。迁移通讯录，就像是那一个执拗的孩子，打死不肯低头。

## 苹果的高傲

那怎么将`.vcf`文件导入到iPhone的通讯录呢？我在网上搜索答案，得到的解决方法是：需要通过网页版`iCloud`的“导入vcard联系人”功能。既然有方法，那就试试看。然而过程还是那么酸爽：当我尝试导入时，提示“无法导入”。

![import vcard](imgs/posts/2024-01-02-importing-android-contacts-into-an-activated-ios-device/截屏2024-01-02%2009.39.34.webp)

那一刹那，我心里那个呐喊啊，“苹果哥，你就饶了我这个卑微的Android战士吧，我只是想导入一个文件而已！”

## vCard版本转换

我继续在网上搜索，发现可能是我导出的`vCard`是`v2`版本，而`icloud`支持的是`v3`版本。继续搜索得知：通过将`vCard`导入qq邮箱，再从qq邮箱导出，以此来将`v2`版本升级到`v3`版本。然而在实际操作中，这个方法并不起作用。现在回想起来，可能这就是神的旨意，让我们能够更好的机会去体验编程师的高级乐趣吧。

遇到问题，当你已经尽力去解决，却无法得到答案时，怎会逃得过我们程序员的眼？在`GitHub`上，我找到了一个[vcard2to3](https://github.com/jowave/vcard2to3)的转换工具。三下五除二，"clone"源代码-"运行"-"转换"-再次"导入icloud"，瞧！成功了！

## 感想

生活中，你可能会遇到各种各样的问题和挑战，当你遇到问题，别忘了我们生活在一个丰富多彩的世界。你可以上网搜索，你可以问问身边的人，当然，你也可以行动起来，自己去解决问题。

毕竟，对于我们程序员来说，解决问题不过是我们日常工作的一部分，正如这次的通讯录搬家大戏，虽然过程曲折，但最终我们还是找到了解决问题的方法。于是，无论是在生活中还是在工作中，只要我们肯动脑筋，肯实践，那么总会有问题被我们解决的那一刻。

最后忍不住开一句玩笑，世上无难事，只要有`GitHub`，哈哈！