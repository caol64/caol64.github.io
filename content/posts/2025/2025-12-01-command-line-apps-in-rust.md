---
author: "路边的阿不"
title: 「译」Rust 中的命令行应用
slug: command-line-apps-in-rust
description: "Translation of 'Command line apps in Rust'"
date: 2025-12-01 11:53:36
draft: false
ShowToc: true
TocOpen: true
tags:
  - Translation
  - Rust
categories:
  - 文档翻译
---

原文链接：https://rust-cli.github.io/book/

# [Rust 中的命令行应用](#command-line-apps-in-rust)

Rust 是一种静态编译、快速的语言，拥有优秀的工具链和迅速扩展的生态系统。这使其非常适合编写命令行应用程序：它们应当小巧、可移植且运行迅速。命令行应用程序也是学习 Rust 的绝佳起点，或向你的团队引入 Rust 的理想方式！

编写一个具有简单命令行界面（CLI）的程序，是刚接触该语言的初学者了解其特性的绝佳练习。然而，这一主题涉及许多方面，这些方面往往在后期才逐渐显现。

本书结构如下：我们首先提供一个快速教程，完成后你将拥有一个可运行的 CLI 工具。你将接触到 Rust 的一些核心概念以及 CLI 应用的主要方面。接下来的章节将深入探讨其中的一些细节。

