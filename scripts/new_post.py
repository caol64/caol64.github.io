import sys
from googletrans import Translator
import subprocess
from datetime import datetime


def translate_title(title):
    translator = Translator()
    translated_title = translator.translate(title, dest='en').text
    return translated_title.lower().replace(',', '').replace('"', '').replace('\'', '').replace(' ', '-')


def create_post(title):
    today = datetime.today()
    formatted_date = today.strftime('%Y-%m-%d')
    translated_title = translate_title(title)
    file_name = f"content/posts/{today.year}/{formatted_date}-{translated_title}.md"
    subprocess.run(["hugo", "new", file_name])
    print(f"Post created successfully: {file_name}")
    return file_name


def replace_title_in_post(file_path, title):
    sed_command = f"sed -i '' 's/title: .*/title: {title}/g' {file_path}"
    try:
        subprocess.run(sed_command, shell=True, check=True)
        print(f"Title replaced successfully in {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python new_post.py <title>")
    else:
        title = sys.argv[1]
        file_path = create_post(title)
        replace_title_in_post(file_path, title)
