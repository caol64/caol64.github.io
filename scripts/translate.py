import sys
import os
import requests


def handle(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # print(''.join(lines))

    results = []
    ignore_tag = ''
    ignore_flag = False
    for line in lines:
        if not ignore_flag:
            ignore_tag = ''
        # if line == '\n':
        #     ignore_tag = '\\n'
        if line.startswith('---'):
            ignore_tag = '---'
            ignore_flag = not ignore_flag
        elif line.startswith('```'):
            ignore_tag = '```'
            ignore_flag = not ignore_flag
        elif line.startswith('!['):
            ignore_tag = 'img'

        if ignore_tag != '\\n':
            if ignore_tag == '':
                handled_line = Line(True, line)
            else:
                handled_line = Line(False, line)
            results.append(handled_line)

    # for r in results:
    #     print(r.get_send(), r.get_content())

    results = merge(results)

    # for r in results:
    #     print(r.get_send(), r.get_content())

    assistant = Assistant()
    for line in results:
        if line.get_send() and line.get_content() != '\n':
            resp_json = assistant.work(line.get_content()).json()
            translated = resp_json['candidates'][0]['content']['parts'][0]['text']
            line.set_content('\n' + translated + '\n')

    file_name, file_extension = os.path.splitext(file_path)
    out_file_path = f"{file_name}.en.{file_extension}"
    with open(out_file_path, "w", encoding="utf-8") as file:
        for line in results:
            file.write(line.get_content())


def merge(results):
    new_results = []
    size = 0
    tmp_list = []
    for r in results:
        if not r.get_send():
            if tmp_list:
                new_results.append(Line(True, ''.join(tmp_list)))
                size = 0
                tmp_list = []
            new_results.append(r)
        else:
            if size + len(r.get_content()) > 500:
                tmp_list.append(r.get_content())
                new_results.append(Line(True, ''.join(tmp_list)))
                size = 0
                tmp_list = []
            else:
                tmp_list.append(r.get_content())
                size += len(r.get_content())
    if tmp_list:
        new_results.append(Line(True, ''.join(tmp_list)))
    return new_results


class Line:
    def __init__(self, send, content) -> None:
        self.send = send
        self.content = content

    def get_send(self):
        return self.send

    def get_content(self):
        return self.content

    def set_content(self, content):
        self.content = content


class Assistant:
    def __init__(self) -> None:
        with open('secrets/gemini.key', 'r') as f:
            self.api_key = f.read()

    def work(self, user_prompt):
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={self.api_key}'
        # print(url)
        headers = {
            'Content-Type': 'application/json',
        }

        # Prepare the body data.
        data = {
            "contents": [{
                "parts": [{
                    "text": f"Translate to English:\n\n{user_prompt}"
                }]
            }]
        }

        # Send the POST request.
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response


if __name__ == "__main__":
    handle(sys.argv[1])
