from pathlib import Path
import re
import yaml


def handle():
    root_dir = Path(__file__).parent.parent
    post_dir = root_dir / "content/posts"
    results = []
    for file_path in post_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix == ".md":
            content = file_path.read_text()
            try:
                # 使用正则表达式匹配 `---` 包裹的部分
                match = re.search(r"^---(.*?)---", content, re.DOTALL)
                if match:
                    yaml_data = match.group(1)
                    metadata = yaml.safe_load(yaml_data)
                    results.append(metadata)
            except Exception as e:
                print(f"An error occurred: {e}")
    print(results)


if __name__ == "__main__":
    handle()