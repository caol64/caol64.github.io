---
author: "路边的阿不"
title: 「译」GitHub推出后量子安全的密钥交换机制，保护传输中的数据
slug: github-introduces-post-quantum-secure-ssh-key-exchange-mechanism
description: ""
date: 2025-10-14 16:38:48
draft: false
ShowToc: true
TocOpen: true
tags:
  - Quantum Cryptography
  - Cryptography
  - Translation
  - Secure
categories:
  - 网络安全
---

> GitHub 正在为通过 SSH 与 Git 交互时的 SSH 访问引入一种混合后量子安全密钥交换算法。

GitHub 已[为通过 SSH 与 Git 交互的场景引入一种混合后量子安全密钥交换算法](https://github.blog/engineering/platform-security/post-quantum-security-for-ssh-access-on-github)。该新算法 sntrup761x25519-sha512（也称为 sntrup761x25519-sha512@openssh.com），结合了[简化版 NTRU Prime](https://ntruprime.cr.yp.to/)（一种后量子密码学方案）与经典椭圆曲线[X25519](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/x25519/)。此举旨在保护 Git 数据，防范未来量子计算机可能对今日记录的 SSH 会话进行解密所带来的潜在威胁。

此次更新影响通过 SSH 终端访问 Git 数据的连接（不包括 HTTPS），自 2025 年 9 月 17 日起在 [GitHub.com](http://github.com) 及非美国地区的 GitHub Enterprise Cloud 平台上线。美国地区暂不包含在内，因其适用更严格的[FIPS 加密标准](https://learn.microsoft.com/en-us/compliance/regulatory/offering-fips-140-2)，而该新算法尚未通过 FIPS 认证。GitHub Enterprise Server 3.19 也将包含此项新的[后量子](https://en.wikipedia.org/wiki/Post-quantum_cryptography)选项。

对于不熟悉该领域的用户，后量子密码学（PQC）指的是一类专为抵御量子计算机攻击而设计的新一代加密算法。目前广泛使用的公钥算法，如[RSA](https://www.rsa.com/)和[椭圆曲线密码学](https://www.geeksforgeeks.org/ethical-hacking/blockchain-elliptic-curve-cryptography/)（ECC），依赖于整数分解和离散对数等数学难题，而这些难题可被具备足够算力的量子计算机利用[Shor 算法](https://www.fortinet.com/resources/cyberglossary/shors-grovers-algorithms)高效破解。一旦量子计算机达到实用规模，这些方案可能在数秒内被攻破，严重威胁安全通信的机密性与完整性。

为应对这一风险，在[NIST 后量子密码标准化项目](https://csrc.nist.gov/projects/post-quantum-cryptography)等倡议的引领下，研究人员和机构已开发出基于不同数学基础（例如[格问题](https://en.wikipedia.org/wiki/Lattice-based_cryptography)、[基于编码的密码学](https://utimaco.com/service/knowledge-base/post-quantum-cryptography/what-code-based-cryptography)、[多元方程](https://www.khanacademy.org/math/multivariable-calculus/thinking-about-multivariable-function/ways-to-represent-multivariable-functions/a/multivariable-functions)）的抗量子算法。许多此类算法现已逐步整合进实际系统中，常以混合模式运行——结合经典算法与后量子算法，兼顾当前互操作性与未来安全性。GitHub 的这一 SSH 新举措，正是在保障今日向后兼容的同时，为基础设施抵御量子威胁迈出的关键一步。

从用户角度看，大多数工作流程几乎不会发生变化。若您使用的 SSH 客户端支持该新算法（例如 OpenSSH 9.0 或更高版本），默认将自动协商并优先使用该算法（前提是您的配置未覆盖默认设置）。不支持该算法的客户端将继续使用传统密钥交换方式，不受影响。GitHub 还提供命令如 `ssh -Q kex` 列出支持的密钥交换算法，以及 `ssh -v git@github.com exit | grep 'kex: algorithm:'` 查看连接时实际选定的算法。

此举的核心动机是应对“先存储，后解密”（store now, decrypt later）的威胁：攻击者可在今日截获 SSH 加密流量，待未来量子计算机具备足够算力后再行解密。通过采用结合经典安全与后量子密码学的混合方案，GitHub 确保即便量子计算使当前算法失效，SSH 流量依然受到保护。

GitHub 同时指出，尽管该新算法较新、实际应用经验较少，但其设计目标始终不低于现有经典密钥交换方法的安全强度。展望未来，GitHub 计划持续关注后量子密码学的发展，并逐步扩展对更多量子安全密钥交换算法的支持，特别是符合 FIPS 要求的算法。

[OpenSSH](https://www.openssh.com/pq.html) 已率先向后量子密码（PQC）算法迈进。自 2022 年 4 月发布的 9.0 版本起，OpenSSH 即已内置 sntrup761x25519-sha512 密钥协商算法（混合模式，结合经典算法与 PQC）。近期，OpenSSH 9.9 增加了 mlkem768x25519-sha256 算法，至 10.0 版本，该算法已成为默认的密钥交换方案。这与 GitHub 推出混合后量子 SSH 密钥交换的举措高度一致。

同样，SSH.com 的[Tectia Quantum-Safe Edition](https://www.ssh.com/products/tectia-ssh/quantum-safe) 通过将经典加密与后量子算法（如[Crystals/Kyber](https://medium.com/identity-beyond-borders/crystals-kyber-the-key-to-post-quantum-encryption-3154b305e7bd)、[FrodoKem](https://frodokem.org/) 和 [NTRU](https://ntru.org/)）结合，提供混合且量子安全的 SSH 实现。它同时兼容 FIPS 模式及传统 SSH 客户端/服务器，其策略同样兼顾前瞻性的 PQC 防护与现有系统的兼容性。

[TinySSH](https://opensource.com/article/20/7/tinyssh)（一款轻量级 SSH 服务器）也已率先尝试混合 PQC 密钥交换。它支持将 NTRU Prime 与[ED25519](https://en.wikipedia.org/wiki/Curve25519) 曲线运算结合，为 SSH 密钥协商增加量子前向保密性。尽管 TinySSH 的实现仍属实验性质，但它展示了小型、专注型 SSH 工具同样在积极采纳混合 PQC 密钥交换模型。

## 作者简介

#### **Craig Risi**