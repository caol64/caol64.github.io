import re
import sys
import yaml
import markdown
import subprocess


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
            content = re.sub(r"^---(.*?)---", "", content, flags=re.DOTALL)
        else:
            title = None

        # 使用正则表达式匹配图片地址 `![]()`和`![](<>)` 将其改为在线路径
        content = modify_md_image_links(content)

        html = markdown.markdown(content, extensions=['fenced_code', 'tables', 'footnotes'])
        if title:
            html = f'<h1>{title}</h1>\n\n{html}'

        # print(html)
        write_to_clipboard(html)

    except Exception as e:
        print(f"An error occurred: {e}")


def modify_md_image_links(text):
    pattern1 = re.compile(r'!\[(.*?)\]\(<(.*?)>\)')  # 匹配![](<>)
    pattern2 = re.compile(r'!\[(.*?)\]\(([^<].*?)\)')  # 匹配![]()

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


def write_to_clipboard(html):
    hex_text = subprocess.check_output(['hexdump', '-ve', '1/1 "%.2x"'], input=html.encode('utf-8'))
    cmd = subprocess.check_output(['xargs', 'printf', 'set the clipboard to {text:\" \", «class HTML»:«data HTML%s»}'], input=hex_text)

    subprocess.run(['osascript', '-'], input=cmd)


if __name__ == "__main__":
    handle(sys.argv[1])
