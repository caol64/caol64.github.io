---
author: 路边的阿不
title: 用「VSCode Task」自动化创建博客
slug: create-hugo-post-with-vscode-task-and-chatgpt
description: Immerse in innovative ways of improving your writing efficiency using VSCode and ChatGPT. Learn how to swiftly generate blog posts in Hugo, with a mere article title input, and see how translation and automation aid the process.
date: 2023-11-14 11:31:43
draft: false
ShowToc: true
TocOpen: true
tags:
  - 效率
  - AI
categories:
  - 教程
---
在之前的文章中，我提到我通常使用 `VSCode` 进行写作。这一次，我想分享一些提高平时写作效率的小技巧。同时，这也是我第一次尝试使用刚刚注册的 `ChatGPT`，看看它在辅助编码方面的能力如何。

## 需求背景

在使用 `Hugo` 创建新文章时，通常需要通过命令来执行操作，比如：

```shell
hugo new content posts/2023/2023-10-21-hello-world.md
```

这个命令中，`content` 后面的内容是新文章的相对路径。按照我的偏好，我希望文章按年份归档，并且在文章标题前添加日期以便于检索。

然而，问题在于每次都要输入这一长串命令，感觉相当繁琐。我觉得这个命令里除了 `"hello world"` 以外的部分都是可以自动生成的。因此，我的需求就产生了：我希望在 `VSCode` 中只需输入文章标题，就能自动生成文章模板。

另外，考虑到我写的是中文博客，我对需求提出了更进一步的要求：输入标题时可以是中文，并且自动翻译成英文。比如，“世界，你好”应该自动翻译成 `hello world`。

## 解决方案

为了实现这一需求，我选择了`VSCode Task`，方案如下：

- **创建Task**
  编写脚本，使得在`VSCode`弹出输入框，接收输入的标题。
- **创建python脚本**
  将输入的标题生成对应的 `Hugo` 命令，并执行。
- **中英文翻译：**
  利用`Google翻译API`，将输入的中文标题翻译成英文。

## 实际操作
### 创建`VSCode Task`
在`VSCode`菜单栏中选择：`Terminal` -> `Configure Tasks` -> `create tasks.json file from template` -> `Others`，会自动在工作目录的`.vscode`文件夹下生成`tasks.json`文件。

将`tasks.json`改成如下内容：
```json
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "2.0.0",
    "tasks": [
        {
            "label": "new post",
            "type": "shell",
            "command": "python",
            "args": ["scripts/new_post.py", "${input:title}"],
            "problemMatcher": []
        }
    ],
    "inputs": [
        {
            "id": "title",
            "type": "promptString",
            "description": "Enter your title."
        }
    ]
}
```
说明一下，这段代码创建了一个名叫`new post`的`task`，底层使用`shell`脚本调用了名叫`scripts/new_post.py`的`python`脚本，并将用户输入的`title`作为参数输入。

### 创建`python`脚本
接下来我们要请出今天的嘉宾——`ChatGPT`，让它帮我生成`python`脚本。

先整理一下我的需求：
> 我希望生成一个python脚本，要求：
> - 接收一个文本类型的输入参数：title
> - 调用google翻译API将title翻译成英文
> - 翻译后的title如果有多个单词，单词间用"-"连接
> - 调用shell脚本`hugo new content posts/${yyyy}/${yyyy-MM-dd}-${title}.md`

将上述提示发给`ChatGPT`，以下是它的回复：
> 您可以使用以下的 Python 脚本来实现您的需求。请确保您已经安装了 `googletrans` 库。您可以使用以下命令来安装它：
> 
> ```bash
> pip install googletrans==4.0.0-rc1
> ```
> 
> 接下来，您可以创建一个 Python 脚本，比如 `translate_and_create_post.py`，内容如下：
> 
> ```python
> import sys
> from googletrans import Translator
> import subprocess
> from datetime import datetime
> 
> def translate_title(title):
>     translator = Translator()
>     translated_title = translator.translate(title, dest='en').text
>     return translated_title.replace(' ', '-')
> 
> def create_post(title):
>     today = datetime.today()
>     formatted_date = today.strftime('%Y-%m-%d')
>     translated_title = translate_title(title)
>     file_name = f"content/posts/{today.year}/{formatted_date}-{translated_title}.md"
>     subprocess.run(["hugo", "new", file_name])
>     print(f"Post created successfully: {file_name}")
> 
> if __name__ == "__main__":
>     if len(sys.argv) != 2:
>         print("Usage: python translate_and_create_post.py <title>")
>     else:
>         title = sys.argv[1]
>         create_post(title)
> ```
> 
> 这个脚本使用了 `googletrans` 库来将输入的标题翻译成英文，并按照您的要求进行了处理。然后，它使用 `subprocess` 模块来调用 `hugo new` 命令创建新的文章。
> 
> 使用方法示例：
> 
> ```bash
> python translate_and_create_post.py "您的标题"
> ```
> 
> 请注意，为了使用 Google 翻译 API，您可能需要提供 API 密钥。确保您已经按照 Google API 文档中的指南获取并配置了 API 密钥。

