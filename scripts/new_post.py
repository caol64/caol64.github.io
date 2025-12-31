import sys
import subprocess
from datetime import datetime
import requests


class Assistant:
    def __init__(self) -> None:
        with open('secrets/gemini.key', 'r') as f:
            self.api_key = f.read()

    def work(self, user_prompt):
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}'
        # print(url)
        headers = {
            'Content-Type': 'application/json',
        }

        # Prepare the body data.
        data = {
            "contents": [{
                "parts": [{
                    "text": f"You are a professional translator. You will not output anything other than the translation result. Translate to English:\n\n{user_prompt}"
                }]
            }]
        }

        # Send the POST request.
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response


def translate_title(title):
    assistant = Assistant()
    resp_json = assistant.work(title).json()
    translated_title = resp_json['candidates'][0]['content']['parts'][0]['text']
    print(translated_title)
    return (
        translated_title.lower()
        .strip()
        .replace(".", "")
        .replace(",", "")
        .replace('"', "")
        .replace("'", "")
        .replace("(", "")
        .replace(")", "")
        .replace(" ", "-")
    )


def create_post(title):
    today = datetime.today()
    formatted_date = today.strftime("%Y-%m-%d")
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
    title = sys.argv[1]
    file_path = create_post(title)
    replace_title_in_post(file_path, title)