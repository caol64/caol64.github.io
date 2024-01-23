import os
import re
import sys


def handle(file_path, output_file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            # 使用正则表达式匹配 `---` 包裹的部分，并删除
            content = re.sub(r"^---(.*?)---", "", content, flags=re.DOTALL)

            # 使用正则表达式匹配图片地址 `![]()`和`![](<>)` 将其改为在线路径
            content = modify_md_image_links(content)

        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write(content)

    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def modify_md_image_links(text):
    pattern1 = re.compile(r'!\[(.*?)\]\(<(.*?)>\)')  # 尖括号的模式
    pattern2 = re.compile(r'!\[(.*?)\]\(([^<].*?)\)')  # 非尖括号的模式

    def replacer(match):
        alt_text = match.group(1)
        url = match.group(2).replace(' ', '%20')
        if not url.startswith('http'):
            return f'![{alt_text}](https://babyno.top{url})'
        else:
            return match.group(0)

    # 首先处理尖括号的模式
    text = re.sub(pattern1, replacer, text)
    # 然后处理非尖括号的模式
    text = re.sub(pattern2, replacer, text)

    return text


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python handle_zhihu.py <file>")
    else:
        file_path = sys.argv[1]
        file_name, file_extension = os.path.splitext(file_path)
        handle(
            file_path,
            f"{file_name}_zhihu.{file_extension}"
        )
