import subprocess
import re
import sys
import yaml


def handle(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    try:
        # 使用正则表达式匹配 `---` 包裹的部分
        match = re.search(r"^---(.*?)---", content, re.DOTALL)
        if match:
            yaml_data = match.group(1)
            metadata = yaml.safe_load(yaml_data)
            title = metadata.get('title')
            slug = metadata.get('slug')
            date = metadata.get('date')
            content = re.sub(r"^---(.*?)---", "", content, flags=re.DOTALL)
        else:
            title = None

        # 使用正则表达式匹配图片地址 `![]()`和`![](<>)` 将其改为在线路径
        content = modify_md_image_links(content)

        if title:
            content = f'# {title}\n\n{content}'
            year = date.year
            month = f'{date.month:02d}'
            url = f'https://babyno.top/posts/{year}/{month}/{slug}/'
            print(url)
            content = f'{content}\n\n> 本文首发于：{url}\n>\n> 公众号：机器人小不'

        print(content)
        write_to_clipboard(content)

    except Exception as e:
        print(f"An error occurred: {e}")


def modify_md_image_links(text):
    pattern1 = re.compile(r'!\[(.*?)\]\(<(.*?)>\)')  # 尖括号的模式
    pattern2 = re.compile(r'!\[(.*?)\]\(([^<].*?)\)')  # 非尖括号的模式

    def replacer(match):
        alt_text = match.group(1)
        url = match.group(2).replace(' ', '%20')
        if not url.startswith('http'):
            return f'![{alt_text}](https://babyno.top/{url})'
        else:
            return match.group(0)

    # 首先处理尖括号的模式
    text = re.sub(pattern1, replacer, text)
    # 然后处理非尖括号的模式
    text = re.sub(pattern2, replacer, text)

    return text


def write_to_clipboard(content):
    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    process.communicate(input=content.encode('utf-8'))


if __name__ == "__main__":
    handle(sys.argv[1])