在深入 CLI 应用之前，最后一件事：如果你发现本书中有错误，或希望帮助我们撰写更多内容，你可以在 [CLI 书籍仓库](https://github.com/rust-cli/book) 中找到其源代码。我们非常期待你的反馈！谢谢！

# [通过在 15 分钟内编写命令行应用来学习 Rust](#learning-rust-by-writing-a-command-line-app-in-15-minutes)

本教程将引导你使用 [Rust](https://rust-lang.org/) 编写一个 CLI（命令行界面）应用程序。大约十五分钟后，你将拥有一段可运行的程序（约第 1.3 节）。之后，我们将继续调整程序，直到我们可以发布这个小工具。

你将学到所有入门所需的基本知识，以及如何找到更多信息。你可以自由跳过目前不需要的部分，或在任何时刻加入进来。

**先决条件**：本教程不替代编程的通用入门，它要求你熟悉一些常见概念。你应该能熟练使用命令行/终端。如果你已经掌握几种其他语言，这将是接触 Rust 的良好开端。

**获取帮助**：如果你在任何时刻对所使用的特性感到困惑或不知所措，请首先查阅 Rust 自带的详尽官方文档，尤其是《Rust 编程语言》一书。它随大多数 Rust 安装一起提供（`rustup doc`），也可在线访问 [doc.rust-lang.org](https://doc.rust-lang.org)。

你也可以随时提问——Rust 社区以友好和乐于助人著称。请查看 [社区页面](https://www.rust-lang.org/community)，了解人们讨论 Rust 的各种场所。

你想编写什么样的项目？不如我们从一个简单的开始：我们来编写一个 `grep` 的小型克隆。这是一个工具，你可以传入一个字符串和一个路径，它将仅打印包含该字符串的行。我们称它为 `grrs`（发音为“grass”）。

最终，我们希望可以像这样运行我们的工具：

```console
$ cat test.txt
foo: 10
bar: 20
baz: 30
$ grrs foo test.txt
foo: 10
$ grrs --help
[一些解释可用选项的帮助文本]
```

**注意**：本书是为 [Rust 2018](https://doc.rust-lang.org/edition-guide/index.html) 编写的。代码示例也可在 Rust 2015 上使用，但你可能需要稍作调整，例如添加 `extern crate foo;` 声明。

请确保你运行的是 Rust 1.31.0（或更高版本），并在 `Cargo.toml` 文件的 `[package]` 部分设置 `edition = "2018"`。

# 项目设置

如果你尚未安装，请在你的计算机上 [安装 Rust](https://www.rust-lang.org/tools/install)（只需几分钟）。之后，打开终端并导航到你希望存放应用程序代码的目录。

在存放编程项目的目录中，运行 `cargo new grrs`。如果你查看新创建的 `grrs` 目录，你会看到一个典型的 Rust 项目结构：

- 一个 `Cargo.toml` 文件，包含我们项目的元数据，包括我们使用的依赖项/外部库列表。
- 一个 `src/main.rs` 文件，是我们（主）二进制文件的入口点。

如果你能在 `grrs` 目录中执行 `cargo run` 并看到 “Hello World”，那么你的环境已设置完毕。

## [可能的样子](#what-it-might-look-like)

```console
$ cargo new grrs
     Created binary (application) `grrs` package
$ cd grrs/
$ cargo run
   Compiling grrs v0.1.0 (/Users/pascal/code/grrs)
    Finished dev [unoptimized + debuginfo] target(s) in 0.70s
     Running `target/debug/grrs`
Hello, world!
```

# [解析命令行参数](#parsing-command-line-arguments)

我们 CLI 工具的典型调用方式如下：

```console
$ grrs foobar test.txt
```

我们期望程序检查 `test.txt` 并打印出包含 `foobar` 的行。但我们如何获取这两个值？

程序名称之后的文本通常称为“命令行参数”或“命令行标志”（特别是当它们看起来像 `--this` 时）。在内部，操作系统通常将它们表示为字符串列表。通常，它们通过空格分隔。

有多种方式思考这些参数及其如何解析为更易处理的形式。你还需要告诉用户你的程序需要哪些参数以及期望的格式。

## [获取参数](#getting-the-arguments)

标准库包含函数 [`std::env::args()`](https://doc.rust-lang.org/1.39.0/std/env/fn.args.html)，它返回一个给定参数的 [迭代器](https://doc.rust-lang.org/1.39.0/std/iter/index.html)。第一个条目（索引为 `0`）是你调用程序时使用的名称（例如 `grrs`）。其后的是用户随后输入的内容。

以这种方式获取原始参数非常直接（在文件 `src/main.rs` 中）：

```rust
fn main() {
    let pattern = std::env::args().nth(1).expect("未提供模式");
    let path = std::env::args().nth(2).expect("未提供路径");

    println!("模式: {:?}, 路径: {:?}", pattern, path)
}
```

我们可以使用 `cargo run` 运行它，通过在 `--` 之后写入参数来传递它们：

```console
$ cargo run -- some-pattern some-file
    Finished dev [unoptimized + debuginfo] target(s) in 0.11s
     Running `target/debug/grrs some-pattern some-file`
模式: "some-pattern", 路径: "some-file"
```

## [CLI 参数作为数据类型](#cli-arguments-as-data-types)

与其将它们视为一堆文本，不如将 CLI 参数视为代表程序输入的自定义数据类型，这往往更有益。

观察 `grrs foobar test.txt`，有两个参数：首先是 `pattern`（要查找的字符串），然后是 `path`（要查找的文件）。

我们还能对它们说些什么？首先，两者都是必需的。我们尚未讨论任何默认值，因此我们期望用户始终提供两个值。此外，我们可以说一点它们的类型：模式预期为字符串，而第二个参数预期为文件路径。

在 Rust 中，通常围绕程序处理的数据来构建程序，因此这种看待 CLI 参数的方式非常契合。让我们从这里开始（在文件 `src/main.rs` 中，在 `fn main() {` 之前）：

```rust
struct Cli {
    pattern: String,
    path: std::path::PathBuf,
}
```

这定义了一个新的结构体（一个 [`struct`](https://doc.rust-lang.org/1.39.0/book/ch05-00-structs.html)），包含两个字段来存储数据：`pattern` 和 `path`。

**注意**：[`PathBuf`](https://doc.rust-lang.org/1.39.0/std/path/struct.PathBuf.html) 类似于 [`String`](https://doc.rust-lang.org/1.39.0/std/string/struct.String.html)，但用于跨平台的文件系统路径。

现在，我们仍需要将实际参数转换为此形式。一种选择是手动解析操作系统提供的字符串列表并自行构建结构体。它看起来像这样：

```rust
fn main() {
    let pattern = std::env::args().nth(1).expect("未提供模式");
    let path = std::env::args().nth(2).expect("未提供路径");

    let args = Cli {
        pattern,
        path: std::path::PathBuf::from(path),
    };

    println!("模式: {:?}, 路径: {:?}", args.pattern, args.path);
}
```

这可行，但不太方便。你如何处理支持 `--pattern="foo"` 或 `--pattern "foo"` 的要求？你如何实现 `--help`？

## [使用 Clap 解析 CLI 参数](#parsing-cli-arguments-with-clap)

更便捷的方式是使用众多可用库之一。解析命令行参数最流行的库称为 [`clap`](https://docs.rs/clap/)。它包含你期望的所有功能，包括对子命令、[shell 补全](https://docs.rs/clap_complete/) 和优秀的帮助信息的支持。

首先，通过在 `Cargo.toml` 文件的 `[dependencies]` 部分添加 `clap = { version = "4.0", features = ["derive"] }` 来导入 `clap`。

现在，我们可以在代码中写入 `use clap::Parser;`，并在我们的 `struct Cli` 上方添加 `#[derive(Parser)]`。同时，我们还可以编写一些文档注释。

它看起来像这样（在文件 `src/main.rs` 中，在 `fn main() {` 之前）：

```rust
use clap::Parser;

/// 在文件中搜索模式并显示包含它的行。
#[derive(Parser)]
struct Cli {
    /// 要查找的模式
    pattern: String,
    /// 要读取的文件路径
    path: std::path::PathBuf,
}
```

**注意**：你可以为字段添加许多自定义属性。例如，如果你想使用此字段作为 `-o` 或 `--output` 之后的参数，你可以添加 `#[arg(short = 'o', long = "output")]`。更多信息请参见 [clap 文档](https://docs.rs/clap/)。

在 `Cli` 结构体下方，我们的模板包含其 `main` 函数。当程序启动时，它将调用此函数：

```rust
fn main() {
    let args = Cli::parse();

    println!("模式: {:?}, 路径: {:?}", args.pattern, args.path)
}
```

这将尝试将参数解析为我们的 `Cli` 结构体。

但如果失败了怎么办？这种方法的美妙之处在于：Clap 知道它期望哪些字段及其预期格式。它可以自动生成一个漂亮的 `--help` 消息，并在你输入 `--putput` 时提示你应传递 `--output`。

**注意**：`parse` 方法旨在用于你的 `main` 函数中。当它失败时，它将打印错误或帮助信息并立即退出程序。不要在其他地方使用它！

## [总结](#wrapping-up)

你的代码现在应如下所示：

```rust
use clap::Parser;

/// 在文件中搜索模式并显示包含它的行。
#[derive(Parser)]
struct Cli {
    /// 要查找的模式
    pattern: String,
    /// 要读取的文件路径
    path: std::path::PathBuf,
}

fn main() {
    let args = Cli::parse();

    println!("模式: {:?}, 路径: {:?}", args.pattern, args.path)
}
```

不带任何参数运行它：

```console
$ cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 10.16s
     Running `target/debug/grrs`
错误：以下必需参数未提供：
    <pattern>
    <path>

用法：
    grrs <pattern> <path>

更多信息请尝试 --help
```

传递参数运行它：

```console
$ cargo run -- some-pattern some-file
    Finished dev [unoptimized + debuginfo] target(s) in 0.11s
     Running `target/debug/grrs some-pattern some-file`
模式: "some-pattern", 路径: "some-file"
```

输出表明我们的程序成功将参数解析为 `Cli` 结构体。

# [grrs 的初步实现](#first-implementation-of-grrs)

在上一章关于命令行参数之后，我们有了输入数据，可以开始编写我们的实际工具了。我们的 `main` 函数目前只包含这一行：

```rust
let args = Cli::parse();
```

我们可以删除之前为演示程序正常工作而添加的 `println` 语句。

让我们从打开我们获得的文件开始。

```rust
let content = std::fs::read_to_string(&args.path).expect("无法读取文件");
```

**注意**：这里看到的 [`.expect`](https://doc.rust-lang.org/1.39.0/std/result/enum.Result.html#method.expect) 方法吗？这是一个快捷函数，当值（在这种情况下是输入文件）无法读取时，会立即退出程序。它并不美观，在下一章 [更好的错误报告](./errors.html) 中，我们将探讨如何改进这一点。

现在，让我们遍历行并打印包含我们模式的每一行：

```rust
for line in content.lines() {
        if line.contains(&args.pattern) {
            println!("{}", line);
        }
    }
```

## [总结](#wrapping-up)

你的代码现在应如下所示：

```rust
use clap::Parser;

/// 在文件中搜索模式并显示包含它的行。
#[derive(Parser)]
struct Cli {
    /// 要查找的模式
    pattern: String,
    /// 要读取的文件路径
    path: std::path::PathBuf,
}

fn main() {
    let args = Cli::parse();
    let content = std::fs::read_to_string(&args.path).expect("无法读取文件");

    for line in content.lines() {
        if line.contains(&args.pattern) {
            println!("{}", line);
        }
    }
}
```

尝试一下：`cargo run -- main src/main.rs` 现在应该可以工作了！

**读者练习**：这不是最佳实现，因为它会将整个文件读入内存，无论文件有多大。找到一种优化方法！（一个想法可能是使用 [`BufReader`](https://doc.rust-lang.org/1.39.0/std/io/struct.BufReader.html) 而不是 `read_to_string()`。）

# 更好的错误报告

我们都不得不接受错误总会发生的事实。与许多其他语言不同，在使用 Rust 时很难忽视或忽略这一现实，因为它没有异常。所有可能的错误状态通常都编码在函数的返回类型中。

## [结果](#results)

像 [`read_to_string`](https://doc.rust-lang.org/1.39.0/std/fs/fn.read_to_string.html) 这样的函数不会返回一个字符串。相反，它返回一个 [`Result`](https://doc.rust-lang.org/1.39.0/std/result/index.html)，其中包含一个 `String` 或某种类型的错误。在这种情况下，是 [`std::io::Error`](https://doc.rust-lang.org/1.39.0/std/io/type.Result.html)。

你如何知道它是哪一个？由于 `Result` 是一个 `enum`，你可以使用 `match` 来检查它是哪个变体：

```rust
#![allow(unused)]
fn main() {
let result = std::fs::read_to_string("test.txt");
match result {
    Ok(content) => { println!("文件内容: {}", content); }
    Err(error) => { println!("糟糕：{}", error); }
}
}
```

**注意**：不确定什么是枚举或它们在 Rust 中如何工作？[查看 Rust 书籍的这一章](https://doc.rust-lang.org/1.39.0/book/ch06-00-enums.html) 以快速上手。

## [解包](#unwrapping)

现在，我们能够访问文件的内容，但在 `match` 块之后，我们无法真正使用它。为此，我们需要处理错误情况。虽然 `match` 块的所有分支都必须返回相同类型的值是一个挑战，但有一个巧妙的技巧可以绕过它：

```rust
#![allow(unused)]
fn main() {
let result = std::fs::read_to_string("test.txt");
let content = match result {
    Ok(content) => { content },
    Err(error) => { panic!("无法处理 {}, 直接在此处退出", error); }
};
println!("文件内容: {}", content);
}
```

我们可以在 `match` 块之后使用 `content` 中的字符串，但如果 `result` 是一个错误，字符串将不存在。这没关系，因为程序会在到达使用 `content` 的点之前退出。

这看起来可能很极端，但非常方便。如果你的程序需要读取该文件，而文件不存在时无法做任何事情，退出是一种有效的策略。甚至有一个在 [`Result`](https://doc.rust-lang.org/1.39.0/std/result/index.html) 上的快捷方法叫做 `unwrap`：

```rust
#![allow(unused)]
fn main() {
let content = std::fs::read_to_string("test.txt").unwrap();
}
```

## [无需恐慌](#no-need-to-panic)

当然，中止程序并不是处理错误的唯一方式。与其使用 `panic!`，我们可以直接使用 `return`：

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
let result = std::fs::read_to_string("test.txt");
let content = match result {
    Ok(content) => { content },
    Err(error) => { return Err(error.into()); }
};
Ok(())
}
```

然而，这改变了我们函数的返回类型。我们之前的示例中隐藏了一些东西：这段代码所在的函数签名。而在最后一个使用 `return` 的示例中，这一点变得很重要。以下是 *完整* 的示例：

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let result = std::fs::read_to_string("test.txt");
    let content = match result {
        Ok(content) => { content },
        Err(error) => { return Err(error.into()); }
    };
    println!("文件内容: {}", content);
    Ok(())
}
```

我们的返回类型是一个 `Result`！这就是为什么我们可以在第二个 `match` 分支中写 `return Err(error);`。看到底部的 `Ok(())` 了吗？它是函数的默认返回值，意思是：“结果正常，且无内容”。

**注意**：为什么不写成 `return Ok(());`？它完全可以这样写——这完全有效。Rust 中任何块的最后一个表达式就是其返回值，通常省略不必要的 `return`。

## [问号](#question-mark)

就像调用 `.unwrap()` 是带有 `panic!` 错误分支的 `match` 的快捷方式一样，我们还有一个用于在错误分支中 `return` 的 `match` 的快捷方式：`?`。

没错，一个问号。你可以将此运算符附加到 `Result` 类型的值上，Rust 将在内部将其扩展为与我们刚刚编写的 `match` 非常相似的代码。

试试看：

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let content = std::fs::read_to_string("test.txt")?;
    println!("文件内容: {}", content);
    Ok(())
}
```

非常简洁！

**注意**：这里还有一些其他事情发生，但理解这些并非必须。例如，我们 `main` 函数中的错误类型是 `Box<dyn std::error::Error>`，但我们上面看到 `read_to_string` 返回的是 [`std::io::Error`](https://doc.rust-lang.org/1.39.0/std/io/type.Result.html)。这是因为 `?` 扩展为代码，将错误类型 *转换* 为。

`Box<dyn std::error::Error>` 也是一个有趣的类型。它是一个可以包含 *任何* 实现标准 [`Error`](https://doc.rust-lang.org/1.39.0/std/error/trait.Error.html) 特征的类型的 `Box`。这意味着所有错误都可以放入此框中，我们可以在所有返回 `Result` 的常用函数上使用 `?`。

## [提供上下文](#providing-context)

当你在 `main` 函数中使用 `?` 时，你得到的错误信息尚可，但不够好。例如，当你运行 `std::fs::read_to_string("test.txt")?` 且文件 `test.txt` 不存在时，你会得到这个输出：

```text
错误：Os { code: 2, kind: NotFound, message: "没有这样的文件或目录" }
```

在你的代码实际上不包含文件名的情况下，很难判断哪个文件是 `NotFound`。有多种方法可以解决这个问题。

一种方法是创建我们自己的错误类型，并使用它来构建自定义错误消息：

```rust
#[derive(Debug)]
struct CustomError(String);

fn main() -> Result<(), CustomError> {
    let path = "test.txt";
    let content = std::fs::read_to_string(path)
        .map_err(|err| CustomError(format!("读取 `{}` 时出错：{}", path, err)))?;
    println!("文件内容: {}", content);
    Ok(())
}
```

运行此代码，我们将获得自定义错误消息：

```text
错误：CustomError("读取 `test.txt` 时出错：没有这样的文件或目录（操作系统错误 2）")
```

不太美观，但我们稍后可以调整我们类型的调试输出。

这种模式非常常见。但它有一个问题：我们不存储原始错误，只存储其字符串表示。流行的 [`anyhow`](https://docs.rs/anyhow) 库对此有一个巧妙的解决方案：其 [`Context`](https://docs.rs/anyhow/1.0/anyhow/trait.Context.html) 特征可用于添加类似于我们 `CustomError` 类型的描述。此外，它保留了原始错误，因此我们获得了一个指向根本原因的“错误链”。

首先，通过在 `Cargo.toml` 文件的 `[dependencies]` 部分添加 `anyhow = "1.0"` 来导入 `anyhow` crate。

完整的示例如下：

```rust
use anyhow::{Context, Result};

fn main() -> Result<()> {
    let path = "test.txt";
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("无法读取文件 `{}`", path))?;
    println!("文件内容: {}", content);
    Ok(())
}
```

这将打印一个错误：

```text
错误：无法读取文件 `test.txt`

原因：
    没有这样的文件或目录（操作系统错误 2）
```

## [总结](#wrapping-up)

你的代码现在应如下所示：

```rust
use anyhow::{Context, Result};
use clap::Parser;

/// 在文件中搜索模式并显示包含它的行。
#[derive(Parser)]
struct Cli {
    /// 要查找的模式
    pattern: String,
    /// 要读取的文件路径
    path: std::path::PathBuf,
}

fn main() -> Result<()> {
    let args = Cli::parse();

    let content = std::fs::read_to_string(&args.path)
        .with_context(|| format!("无法读取文件 `{}`", args.path.display()))?;

    for line in content.lines() {
        if line.contains(&args.pattern) {
            println!("{}", line);
        }
    }

    Ok(())
}
```

# 输出

## [打印“Hello World”](#printing-hello-world)

```rust
#![allow(unused)]
fn main() {
println!("Hello World");
}
```

很简单，太好了！进入下一个主题。

## [使用 `println!`](#using-println)

你可以使用 `println!` 宏打印几乎所有你想要的内容。这个宏具有相当惊人的功能，但也具有特殊的语法。它期望第一个参数是一个包含占位符的字符串字面量。字符串将由后续参数的值填充。

例如：

```rust
#![allow(unused)]
fn main() {
let x = 42;
println!("我的幸运数字是 {}。", x);
}
```

将打印：

```console
我的幸运数字是 42。
```

上面字符串中的花括号（`{}`）是这些占位符之一。这是默认的占位符类型，尝试以人类可读的方式打印给定值。对于数字和字符串，这非常有效，但并非所有类型都能做到这一点。这就是为什么还有一个“调试表示”，你可以通过像这样填充占位符的花括号来获取：`{:?}`。

例如：

```rust
#![allow(unused)]
fn main() {
let xs = vec![1, 2, 3];
println!("列表是: {:?}", xs);
}
```

将打印：

```console
列表是: [1, 2, 3]
```

如果你希望自己的数据类型可用于调试和日志记录，你通常可以在其定义上方添加 `#[derive(Debug)]`。

**注意**：“用户友好”的打印使用 [`Display`](https://doc.rust-lang.org/1.39.0/std/fmt/trait.Display.html) 特征，而调试输出（人类可读但面向开发人员）使用 [`Debug`](https://doc.rust-lang.org/1.39.0/std/fmt/trait.Debug.html) 特征。你可以在 [`std::fmt` 模块的文档](https://doc.rust-lang.org/1.39.0/std/fmt/index.html) 中找到有关 `println!` 中可以使用的语法的更多信息。

## [打印错误](#printing-errors)

打印错误应通过 `stderr` 进行，以便用户和其他工具更容易将它们的输出重定向到文件或其他工具。

**注意**：在大多数操作系统上，程序可以写入两个输出流：`stdout` 和 `stderr`。`stdout` 用于程序的实际输出，而 `stderr` 允许将错误和其他消息与 `stdout` 分开。这样，输出可以存储到文件或管道到另一个程序，而错误则显示给用户。

在 Rust 中，这是通过 `println!` 和 `eprintln!` 实现的，前者打印到 `stdout`，后者打印到 `stderr`。

```rust
#![allow(unused)]
fn main() {
println!("这是信息");
eprintln!("这是错误！:(");
}
```

**注意**：打印 [转义码](https://en.wikipedia.org/wiki/ANSI_escape_code) 可能很危险，并会使用户的终端进入奇怪的状态。手动打印它们时务必小心！

理想情况下，处理原始转义码时，应使用像 `ansi_term` 这样的 crate，以使你和用户的生活更轻松。

## [关于打印性能的说明](#a-note-on-printing-performance)

打印到终端出人意料地慢！如果你在循环中调用像 `println!` 这样的函数，它很容易成为快速程序中的瓶颈。为了加快速度，你可以做两件事。

首先，你可能希望减少实际“刷新”到终端的写入次数。`println!` 每次都会告诉系统刷新到终端，因为通常每打印一行都需要这样做。如果你不需要这样，你可以将 `stdout` 句柄包装在 [`BufWriter`](https://doc.rust-lang.org/1.39.0/std/io/struct.BufWriter.html) 中，它默认缓冲最多 8 kB。当你希望立即打印时，你仍然可以调用此 `BufWriter` 上的 `.flush()`。

```rust
#![allow(unused)]
fn main() {
use std::io::{self, Write};

let stdout = io::stdout(); // 获取全局 stdout 实体
let mut handle = io::BufWriter::new(stdout); // 可选：将该句柄包装在缓冲区中
writeln!(handle, "foo: {}", 42); // 如果你关心错误，请添加 `?`
}
```

其次，获取 `stdout`（或 `stderr`）的锁并直接使用 `writeln!` 打印到它，这很有帮助。这防止了系统反复锁定和解锁 `stdout`。

```rust
#![allow(unused)]
fn main() {
use std::io::{self, Write};

let stdout = io::stdout(); // 获取全局 stdout 实体
let mut handle = stdout.lock(); // 获取它的锁
writeln!(handle, "foo: {}", 42); // 如果你关心错误，请添加 `?`
}
```

你也可以结合这两种方法。

## [显示进度条](#showing-a-progress-bar)

一些 CLI 应用程序运行不到一秒，而另一些则需要几分钟甚至几小时。如果你正在编写后一类程序，你可能希望向用户显示某些事情正在发生。为此，你应该尝试打印有用的进度更新，最好以易于消费的形式。

使用 [indicatif](https://crates.io/crates/indicatif) crate，你可以为你的程序添加进度条和小旋转器。这是一个快速示例：

```rust
fn main() {
    let pb = indicatif::ProgressBar::new(100);
    for i in 0..100 {
        do_hard_work();
        pb.println(format!("[+] 完成 #{}", i));
        pb.inc(1);
    }
    pb.finish_with_message("完成");
}
```

有关更多信息，请参阅 [文档](https://docs.rs/indicatif) 和 [示例](https://github.com/console-rs/indicatif/tree/main/examples)。

## [日志记录](#logging)

为了更容易理解我们的程序中发生了什么，我们可能希望添加一些日志语句。这在编写应用程序时通常很容易，并且在半年后再次运行此程序时会变得非常有帮助。在某种程度上，日志记录与使用 `println!` 相同，只是你可以指定消息的重要性。你可以使用的级别通常是 *error*、*warn*、*info*、*debug* 和 *trace*（*error* 优先级最高，*trace* 最低）。

要为你的应用程序添加简单的日志记录，你需要两样东西：[log](https://crates.io/crates/log) crate（它包含按日志级别命名的宏）和一个实际将日志输出写入有用位置的 *适配器*。能够使用日志适配器非常灵活：例如，你可以使用它们将日志不仅写入终端，还写入 [syslog](https://en.wikipedia.org/wiki/Syslog) 或中央日志服务器。

由于我们只关注编写 CLI 应用程序，一个简单的适配器是 [env_logger](https://crates.io/crates/env_logger)。它被称为“env”日志，因为你可以使用环境变量来指定你想记录应用程序的哪些部分以及以哪个级别记录。它会用时间戳和日志消息来源的模块前缀你的日志消息。由于库也可以使用 `log`，你可以轻松配置它们的日志输出。

这里是一个快速示例：

```rust
use log::{info, warn};

fn main() {
    env_logger::init();
    info!("启动中");
    warn!("哦，没有实现任何内容！");
}
```

假设你将此文件作为 `src/bin/output-log.rs`，在 Linux 和 macOS 上，你可以像这样运行它：

```console
$ env RUST_LOG=info cargo run --bin output-log
    Finished dev [unoptimized + debuginfo] target(s) in 0.17s
     Running `target/debug/output-log`
[2018-11-30T20:25:52Z INFO  output_log] 启动中
[2018-11-30T20:25:52Z WARN  output_log] 哦，没有实现任何内容！
```

在 Windows PowerShell 中，你可以像这样运行它：

```console
$ $env:RUST_LOG="info"
$ cargo run --bin output-log
    Finished dev [unoptimized + debuginfo] target(s) in 0.17s
     Running `target/debug/output-log.exe`
[2018-11-30T20:25:52Z INFO  output_log] 启动中
[2018-11-30T20:25:52Z WARN  output_log] 哦，没有实现任何内容！
```

在 Windows CMD 中，你可以像这样运行它：

```console
$ set RUST_LOG=info
$ cargo run --bin output-log
    Finished dev [unoptimized + debuginfo] target(s) in 0.17s
     Running `target/debug/output-log.exe`
[2018-11-30T20:25:52Z INFO  output_log] 启动中
[2018-11-30T20:25:52Z WARN  output_log] 哦，没有实现任何内容！
```

`RUST_LOG` 是你可以用来设置日志设置的环境变量名称。`env_logger` 还包含一个构建器，因此你可以以编程方式调整这些设置，例如默认显示 *info* 级别的消息。

还有许多其他日志适配器以及 `log` 的替代品和扩展。如果你知道你的应用程序将有大量日志，确保审查它们并让你的用户生活更轻松。

**提示**：经验表明，即使是稍微有用的 CLI 程序也可能被使用多年，尤其是如果它们原本是作为临时解决方案设计的。如果您的应用程序出现问题，而某人（例如未来的你）需要弄清楚原因，能够传递 `--verbose` 来获取额外的日志输出，可能会在调试时间上节省几分钟甚至几小时。[clap-verbosity-flag](https://crates.io/crates/clap-verbosity-flag) crate 提供了一种快速方式，为使用 `clap` 的项目添加 `--verbose`。

# 测试

数十年的软件开发中，人们发现了一个真理：未经测试的软件很少能正常工作。许多人甚至会说，大多数经过测试的软件也不起作用。但我们都乐观，对吧？为确保你的程序按预期工作，测试它是明智的。

一个好的起点是编写一个 `README` 文件，描述你的程序应该做什么，当你准备发布新版本时，回顾 `README` 并确保行为仍然如预期。你可以通过写下你的程序应如何响应错误输入来使这一过程更严谨。

这里有一个更酷的想法：在编写代码之前先写那个 `README`。

**注意**：如果你还不了解 [测试驱动开发](https://en.wikipedia.org/wiki/Test-driven_development)（TDD），请查看一下。

## [自动化测试](#automated-testing)

这都很好，但手动做所有这些？这可能需要大量时间。同时，许多人喜欢让计算机替他们做事。让我们谈谈如何自动化这些测试。

Rust 有一个内置的测试框架，所以让我们从编写第一个测试开始：

```rust
fn answer() -> i32 {
  42
}

#[test]
fn check_answer_validity() {
    assert_eq!(answer(), 42);
}
```

你可以将此代码片段放在包中的几乎任何源文件中，`cargo test` 将找到并运行它。关键在于 `#[test]` 属性。它允许构建系统发现此类函数并将其作为测试运行，验证它们不会恐慌。

**读者练习**：使此测试生效。

你应该最终得到如下输出：

```text
运行 1 个测试
test check_answer_validity ... ok

测试结果：ok。1 通过；0 失败；0 忽略；0 测量；0 过滤
```

现在我们已经看到了 *如何* 编写测试，我们仍然需要弄清楚 *测试什么*。正如你所见，为函数编写断言只需很少的代码，但 CLI 应用程序通常不止一个函数！更糟的是，它通常处理用户输入、读取文件和写入输出。

## [使你的代码可测试](#making-your-code-testable)

有两种互补的方法来测试功能。一种是测试构建完整应用程序所使用的小单元。这些被称为“单元测试”。另一种是从外部测试最终应用程序，称为黑盒测试或集成测试。让我们从第一种开始。

为了弄清楚我们应该测试什么，让我们看看我们的程序功能。`grrs` 应该打印出匹配给定模式的行，因此让我们为 *这* 编写单元测试。我们希望确保我们最重要的逻辑部分正常工作，并且我们以不依赖任何周围设置代码（如 CLI 参数）的方式进行。

回到我们的 [初步实现](impl-draft.html) 中的 `grrs`，我们在 `main` 函数中添加了这段代码：

```rust
// ...
for line in content.lines() {
    if line.contains(&args.pattern) {
        println!("{}", line);
    }
}
```

不幸的是，这不容易测试。首先，它在主函数中，所以我们不能轻易调用它。通过将此代码段移动到一个函数中来解决这个问题：

```rust
#![allow(unused)]
fn main() {
fn find_matches(content: &str, pattern: &str) {
    for line in content.lines() {
        if line.contains(pattern) {
            println!("{}", line);
        }
    }
}
}
```

现在，我们可以在测试中调用这个函数并查看它的输出：

```rust
#[test]
fn find_a_match() {
    find_matches("lorem ipsum\ndolor sit amet", "lorem");
    assert_eq!( // 呃
```

或者…我们可以吗？目前，`find_matches` 直接打印到 `stdout`，即终端。我们无法在测试中轻松捕获它！这是一个在实现后编写测试时经常出现的问题：我们编写了一个紧密集成在其使用上下文中的函数。

**注意**：在编写小型 CLI 应用程序时，这完全没问题。没有必要使所有内容都可测试！重要的是思考你可能希望为哪些部分编写单元测试。虽然我们会看到，使这个函数可测试很简单，但这并不总是如此。

好吧，我们如何使它可测试？我们需要以某种方式捕获输出。Rust 的标准库有一些用于处理 I/O（输入/输出）的出色抽象，我们将使用一个名为 [`std::io::Write`](https://doc.rust-lang.org/1.39.0/std/io/trait.Write.html) 的抽象。这是一个 [特征](https://doc.rust-lang.org/book/ch10-02-traits.html)，它抽象了我们可以写入的东西，包括字符串和 `stdout`。

如果你第一次在 Rust 的上下文中听到“特征”，你将有惊喜。特征是 Rust 最强大的功能之一。你可以将它们视为 Java 中的接口或 Haskell 中的类型类，无论你更熟悉哪个。它们允许你抽象不同类型的共享行为。使用特征的代码可以以非常通用和灵活的方式表达思想。这意味着它也可能难以阅读。不要被吓倒。即使使用 Rust 多年的人也不总是立即理解泛型代码。在这种情况下，考虑具体用法会有帮助。在我们的情况下，我们抽象的行为是“写入它”。实现 (`impl`) 它的类型示例包括终端的标准输出、文件、内存中的缓冲区或 TCP 网络连接。向下滚动 [std::io::Write 的文档](https://doc.rust-lang.org/1.39.0/std/io/trait.Write.html) 以查看“实现者”列表。

有了这些知识，让我们更改我们的函数以接受第三个参数。它可以是任何实现 `Write` 的类型。这样，我们可以在测试中提供一个简单的字符串并对其断言。这是我们如何编写这个版本的 `find_matches`：

```rust
fn find_matches(content: &str, pattern: &str, mut writer: impl std::io::Write) {
    for line in content.lines() {
        if line.contains(pattern) {
            writeln!(writer, "{}", line);
        }
    }
}
```

新参数是 `mut writer`，即我们称之为“写入器”的可变东西。它的类型是 `impl std::io::Write`，你可以将其读作任何实现 `Write` 特征的类型的占位符。注意我们如何用 `writeln!(writer, …)` 替换了之前使用的 `println!(…)`。`println!` 与 `writeln!` 工作方式相同，但它总是使用标准输出。

现在，我们可以测试输出：

```rust
#[test]
fn find_a_match() {
    let mut result = Vec::new();
    find_matches("lorem ipsum\ndolor sit amet", "lorem", &mut result);
    assert_eq!(result, b"lorem ipsum\n");
}
```

要在我们的应用程序代码中使用它，我们必须通过添加 [`&mut std::io::stdout()`](https://doc.rust-lang.org/1.39.0/std/io/fn.stdout.html) 作为第三个参数来更改 `main` 中对 `find_matches` 的调用。以下是基于我们前面章节所见并使用我们提取的 `find_matches` 函数的 `main` 函数示例：

```rust
fn main() -> Result<()> {
    let args = Cli::parse();
    let content = std::fs::read_to_string(&args.path)
        .with_context(|| format!("无法读取文件 `{}`", args.path.display()))?;

    find_matches(&content, &args.pattern, &mut std::io::stdout());

    Ok(())
}
```

**注意**：由于 `stdout` 期望字节（而非字符串），我们使用 `std::io::Write` 而不是 `std::fmt::Write`。因此，我们在测试中使用空向量作为 `writer`（其类型将被推断为 `Vec<u8>`），并在 `assert_eq!` 中使用 `b"foo"`。`b` 前缀使其成为 *字节字符串字面量*，因此其类型将是 `&[u8]` 而不是 `&str`。

**注意**：我们也可以让这个函数返回一个 `String`，但这会改变其行为。它不会直接写入终端，而是将所有内容收集到一个字符串中，并在最后一次性全部输出。

**读者练习**：[`writeln!`](https://doc.rust-lang.org/1.39.0/std/macro.writeln.html) 返回一个 [`io::Result`](https://doc.rust-lang.org/1.39.0/std/io/type.Result.html)，因为写入可能失败（例如，当缓冲区已满且无法扩展时）。为 `find_matches` 添加错误处理。

我们刚刚看到了如何使这段代码可测试。我们有：

1. 识别了我们应用程序的一个核心部分。
2. 将其放入自己的函数中。
3. 使其更具灵活性。

尽管目标是使其可测试，但最终结果实际上是一个非常地道且可重用的 Rust 代码。太棒了！

## [将你的代码拆分为库和二进制目标](#splitting-your-code-into-library-and-binary-targets)

我们可以在这里再做一件事。到目前为止，我们将所有内容都放在 `src/main.rs` 文件中。这意味着我们当前的项目生成一个单一的二进制文件，但我们也可以像这样使我们的代码作为库可用：

1. 将 `find_matches` 函数放入新的 `src/lib.rs`。
2. 在 `fn` 前添加 `pub`，使其成为我们的库用户可以访问的内容（即 `pub fn find_matches`）。
3. 从 `src/main.rs` 中删除 `find_matches`。
4. 在 `fn main` 中，将对 `find_matches` 的调用前缀为 `grrs::`，使其现在为 `grrs::find_matches(…)`。这意味着它使用我们刚刚编写的库中的函数！

Rust 处理项目的方式非常灵活，尽早考虑将什么放入你的 crate 的库部分是个好主意。例如，你可以考虑首先为你的应用程序特定逻辑编写一个库，然后像使用任何其他库一样在你的 CLI 中使用它。或者，如果你的项目有多个二进制文件，你可以将公共功能放入该 crate 的库部分。

**注意**：说到将所有内容放入 `src/main.rs`，如果我们继续这样做，它将变得难以阅读。[模块系统](https://doc.rust-lang.org/1.39.0/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html) 可以帮助你结构化和组织你的代码。

## [通过运行它们来测试 CLI 应用程序](#testing-cli-applications-by-running-them)

到目前为止，我们费尽心思测试了我们应用程序的 *业务逻辑*，结果是 `find_matches` 函数。这非常有价值，是良好测试代码库的良好第一步。通常，这些类型的测试称为“单元测试”。

我们没有测试大量代码：所有处理外部世界的代码！想象一下你写了主函数，但不小心保留了一个硬编码的字符串而不是使用用户提供的路径参数。我们也应该为这些编写测试！这种级别的测试通常称为集成测试或系统测试。

在核心上，我们仍然在编写函数并用 `#[test]` 注释它们。这只是这些函数内部内容的问题。例如，我们将希望使用我们项目的主二进制文件并像运行常规程序一样运行它。我们将把这些测试放入新目录中的新文件中：`tests/cli.rs`。

**注意**：按照惯例，`cargo` 将在 `tests/` 目录中查找集成测试。同样，它将在 `benches/` 中查找基准测试，在 `examples/` 中查找示例。这些惯例也扩展到你的主源代码：库有 `src/lib.rs` 文件，主二进制文件是 `src/main.rs`，如果有多个二进制文件，cargo 期望它们位于 `src/bin/<name>.rs`。遵循这些惯例将使你的代码库对熟悉阅读 Rust 代码的人更具可发现性。

`grrs` 是一个小型工具，用于在文件中搜索字符串。我们已经测试了我们可以找到匹配项。让我们思考一下我们还可以测试哪些其他功能。

这是我想到的：

- 当文件不存在时会发生什么？
- 当没有匹配项时输出是什么？
- 当我们忘记一个（或两个）参数时，我们的程序是否以错误退出？

这些都是有效的测试用例。此外，我们还应包含一个关于“幸福路径”的测试用例：我们找到了至少一个匹配项并打印了它。

为了使这些类型的测试更容易，我们将使用 [`assert_cmd`](https://docs.rs/assert_cmd) crate。它具有一系列有用的辅助工具，允许我们运行我们的主二进制文件并查看其行为。我们还将添加 [`predicates`](https://docs.rs/predicates) crate，它有助于编写 `assert_cmd` 可以测试的断言，并具有出色的错误消息。我们不会将这些依赖项添加到主列表中，而是添加到 `Cargo.toml` 的 `dev dependencies` 部分。它们仅在开发 crate 时需要，而不是在使用它时。

```toml
[dev-dependencies]
assert_cmd = "2.0.14"
predicates = "3.1.0"
```

这听起来像是很多设置。尽管如此，让我们直接进入并创建我们的 `tests/cli.rs` 文件：

```rust
use assert_cmd::cargo::*; // 导入 cargo_bin_cmd! 宏和方法
use predicates::prelude::*; // 用于编写断言

#[test]
fn file_doesnt_exist() -> Result<(), Box<dyn std::error::Error>> {
    let mut cmd = cargo_bin_cmd!("grrs");

    cmd.arg("foobar").arg("test/file/doesnt/exist");
    cmd.assert()
        .failure()
        .stderr(predicate::str::contains("无法读取文件"));

    Ok(())
}
```

你可以像上面编写的测试一样使用 `cargo test` 运行此测试。第一次运行时可能会花一点时间，因为 `Command::cargo_bin("grrs")` 需要编译你的主二进制文件。

## [生成测试文件](#generating-test-files)

我们刚刚看到的测试只检查当输入文件不存在时我们的程序是否写入错误消息。这是一个重要的测试，但可能不是最重要的。让我们测试我们实际上会打印在文件中找到的匹配项！

我们需要有一个我们知道内容的文件，这样我们才能知道我们的程序 *应该* 返回什么，并在代码中检查这个期望。一个想法可能是向项目添加一个具有自定义内容的文件并在我们的测试中使用它。另一个是在我们的测试中创建临时文件。对于本教程，我们将研究后者。它更灵活，适用于其他情况；例如，当你测试更改文件的程序时。

为了创建这些临时文件，我们将使用 [`assert_fs`](https://docs.rs/assert_fs) crate。让我们将其添加到我们的 `Cargo.toml` 的 `dev-dependencies` 中：

```toml
assert_fs = "1.1.1"
```

这是一个新的测试用例，它创建一个临时文件（一个“命名”文件以便我们可以获取其路径），用一些文本填充它，然后运行我们的程序以查看我们是否获得正确的输出。你可以将其写在其他测试用例下面。当变量 `file` 在函数结束时超出作用域时，实际的临时文件将自动删除。

```rust
#[test]
fn find_content_in_file() -> Result<(), Box<dyn std::error::Error>> {
    let file = assert_fs::NamedTempFile::new("sample.txt")?;
    file.write_str("A test\nActual content\nMore content\nAnother test")?;

    let mut cmd = cargo_bin_cmd!("grrs");
    cmd.arg("test").arg(file.path());
    cmd.assert()
        .success()
        .stdout(predicate::str::contains("A test\nAnother test"));

    Ok(())
}
```

**读者练习**：添加将空字符串作为模式传递的集成测试。根据需要调整程序。

## [测试什么？](#what-to-test)

虽然编写集成测试当然很有趣，但编写和更新它们需要一些时间，尤其是在你的应用程序行为发生变化时。为确保你明智地使用时间，你应该问自己应该测试什么。

一般来说，为用户可以观察到的所有类型行为编写集成测试是个好主意。这意味着你不需要覆盖所有边缘情况。通常，拥有不同类型的示例就足够了，并依赖单元测试来覆盖边缘情况。

同样，最好不要将测试集中在那些你无法主动控制的事情上。测试 `--help` 的确切布局将是个坏主意，因为它是由你生成的。相反，你可能只想检查某些元素是否存在。

根据你的程序性质，你还可以尝试添加更多测试技术。例如，如果你提取了程序的部分并发现自己在编写大量示例用例作为单元测试，同时试图想出所有边缘情况，你应该看看 [`proptest`](https://docs.rs/proptest)。如果你有一个消耗任意文件并解析它们的程序，尝试编写一个 [模糊测试器](https://rust-fuzz.github.io/book/introduction.html) 来寻找边缘情况中的错误。

**注意**：你可以在 [本书的仓库](https://github.com/rust-cli/book/tree/master/src/tutorial/testing) 中找到本章使用的完整、可运行的源代码。

# 打包和分发 Rust 工具

如果你对自己的程序准备好让其他人使用感到自信，是时候打包和发布了！

有几种方法，我们将从最简单设置到对用户最方便的三种方法来看。

## [最快：`cargo publish`](#quickest-cargo-publish)

发布你的应用程序最简单的方法是使用 cargo。你还记得我们如何向项目添加外部依赖项吗？Cargo 从其默认的 crate 注册表 [crates.io](https://crates.io/) 下载它们。通过 `cargo publish`，你可以将 crate 发布到 [crates.io](https://crates.io/)，这对所有 crate 都适用，包括具有二进制目标的 crate。

将 crate 发布到 [crates.io](https://crates.io/) 可以通过几个步骤完成。首先，如果你还没有，创建一个 [crates.io](https://crates.io/) 账户，这是通过授权你使用 GitHub 完成的，因此你需要有一个 GitHub 账户并登录在那里。其次，你使用 cargo 在本地机器上登录。为此，前往你的 [crates.io 账户页面](https://crates.io/me)，创建一个新令牌，并运行 `cargo login <your-new-token>`。你每台计算机只需这样做一次。你可以在 cargo 的 [发布指南](https://doc.rust-lang.org/1.39.0/cargo/reference/publishing.html) 中了解更多关于此的信息。

现在，cargo 和 crates.io 都认识你，你就可以发布 crate 了。在匆忙发布新版本之前，最好再次打开你的 `Cargo.toml` 并确保你添加了必要的元数据。你可以在 [cargo 清单格式的文档](https://doc.rust-lang.org/1.39.0/cargo/reference/manifest.html) 中找到所有可以设置的字段。这里是一些常见条目的快速概述：

```toml
[package]
name = "grrs"
version = "0.1.0"
authors = ["你的名字 <your@email.com>"]
license = "MIT OR Apache-2.0"
description = "一个搜索文件的工具"
readme = "README.md"
homepage = "https://github.com/you/grrs"
repository = "https://github.com/you/grrs"
keywords = ["cli", "search", "demo"]
categories = ["command-line-utilities"]
```

**注意**：此示例包括强制性的 license 字段，这是 Rust 项目的一个常见选择：与编译器本身使用的相同许可证。它还引用了一个 `README.md` 文件。它应包含关于你的项目是什么的简短描述，并且不仅包含在 crates.io 上你的 crate 页面上，GitHub 也会在存储库页面上默认显示它。

### [如何从 crates.io 安装二进制文件](#how-to-install-a-binary-from-cratesio)

我们已经看到了如何将 crate 发布到 crates.io，你可能会想知道如何安装它。与库不同，cargo 在你运行 `cargo build` 或类似命令时会为你下载并编译，你需要明确告诉它安装二进制文件。

这是通过 `cargo install <crate-name>` 完成的。它将默认下载 crate，编译其中包含的所有二进制目标（以“发布”模式，因此可能需要一些时间），并将它们复制到 `~/.cargo/bin/` 目录中。确保你的 shell 知道在此处查找二进制文件！

还可以从 git 仓库安装 crate，仅安装特定的二进制文件，并指定安装它们的替代目录。有关详细信息，请参阅 `cargo install --help`。

### [何时使用它](#when-to-use-it)

`cargo install` 是安装二进制 crate 的简单方法。它对 Rust 开发者非常方便，但有一些显著的缺点：由于它总是从源代码重新编译，你的工具的用户需要在他们的机器上安装 Rust、cargo 和项目所需的所有其他系统依赖项。编译大型 Rust 代码库可能需要一些时间。

最好将它用于分发面向其他 Rust 开发者的工具。例如，许多 cargo 子命令如 `cargo-tree` 或 `cargo-outdated` 可以用它安装。

## [分发二进制文件](#distributing-binaries)

Rust 是一种编译为原生代码的语言，默认情况下静态链接所有依赖项。当你在包含名为 `grrs` 的二进制文件的项目上运行 `cargo build` 时，你会得到一个名为 `grrs` 的二进制文件。试试看！使用 `cargo build`，它将是 `target/debug/grrs`，当你运行 `cargo build --release` 时，它将是 `target/release/grrs`。除非你使用明确需要在目标系统上安装外部库的 crate（如使用系统版本的 OpenSSL），否则这个二进制文件只依赖于常见的系统库。这意味着，你取这个文件，发送给运行与你相同操作系统的用户，他们就可以运行它。

这已经非常强大了！它绕过了我们刚刚看到的 `cargo install` 的两个缺点：用户不需要在他们的机器上安装 Rust，而且不需要花费一分钟编译，他们可以立即运行二进制文件。

正如我们所见，`cargo build` *已经* 为我们构建了二进制文件。问题是这些二进制文件并不能保证在所有平台上都能工作。如果你在 Windows 机器上运行 `cargo build`，你不会得到一个在 Mac 上工作的二进制文件。有没有办法自动为所有目标平台生成这些二进制文件？

### [在 CI 上构建二进制发布](#building-binary-releases-on-ci)

如果你的工具是开源的并托管在 GitHub 上，设置一个免费的 CI（持续集成）服务如 [Travis CI](https://travis-ci.com/) 是相当容易的。还有其他提供此功能的服务，但 Travis 非常流行。每次你向你的仓库推送更改时，它都会在虚拟机中运行设置命令。这些命令是什么，以及它们运行的机器类型，都是可配置的。例如，一个好的想法是在安装了 Rust 和一些常见构建工具的机器上运行 `cargo test`。如果失败了，你就知道最近的更改有问题。

我们也可以用它来构建二进制文件并上传到 GitHub！如果我们运行 `cargo build --release` 并将二进制文件上传到某处，我们就完成了，对吧？还不完全是。我们仍然需要确保我们构建的二进制文件尽可能与许多系统兼容。例如，在 Linux 上，我们可以为当前系统或 `x86_64-unknown-linux-musl` 目标编译，而不依赖默认系统库。在 macOS 上，我们可以将 `MACOSX_DEPLOYMENT_TARGET` 设置为 `10.7`，以便只依赖 10.7 及更早版本中存在的系统功能。

你可以在这里看到使用此方法构建二进制文件的一个示例：[Linux 和 macOS](https://github.com/rustwasm/wasm-pack/blob/51e6351c28fbd40745719e6d4a7bf26dadd30c85/.travis.yml#L74-L91) 和 [Windows 使用 AppVeyor](https://github.com/rustwasm/wasm-pack/blob/51e6351c28fbd40745719e6d4a7bf26dadd30c85/.appveyor.yml)。

另一种方法是使用预构建的（即 Docker）镜像，其中包含我们构建二进制文件所需的所有工具。这使我们能够轻松针对更多奇特的平台。[trust](https://github.com/japaric/trust) 项目包含你可以包含在项目中的脚本以及如何设置的说明。它还包括使用 AppVeyor 的 Windows 支持。

如果你更愿意在本地设置并在自己的机器上生成发布文件，请查看 [trust](https://github.com/japaric/trust)。它内部使用 [cross](https://github.com/rust-embedded/cross)，它的工作方式类似于 cargo，但将命令转发到 Docker 容器内的 cargo 进程。图像的定义也可以在 [cross 的仓库](https://github.com/rust-embedded/cross) 中找到。

### [如何安装这些二进制文件](#how-to-install-these-binaries)

你将你的用户指向你的发布页面，它可能看起来像 [这个](https://github.com/rustwasm/wasm-pack/releases/tag/v0.5.1)，他们可以下载我们刚刚创建的工件。我们生成的发布工件没什么特别的。它们只是包含我们二进制文件的归档文件！这意味着你的工具的用户可以用他们的浏览器下载它们，提取它们（通常自动），并将二进制文件复制到他们喜欢的地方。

这需要一些手动安装程序的经验，因此你希望在 README 文件中添加一个部分，说明如何安装此程序。

**注意**：如果你使用 [trust](https://github.com/japaric/trust) 构建你的二进制文件并将它们添加到 GitHub 发布中，你也可以告诉人们运行 `curl -LSfs https://japaric.github.io/trust/install.sh | sh -s -- --git your-name/repo-name`，如果你认为这更容易。

### [何时使用它](#when-to-use-it-1)

拥有二进制发布是一个好主意。几乎没有缺点。它没有解决用户必须手动安装和更新你的工具的问题，但他们可以快速获取最新版本，而无需安装 Rust。

### [除了二进制文件之外，还打包什么](#what-to-package-in-addition-to-your-binaries)

现在，当用户下载我们的发布版本时，他们将得到一个 `.tar.gz` 文件，其中仅包含二进制文件。在我们的示例项目中，他们将只得到一个可以运行的 `grrs` 文件，但还有更多我们已经在仓库中的文件，他们可能想要。例如，README 文件告诉他们如何使用这个工具和许可证文件。既然我们已经有了它们，添加它们很容易。

还有更多有趣的文件有意义，特别是对于命令行工具。我们为什么不除了 README 文件外还提供一个手册页和为你的 shell 添加可能标志的补全的配置文件？你可以手动编写这些，但 *clap*，我们使用的参数解析库（clap 基于它）有一种方式可以为我们生成所有这些文件。详见 [这个深入章节](../in-depth/docs.html)。

## [将你的应用放入包管理器](#getting-your-app-into-package-repositories)

我们到目前为止看到的两种方法都不是你通常在机器上安装软件的方式，特别是对于使用大多数操作系统上的全局包管理器安装的命令行工具。对用户的好处非常明显：如果可以像安装其他工具一样安装你的程序，就不需要思考如何安装它。这些包管理器还允许用户在有新版本可用时更新他们的程序。

遗憾的是，支持不同的系统意味着你需要查看这些不同系统是如何工作的。对于某些系统，这可能只是向你的仓库添加一个文件（例如，为 macOS 的 `brew` 添加一个 Formula 文件，如 [这个](https://github.com/BurntSushi/ripgrep/blob/31adff6f3c4bfefc9e77df40871f2989443e6827/pkg/brew/ripgrep-bin.rb)），但对于其他系统，你通常需要自己发送补丁并将你的工具添加到他们的仓库中。有像 [cargo-bundle](https://crates.io/crates/cargo-bundle)、[cargo-deb](https://crates.io/crates/cargo-deb) 和 [cargo-aur](https://crates.io/crates/cargo-aur) 这样的有用工具，但描述它们如何工作以及如何为这些不同系统正确打包你的工具超出了本章的范围。

相反，让我们看看一个用 Rust 编写并可在许多不同包管理器中获得的工具。

### [一个例子：ripgrep](#an-example-ripgrep)

[ripgrep](https://github.com/BurntSushi/ripgrep) 是 `grep`/`ack`/`ag` 的替代品，用 Rust 编写。它非常成功，并且为许多操作系统打包：只需查看其 README 的 [“安装”部分](https://github.com/BurntSushi/ripgrep/tree/31adff6f3c4bfefc9e77df40871f2989443e6827#installation)！

注意它列出了几种不同的安装方式：它从 GitHub 发布链接开始，其中包含你可以直接下载的二进制文件，它列出了使用一堆不同包管理器安装的方法，你也可以使用 `cargo install` 安装。

这似乎是个非常好的主意。不要在这里选择一种方法。从 `cargo install` 开始，添加二进制发布，最后使用系统包管理器分发你的工具。

# 深入主题

一小部分章节，涵盖你在编写命令行应用程序时可能关心的一些更多细节。

# 信号处理

像命令行应用程序这样的进程需要对操作系统发送的信号做出反应。最常见的例子可能是 Ctrl+C，这个信号通常告诉进程终止。在 Rust 程序中处理信号，你需要考虑如何接收这些信号以及如何对它们做出反应。

**注意**：如果你的应用程序不需要优雅地关闭，默认处理就足够了（即立即退出，让操作系统清理资源如打开的文件句柄）。在这种情况下：不需要遵循本章的内容！

然而，对于需要自我清理的应用程序，本章非常相关！例如，如果你的应用程序需要正确关闭网络连接（向另一端的进程说“再见”），删除临时文件，或重置系统设置，请继续阅读。

## [不同操作系统之间的差异](#differences-between-operating-systems)

在 Unix 系统（如 Linux、macOS 和 FreeBSD）上，进程可以接收 [信号](https://manpages.ubuntu.com/manpages/bionic/en/man7/signal.7.html)。它可以以默认（操作系统提供的）方式对它们做出反应，捕获信号并在程序定义的方式中处理它们，或完全忽略信号。

Windows 没有信号。你可以使用 [控制台处理程序](https://docs.microsoft.com/en-us/windows/console/console-control-handlers) 来定义当事件发生时执行的回调。还有 [结构化异常处理](https://docs.microsoft.com/en-us/windows/desktop/debug/structured-exception-handling)，它处理各种系统异常，如除零、无效访问异常、堆栈溢出等。

## [首先：处理 Ctrl+C](#first-off-handling-ctrlc)

[ctrlc](https://crates.io/crates/ctrlc) crate 正如其名：它允许你以跨平台的方式对用户按下 Ctrl+C 做出反应。使用该 crate 的主要方式是：

```rust
use std::{thread, time::Duration};

fn main() {
    ctrlc::set_handler(move || {
        println!("收到 Ctrl+C！");
    })
    .expect("设置 Ctrl-C 处理程序时出错");

    // 以下代码执行实际工作，可以通过按下 Ctrl-C 中断。作为示例：让我们等待几秒钟。
    thread::sleep(Duration::from_secs(2));
}
```

当然，这没什么帮助：它只打印一条消息，但除此之外并不停止程序。

在现实世界的程序中，最好在信号处理程序中设置一个变量，然后在程序的各个地方检查它。例如，你可以在信号处理程序中设置一个 `Arc<AtomicBool>`（一个在线程之间共享的布尔值），并在热循环中，或在等待线程时，定期检查其值并在它变为 true 时中断。

```rust
use signal_hook::{consts::SIGINT, iterator::Signals};
use std::{error::Error, thread, time::Duration};

fn main() -> Result<(), Box<dyn Error>> {
    let mut signals = Signals::new([SIGINT])?;

    thread::spawn(move || {
        for sig in signals.forever() {
            println!("收到信号 {:?}", sig);
        }
    });

    // 以下代码执行实际工作，可以通过按下 Ctrl-C 中断。作为示例：让我们等待几秒钟。
    thread::sleep(Duration::from_secs(2));

    Ok(())
}
```

## [使用通道](#using-channels)

与其设置一个变量并让程序的其他部分检查它，你可以使用通道：你创建一个通道，每当接收到信号时，信号处理程序就会向其中发送一个值。在你的应用程序代码中，你使用这个通道和其他通道作为线程间的同步点。使用 [crossbeam-channel](https://crates.io/crates/crossbeam-channel) 时，它看起来像这样：

```rust
use std::time::Duration;
use crossbeam_channel::{bounded, tick, Receiver, select};
use anyhow::Result;

fn ctrl_channel() -> Result<Receiver<()>, ctrlc::Error> {
    let (sender, receiver) = bounded(100);
    ctrlc::set_handler(move || {
        let _ = sender.send(());
    })?;

    Ok(receiver)
}

fn main() -> Result<()> {
    let ctrl_c_events = ctrl_channel()?;
    let ticks = tick(Duration::from_secs(1));

    loop {
        select! {
            recv(ticks) -> _ => {
                println!("正在工作！");
            }
            recv(ctrl_c_events) -> _ => {
                println!();
                println!("再见！");
                break;
            }
        }
    }

    Ok(())
}
```

## [使用异步和流](#using-futures-and-streams)

如果你正在使用 [tokio](https://tokio.rs/)，你很可能已经使用异步模式和事件驱动设计编写你的应用程序。与其直接使用 crossbeam 的通道，你可以启用 signal-hook 的 `tokio-support` 功能。这允许你对 signal-hook 的 `Signals` 类型调用 [`.into_async()`](https://docs.rs/signal-hook/0.1.6/signal_hook/iterator/struct.Signals.html#method.into_async)，以获得一个实现 `futures::Stream` 的新类型。

## [在处理第一个 Ctrl+C 时又收到另一个 Ctrl+C 该怎么办](#what-to-do-when-you-receive-another-ctrlc-while-youre-handling-the-first-ctrlc)

大多数用户会按下 Ctrl+C，然后给你的程序几秒钟时间退出，或告诉他们发生了什么。如果这种情况没有发生，他们会再次按下 Ctrl+C。典型的行为是让应用程序立即退出。

# 使用配置文件

处理配置可能令人烦恼，尤其是当你支持多个操作系统，而它们都有各自存放短期和长期文件的位置时。

对此有多种解决方案，有些更底层，有些则更高级。

最简单易用的 crate 是 [`confy`](https://docs.rs/confy/0.3.1/confy/)。它要求你提供应用程序的名称，并通过一个 `struct`（需实现 `Serialize`、`Deserialize`）指定配置结构，它会自动处理其余部分！

```rust
#[derive(Debug, Serialize, Deserialize)]
struct MyConfig {
    name: String,
    comfy: bool,
    foo: i64,
}

fn main() -> Result<(), io::Error> {
    let cfg: MyConfig = confy::load("my_app")?;
    println!("{:#?}", cfg);
    Ok(())
}
```

这使用起来极其简单，当然你为此牺牲了可配置性。但如果你只需要一个简单的配置，这个 crate 可能正适合你！

## [配置环境](#configuration-environments)

**待办事项**

1. 评估现有 crate
2. CLI 参数 + 多个配置文件 + 环境变量
3. [`configure`](https://docs.rs/configure/0.1.1/configure/) 能否完成所有这些？是否有围绕它的优秀封装？

# 退出码

程序并不总是成功运行。当发生错误时，你应该确保正确地输出必要的信息。除了[向用户报告错误](human-communication.html)，在大多数系统上，当进程退出时，还会发出一个退出码（0 到 255 之间的整数与大多数平台兼容）。你应该为程序的状态输出正确的代码。例如，在理想情况下，当你的程序成功时，它应该以 `0` 退出。

但当发生错误时，情况会变得复杂一些。在实际中，许多工具在发生常见故障时会以 `1` 退出。目前，Rust 在进程恐慌时会设置退出码为 `101`。除此之外，人们在他们的程序中做了很多不同的事情。

那么，该怎么办？BSD 生态系统收集了它们退出码的通用定义（你可以在 [这里](https://www.freebsd.org/cgi/man.cgi?query=sysexits&apropos=0&sektion=0&manpath=FreeBSD+11.2-stable&arch=default&format=html) 找到它们）。Rust 库 [`exitcode`](https://crates.io/crates/exitcode) 提供了相同的代码，可直接在你的应用程序中使用。请参阅其 API 文档以了解可用的值。

在将 `exitcode` 依赖项添加到你的 `Cargo.toml` 后，你可以这样使用它：

```rust
fn main() {
    // ...实际工作...
    match result {
        Ok(_) => {
            println!("完成！");
            std::process::exit(exitcode::OK);
        }
        Err(CustomError::CantReadConfig(e)) => {
            eprintln!("错误：{}", e);
            std::process::exit(exitcode::CONFIG);
        }
        Err(e) => {
            eprintln!("错误：{}", e);
            std::process::exit(exitcode::DATAERR);
        }
    }
}
```

# 与人类交流

请务必先阅读教程中关于 [CLI 输出](../tutorial/output.html) 的章节。它涵盖了如何向终端写入输出，而本章将讨论 *输出什么*。

## [一切正常时](#when-everything-is-fine)

即使一切正常，报告应用程序的进展也很有用。在这些消息中尽量做到信息丰富且简洁。避免在日志中使用过于技术性的术语。记住：应用程序没有崩溃，因此用户没有理由去查找错误。

最重要的是，保持沟通风格的一致性。使用相同的前缀和句式，使日志易于快速浏览。

尝试让你的应用程序输出讲述它正在做什么以及如何影响用户的“故事”。这可以包括显示涉及的步骤时间线，甚至为长时间运行的操作显示进度条和指示器。用户在任何时候都不应感到应用程序在执行他们无法理解的神秘操作。

## [当难以判断发生了什么时](#when-its-hard-to-tell-whats-going-on)

在传达非正常状态时，保持一致性非常重要。一个日志记录密集但不遵循严格日志级别的应用程序，提供的信息量与不记录日志的应用程序相同，甚至更少。

因此，定义事件及其相关消息的严重程度至关重要；然后为它们使用一致的日志级别。这样，用户可以通过 `--verbose` 标志或环境变量（如 `RUST_LOG`）自行选择日志量。

常用的 `log` crate [定义了](https://docs.rs/log/0.4.4/log/enum.Level.html)以下级别（按严重性递增排序）：

- trace
- debug
- info
- warning
- error

将 *info* 视为默认日志级别是个好主意。用于提供信息性输出。（一些倾向于更安静输出风格的应用程序可能默认只显示警告和错误。）

此外，始终在日志消息中使用相似的前缀和句式是个好主意，以便于使用 `grep` 等工具进行过滤。一条消息应能提供足够的上下文，使其在过滤后的日志中仍具可用性，同时又不至于过于冗长。

### [示例日志语句](#example-log-statements)

```console
error: 无法在 `/home/you/project/` 中找到 `Cargo.toml`
```

```console
=> 下载仓库索引
=> 下载包...
```

以下日志输出来自 [wasm-pack](https://crates.io/crates/wasm-pack)：

```console
[1/7] 添加 WASM 目标...
 [2/7] 编译为 WASM...
 [3/7] 创建 pkg 目录...
 [4/7] 写入 package.json...
 > [WARN]: Cargo.toml 中缺少字段 `description`。非必需，但推荐
 > [WARN]: Cargo.toml 中缺少字段 `repository`。非必需，但推荐
 > [WARN]: Cargo.toml 中缺少字段 `license`。非必需，但推荐
 [5/7] 复制你的 README...
 > [WARN]: 原始 crate 没有 README
 [6/7] 安装 WASM-bindgen...
 > [INFO]: wasm-bindgen 已安装
 [7/7] 运行 WASM-bindgen...
 1 秒内完成
```

## [发生恐慌时](#when-panicking)

一个常被忽视的方面是，当程序崩溃时，它也会输出一些内容。在 Rust 中，“崩溃”最常见的形式是“恐慌”（即“受控崩溃”，与“操作系统终止进程”相对）。默认情况下，当发生恐慌时，“恐慌处理程序”会向控制台打印一些信息。

例如，如果你使用 `cargo new --bin foo` 创建一个新二进制项目，并将 `fn main` 的内容替换为 `panic!("Hello World")`，运行程序时你会得到：

```console
线程 'main' 在 src/main.rs:2:5 处恐慌，原因: 'Hello, world!'
注意：使用 `RUST_BACKTRACE=1` 查看回溯。
```

这对开发者来说是有用的信息。（惊喜：程序因 `main.rs` 文件第 2 行而崩溃。）但对于没有源代码访问权限的用户来说，这并不太有价值。事实上，它很可能只会造成困惑。因此，添加一个更面向最终用户的自定义恐慌处理程序是个好主意。

一个专门做这件事的库叫做 [human-panic](https://crates.io/crates/human-panic)。要将其添加到你的 CLI 项目中，你导入它并在 `main` 函数开头调用 `setup_panic!()` 宏：

```rust
use human_panic::setup_panic;

fn main() {
   setup_panic!();

   panic!("Hello world")
}
```

现在它会显示一条非常友好的消息，并告诉用户他们可以做什么：

```console
这真令人尴尬。

foo 遇到了问题并崩溃了。为了帮助我们诊断问题，你可以向我们发送崩溃报告。

我们已在 "/var/folders/n3/dkk459k908lcmkzwcmq0tcv00000gn/T/report-738e1bec-5585-47a4-8158-f1f7227f0168.toml" 生成了一份报告文件。提交一个议题或发送一封主题为 "foo Crash Report" 的邮件，并将报告作为附件包含在内。

- 作者：你的名字 <your.name@example.com>

我们重视隐私，不进行任何自动错误收集。为了改进软件，我们依赖人们提交报告。

谢谢！
```

# 与机器通信

命令行工具的真正威力体现在你能将它们组合使用时。这并不是一个新想法：事实上，这是 [Unix 哲学](https://en.wikipedia.org/wiki/Unix_philosophy) 中的一句话：

> 每个程序的输出都应成为另一个尚未知晓的程序的输入。

如果我们的程序满足这一期望，我们的用户就会满意。为确保这一点顺利实现，我们不仅应提供美观的人类可读输出，还应提供适合其他程序需求的版本。让我们看看如何做到这一点。

**注意**：请务必先阅读教程中关于 [CLI 输出](../tutorial/output.html) 的章节。它涵盖了如何向终端写入输出。

## [谁在读取这些内容？](#whos-reading-this)

首先要问的问题是：我们的输出是面向前端有彩色终端的人类，还是面向另一个程序？要回答这个问题，我们可以使用 [IsTerminal](https://doc.rust-lang.org/stable/std/io/trait.IsTerminal.html) 特征：

```rust
use std::io::IsTerminal;

if std::io::stdout().is_terminal() {
    println!("我是一个终端");
} else {
    println!("我不是");
}
```

根据谁将读取我们的输出，我们可以添加额外信息。例如，人类喜欢颜色，如果你在某个 Rust 项目中运行 `ls`，你可能会看到类似这样的内容：

```console
$ ls
CODE_OF_CONDUCT.md   LICENSE-APACHE       examples
CONTRIBUTING.md      LICENSE-MIT          proptest-regressions
Cargo.lock           README.md            src
Cargo.toml           convey_derive        target
```

因为这种样式是为人类设计的，在大多数配置中，它甚至会以颜色打印某些名称（如 `src`），以表明它们是目录。但如果你将其管道输出到文件或 `cat` 等程序，`ls` 会调整其输出。它不会使用适合我终端窗口的列，而是每项单独一行。它也不会输出任何颜色。

```console
$ ls | cat
CODE_OF_CONDUCT.md
CONTRIBUTING.md
Cargo.lock
Cargo.toml
LICENSE-APACHE
LICENSE-MIT
README.md
convey_derive
examples
proptest-regressions
src
target
```

## [为机器提供的简单输出格式](#easy-output-formats-for-machines)

历史上，命令行工具产生的唯一输出类型是字符串。这对于终端前的人类来说通常没问题，因为他们能够阅读文本并推断其含义。但其他程序通常不具备这种能力：它们理解像 `ls` 这样的工具输出的唯一方式是，程序作者包含了一个恰好能处理 `ls` 输出的解析器。

这通常意味着输出被限制在易于解析的范围内。例如，TSV（制表符分隔值）格式非常流行，其中每条记录占一行，每行包含制表符分隔的内容。这些基于文本行的简单格式允许使用 `grep` 等工具处理 `ls` 的输出。`| grep Cargo` 并不关心你的行是来自 `ls` 还是文件，它只是逐行过滤。

其缺点是，你无法使用简单的 `grep` 命令来过滤 `ls` 给出的所有目录。为此，每个目录项都需要携带额外的数据。

## [为机器提供 JSON 输出](#json-output-for-machines)

制表符分隔值是一种输出结构化数据的简单方式，但它要求另一个程序知道预期的字段（及其顺序），并且很难输出不同类型的消息。例如，假设我们的程序希望向消费者发送一条消息，说明它正在等待下载，然后输出一条描述其获取数据的消息。这些是截然不同的消息类型，试图在 TSV 输出中统一它们需要我们发明一种区分它们的方法。当我们想打印包含两个长度不一的项目列表的消息时，情况也是如此。

尽管如此，选择一种在大多数编程语言/环境中易于解析的格式仍然是个好主意。因此，近年来，许多应用程序获得了以 [JSON](https://www.json.org/) 输出其数据的能力。它足够简单，以至于几乎所有语言都有解析器，同时又足够强大，适用于许多情况。虽然它是一种人类可读的文本格式，但许多人也开发了非常快速的 JSON 数据解析和序列化实现。

在上述描述中，我们谈到了“消息”由我们的程序输出。这是一种思考输出的好方法：你的程序不一定只输出一个数据块，而可能在运行过程中发出大量不同的信息。在输出 JSON 时支持这种方法的一个简单方式是，每条消息写一个 JSON 文档，并将每个 JSON 文档放在新行上（有时称为 [行分隔 JSON](https://en.wikipedia.org/wiki/JSON_streaming#Line-delimited_JSON)）。这可以使实现简单到仅使用常规的 `println!`。

以下是一个简单的示例，使用 [serde_json](https://crates.io/crates/serde_json) 的 `json!` 宏快速在 Rust 源代码中编写有效的 JSON：

```rust
use clap::Parser;
use serde_json::json;

/// 在文件中搜索模式并显示包含它的行。
#[derive(Parser)]
struct Cli {
    /// 输出 JSON 而非人类可读消息
    #[arg(long = "json")]
    json: bool,
}

fn main() {
    let args = Cli::parse();
    if args.json {
        println!(
            "{}",
            json!({
                "type": "message",
                "content": "Hello world",
            })
        );
    } else {
        println!("Hello world");
    }
}
```

输出如下：

```console
$ cargo run -q
Hello world
$ cargo run -q -- --json
{"content":"Hello world","type":"message"}
```

（使用 `-q` 运行 `cargo` 可以抑制其常规输出。`--` 之后的参数将传递给我们的程序。）

### [实际示例：ripgrep](#practical-example-ripgrep)

*[ripgrep](https://github.com/BurntSushi/ripgrep)* 是用 Rust 编写的 *grep* 或 *ag* 的替代品。默认情况下，它会产生类似以下的输出：

```console
$ rg default
src/lib.rs
37:    Output::default()

src/components/span.rs
6:    Span::default()
```

但给定 `--json` 时，它会打印：

```console
$ rg default --json
{"type":"begin","data":{"path":{"text":"src/lib.rs"}}}
{"type":"match","data":{"path":{"text":"src/lib.rs"},"lines":{"text":"    Output::default()\n"},"line_number":37,"absolute_offset":761,"submatches":[{"match":{"text":"default"},"start":12,"end":19}]}}
{"type":"end","data":{"path":{"text":"src/lib.rs"},"binary_offset":null,"stats":{"elapsed":{"secs":0,"nanos":137622,"human":"0.000138s"},"searches":1,"searches_with_match":1,"bytes_searched":6064,"bytes_printed":256,"matched_lines":1,"matches":1}}}
{"type":"begin","data":{"path":{"text":"src/components/span.rs"}}}
{"type":"match","data":{"path":{"text":"src/components/span.rs"},"lines":{"text":"    Span::default()\n"},"line_number":6,"absolute_offset":117,"submatches":[{"match":{"text":"default"},"start":10,"end":17}]}}
{"type":"end","data":{"path":{"text":"src/components/span.rs"},"binary_offset":null,"stats":{"elapsed":{"secs":0,"nanos":22025,"human":"0.000022s"},"searches":1,"searches_with_match":1,"bytes_searched":5221,"bytes_printed":277,"matched_lines":1,"matches":1}}}
{"data":{"elapsed_total":{"human":"0.006995s","nanos":6994920,"secs":0},"stats":{"bytes_printed":533,"bytes_searched":11285,"elapsed":{"human":"0.000160s","nanos":159647,"secs":0},"matched_lines":2,"matches":2,"searches":2,"searches_with_match":2}},"type":"summary"}
```

正如你所见，每个 JSON 文档都是一个包含 `type` 字段的对象（映射）。这使我们能够编写一个简单的 `rg` 前端，实时读取这些文档，并在 *ripgrep* 仍在搜索时显示匹配项（以及它们所在的文件）。

**注意**：这就是 Visual Studio Code 用于其代码搜索的方式。

## [如何处理通过管道输入给我们的数据](#how-to-deal-with-input-piped-into-us)

假设我们有一个程序，用于读取文件中的单词数量：

```rust
use clap::Parser;
use std::path::PathBuf;

/// 统计文件中的行数
#[derive(Parser)]
#[command(arg_required_else_help = true)]
struct Cli {
    /// 要读取的文件路径
    file: PathBuf,
}

fn main() {
    let args = Cli::parse();
    let mut word_count = 0;
    let file = args.file;

    for line in std::fs::read_to_string(&file).unwrap().lines() {
        word_count += line.split(' ').count();
    }

    println!("{} 中的单词数: {}", file.to_str().unwrap(), word_count)
}
```

它接受文件路径，逐行读取，并统计由空格分隔的单词数量。

当你运行它时，它会输出文件中的总单词数：

```console
$ cargo run README.md
README.md 中的单词数: 47
```

但如果我们想统计通过管道输入到程序中的单词数量呢？Rust 程序可以通过 [Stdin 结构](https://doc.rust-lang.org/std/io/struct.Stdin.html) 读取通过 stdin 传递的数据，你可以通过标准库中的 [stdin 函数](https://doc.rust-lang.org/std/io/fn.stdin.html) 获取它。类似于读取文件的行，它也可以从 stdin 读取行。

以下是一个统计通过 stdin 输入的单词数量的程序：

```rust
use clap::{CommandFactory, Parser};
use std::{
    fs::File,
    io::{stdin, BufRead, BufReader, IsTerminal},
    path::PathBuf,
};

/// 统计文件或 stdin 中的行数
#[derive(Parser)]
#[command(arg_required_else_help = true)]
struct Cli {
    /// 要读取的文件路径，使用 - 从 stdin 读取（不能是 tty）
    file: PathBuf,
}

fn main() {
    let args = Cli::parse();

    let word_count;
    let mut file = args.file;

    if file == PathBuf::from("-") {
        if stdin().is_terminal() {
            Cli::command().print_help().unwrap();
            ::std::process::exit(2);
        }

        file = PathBuf::from("<stdin>");
        word_count = words_in_buf_reader(BufReader::new(stdin().lock()));
    } else {
        word_count = words_in_buf_reader(BufReader::new(File::open(&file).unwrap()));
    }

    println!("{} 的单词数: {}", file.to_string_lossy(), word_count)
}

fn words_in_buf_reader<R: BufRead>(buf_reader: R) -> usize {
    let mut count = 0;
    for line in buf_reader.lines() {
        count += line.unwrap().split(' ').count()
    }
    count
}
```

如果你运行该程序并使用 `-` 表示从 stdin 读取，它将输出单词数量：

```console
$ echo "hi there friend" | cargo run -- -
stdin 中的单词数: 3
```

它要求 stdin 不是交互式的，因为我们期望输入是通过管道传入程序的，而不是在运行时手动输入的文本。如果 stdin 是 tty，它会输出帮助文档，以便清楚地说明为什么不起作用。

# 为你的 CLI 应用渲染文档

CLI 的文档通常包括命令中的 `--help` 部分和手册（man）页面。

使用 [`clap`](https://crates.io/crates/clap) 和 [`clap_mangen`](https://crates.io/crates/clap_mangen) crate 时，两者都可以自动生成。

```rust
#[derive(Parser)]
pub struct Head {
    /// 要加载的文件
    pub file: PathBuf,
    /// 要打印的行数
    #[arg(short = "n", default_value = "5")]
    pub count: usize,
}
```

其次，你需要使用 `build.rs` 在编译时根据代码中的应用定义生成手册文件。

需要注意一些事项（如你希望如何打包二进制文件），但目前我们只需将 `man` 文件放在 `src` 文件夹旁边。

```rust
use clap::CommandFactory;

#[path="src/cli.rs"]
mod cli;

fn main() -> std::io::Result<()> {
    let out_dir = std::path::PathBuf::from(std::env::var_os("OUT_DIR").ok_or_else(|| std::io::ErrorKind::NotFound)?);
    let cmd = cli::Head::command();

    let man = clap_mangen::Man::new(cmd);
    let mut buffer: Vec<u8> = Default::default();
    man.render(&mut buffer)?;

    std::fs::write(out_dir.join("head.1"), buffer)?;

    Ok(())
}
```

当你现在编译应用程序时，项目目录中将出现一个 `head.1` 文件。

如果你在 `man` 中打开它，你就能欣赏到你的免费文档。

# 资源

协作/帮助

- [cli-and-tui Discord 频道](https://discord.com/channels/273534239310479360/943315667430563862)

## [本书中引用的 crate](#crates-referenced-in-this-book)

- [anyhow](https://crates.io/crates/anyhow) - 提供 `anyhow::Error` 用于简易错误处理
- [assert_cmd](https://crates.io/crates/assert_cmd) - 简化 CLI 的集成测试
- [assert_fs](https://crates.io/crates/assert_fs) - 设置输入文件和测试输出文件
- [clap-verbosity-flag](https://crates.io/crates/clap-verbosity-flag) - 为 clap CLI 添加 `--verbose` 标志
- [clap](https://crates.io/crates/clap) - 命令行参数解析器
- [confy](https://crates.io/crates/confy) - 无样板配置管理
- [crossbeam-channel](https://crates.io/crates/crossbeam-channel) - 提供多生产者多消费者通道用于消息传递
- [ctrlc](https://crates.io/crates/ctrlc) - 简单的 Ctrl-C 处理程序
- [env_logger](https://crates.io/crates/env_logger) - 实现可通过环境变量配置的日志记录器
- [exitcode](https://crates.io/crates/exitcode) - 系统退出码常量
- [human-panic](https://crates.io/crates/human-panic) - 恐慌消息处理程序
- [indicatif](https://crates.io/crates/indicatif) - 进度条和旋转器
- [log](https://crates.io/crates/log) - 提供抽象于实现之上的日志记录
- [predicates](https://crates.io/crates/predicates) - 实现布尔值谓词函数
- [proptest](https://crates.io/crates/proptest) - 属性测试框架
- [serde_json](https://crates.io/crates/serde_json) - 序列化/反序列化为 JSON
- [signal-hook](https://crates.io/crates/signal-hook) - 处理 UNIX 信号
- [tokio](https://crates.io/crates/tokio) - 异步运行时
- [wasm-pack](https://crates.io/crates/wasm-pack) - 用于构建 WebAssembly 的工具

## [其他 crate](#other-crates)

由于 Rust crate 的格局不断变化，寻找 crate 的好地方是 [lib.rs](https://lib.rs) crate 索引，包括：

- [命令行界面](https://lib.rs/command-line-interface)
- [配置](https://lib.rs/config)
- [数据库接口](https://lib.rs/database)
- [编码](https://lib.rs/encoding)
- [文件系统](https://lib.rs/filesystem)
- [HTTP 客户端](https://lib.rs/web-programming/http-client)
- [操作系统](https://lib.rs/os)

其他资源：

- [Rust Cookbook](https://rust-lang-nursery.github.io/rust-cookbook/)
- [rosetta-rs](https://github.com/rosetta-rs)