嗬，看上去不错，赶紧把这段代码保存成`scripts/new_post.py`试一下。

![](imgs/posts/2023-11-14-create-a-hugo-post-with-vscode-task-and-chatgpt/1.gif)

真不错，一次性成功，我的心还有点小激动。但还有点小问题，生成的模版里的`title`也被翻译成英文了，我想保留的是我的输入。只要用`sed`命令查找并替换就行了。有了刚才的经历，这点小事交给`ChatGPT`我信心十足。

输入：

> 我希望生成一个python脚本，要求：
> - 接收一个文本类型的输入参数：title
> - 给定一个文本文件`a.txt`
> - 使用`sed`命令找到文件中`title: `开头的行，将`title: `之后的内容替换为${title}

输出：
> 如果您想使用`sed`命令替换文件中的文本，您可以在Python脚本中调用`subprocess`模块来执行`sed`命令。以下是一个示例脚本：
> 
> ```python
> import sys
> import subprocess
> 
> def replace_title_in_file(title):
>     file_path = 'a.txt'
>     sed_command = f"sed -i 's/title: .*/title: {title}/g' {file_path}"
> 
>     try:
>         subprocess.run(sed_command, shell=True, check=True)
>         print(f"Title replaced successfully in {file_path}")
>     except subprocess.CalledProcessError as e:
>         print(f"Error: {e}")
> 
> if __name__ == "__main__":
>     if len(sys.argv) != 2:
>         print("Usage: python replace_title_with_sed.py <title>")
>     else:
>         title = sys.argv[1]
>         replace_title_in_file(title)
> ```
> 
> 这个脚本使用`subprocess`模块调用了`sed`命令，替换了文件中以`title: `开头的行的内容。使用方法示例：
> 
> ```bash
> python replace_title_with_sed.py "新的标题"
> ```
> 
> 请确保脚本和`a.txt`文件在同一目录下，且您具有足够的权限读写`a.txt`文件。这个脚本会在文件中找到以`title: `开头的行，并将其替换为新的标题。

把`replace_title_in_file`方法复制到`scripts/new_post.py`文件里，并在刚才到操作完成后调用它即可。

### 调试
本以为这一步也会像第一步那样顺利，但没想到事实打脸。这段代码运行报错。无奈只能将`sed`命令拷贝到终端调试。

继续追问：
> 使用`sed`命令找到文件中`title: `开头的行，将该行`title: `之后的内容替换为${title}

回答：
> 如果您只想使用 `sed` 命令替换文件中以 `title: ` 开头的行的内容，可以在终端中执行如下命令：
> 
> ```bash
> sed -i 's/^title: .*/title: ${title}/g' a.txt
> ```

还是不行，有点汗流浃背了。此时我突然意识到了什么，于是再次追问：
> mac环境下，使用`sed`命令找到文件中`title: `开头的行，将该行`title: `之后的内容替换为${title}

回答：
> 在 macOS 上，`sed` 的用法稍有不同。您可以使用以下命令来实现在文件中找到以 `title: ` 开头的行，并将其后的内容替换为 `${title}`：
> 
> ```bash
> sed -i '' 's/^title: .*/title: ${title}/g' a.txt
> ```
> 
> 在 macOS 上，`-i` 选项后需要提供一个备份文件的扩展名，即使不需要备份也要提供一个空字符串 `''`。这样，`sed` 命令会直接在原始文件上进行修改。

原来如此，`mac`下需要多一个参数，是我的锅，不能怪`ChatGPT`。

稍作调整后，我继续进行操作：

![](imgs/posts/2023-11-14-create-a-hugo-post-with-vscode-task-and-chatgpt/2.gif)

效果不错，还是挺满意的。

## 总结
通过这样的优化，我现在只需专注于输入文章标题，而不再需要关心繁杂的命令。这大大提高了我的写作效率，使得整个流程更加流畅。

最让人惊喜的是`ChatGPT`，它带给我的体验是震撼的。我没有尝试它的高级功能，但已经被它的魅力折服。看来是时候去深入了解它了。