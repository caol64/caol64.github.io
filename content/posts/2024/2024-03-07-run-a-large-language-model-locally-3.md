---
author: 路边的阿不
title: 在本地跑一个大语言模型(3)
slug: run-a-large-language-model-locally-3
description: Unlock the power of function-calling feature to extend your model's capabilities with this comprehensive tutorial. Explore how to define specific functions, create user prompts and return the precise JSON schema.
date: 2024-03-07 14:24:56
draft: false
ShowToc: true
TocOpen: true
tags:
  - Ollama
  - AI
categories:
  - 教程
---
在前两篇文章里，我们已经介绍了如何在本地运行`Ollama`以及如何通过提供外部数据库的方式微调模型的答案。本篇文章将继续探索如何使用“函数调用(`function-calling`)”功能以扩展模型能力，使其在“智能”的道路上越走越远。

## function-calling介绍

根据`OpenAI`官方文档，`function-calling`是使得大型语言模型具备可以连接到外部工具的能力。简而言之，**开发者事先给模型提供了若干工具（函数），在模型理解用户的问题后，自行判断是否需要调用工具以获得更多上下文信息，帮助模型更好的决策**。

举个例子：在[上一篇文章](https://babyno.top/posts/2024/03/run-a-large-language-model-locally-2/)我们是利用`Document loaders`将事先准备好的文本作为上下文提供给模型，而使用`function-calling`以后，我们只要提供一个“搜索函数”作为工具，模型即可自己通过搜索引擎进行搜索然后得出答案。

得益于最新的模型训练，现在的模型既能够检测何时应调用函数（取决于输入），还能够以比以前的模型更贴近函数签名的方式响应 JSON。

## 用途

`function-calling`有什么用？官网给出3个例子：

- **创建通过调用外部 API 回答问题的助手**
- **将自然语言转换为 API 调用**
- **从文本中提取结构化数据**

下面我们就一步一步来理解一下`function-calling`。

## 定义function

首先定义4个`function`，这4个`function`有不同的使用场景。

```python
def get_gas_prices(city: str) -> float:
    """Get gas prices for specified cities."""
    print(f'Get gas prices for {city}.')


def github(project: str) -> str:
    '''Get the infomations such as author from github with the project name.'''
    print(f'Access the github for {project}.')


def get_weather(city: str) -> str:
    """Get the current weather given a city."""
    print(f'Getting weather for {city}.')


def get_directions(start: str, destination: str) -> float:
    """Get directions from Google Directions API.
    start: start address as a string including zipcode (if any)
    destination: end address as a string including zipcode (if any)"""
    print(f'Get directions for {start} {destination}.')
```

## 定义Prompts

```python
    functions_prompt = f"""
You have access to the following tools:
{function_to_json(get_weather)}
{function_to_json(get_gas_prices)}
{function_to_json(get_directions)}
{function_to_json(github)}

You must follow these instructions:
Always select one or more of the above tools based on the user query
If a tool is found, you must respond in the JSON format matching the following schema:
{{
   "tools": {{
        "tool": "<name of the selected tool>",
        "tool_input": <parameters for the selected tool, matching the tool's JSON schema
   }}
}}
If there are multiple tools required, make sure a list of tools are returned in a JSON array.
If there is no tool that match the user request, you must respond empty JSON {{}}.

User Query:
    """
```

这是一个复杂的提示，让我们一步一步来看：

首先，告诉模型我提供了4个工具，让它自己去查询这4个工具的元数据。`function_to_json`函数返回的内容如下：

```json
{
  "name": "get_weather",
  "description": "Get the current weather given a city.",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "str"
      }
    }
  },
  "returns": "str"
}
```

这一步就是让模型根据这几个函数的元数据来理解函数，尤其是`description`写的应该尽量详细。

第二步提示模型作出自己的判断，根据上面提供的工具选择一个或多个进行调用，并指定了模型返回数据格式——`JSON`以及这个`JSON`的`schema`。

第三步等待用户的问题。

## 完整代码

```python
import inspect
import json
import requests
from typing import get_type_hints


def generate_full_completion(model: str, prompt: str) -> dict[str, str]:
    params = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(
        "http://localhost:11434/api/generate",
        headers={"Content-Type": "application/json"},
        data=json.dumps(params),
        timeout=60,
    )
    return json.loads(response.text)


def get_gas_prices(city: str) -> float:
    """Get gas prices for specified cities."""
    print(f'Get gas prices for {city}.')


def github(project: str) -> str:
    '''Get the infomations such as author from github with the project name.'''
    print(f'Access the github for {project}.')


def get_weather(city: str) -> str:
    """Get the current weather given a city."""
    print(f'Getting weather for {city}.')


def get_directions(start: str, destination: str) -> float:
    """Get directions from Google Directions API.
    start: start address as a string including zipcode (if any)
    destination: end address as a string including zipcode (if any)"""
    print(f'Get directions for {start} {destination}.')


def get_type_name(t):
    name = str(t)
    if "list" in name or "dict" in name:
        return name
    else:
        return t.__name__


def function_to_json(func):
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    function_info = {
        "name": func.__name__,
        "description": func.__doc__,
        "parameters": {"type": "object", "properties": {}},
        "returns": type_hints.get("return", "void").__name__,
    }

    for name, _ in signature.parameters.items():
        param_type = get_type_name(type_hints.get(name, type(None)))
        function_info["parameters"]["properties"][name] = {"type": param_type}

    return json.dumps(function_info, indent=2)


def main():
    functions_prompt = f"""
You have access to the following tools:
{function_to_json(get_weather)}
{function_to_json(get_gas_prices)}
{function_to_json(get_directions)}
{function_to_json(github)}

You must follow these instructions:
Always select one or more of the above tools based on the user query
If a tool is found, you must respond in the JSON format matching the following schema:
{{
   "tools": {{
        "tool": "<name of the selected tool>",
        "tool_input": <parameters for the selected tool, matching the tool's JSON schema
   }}
}}
If there are multiple tools required, make sure a list of tools are returned in a JSON array.
If there is no tool that match the user request, you must respond empty JSON {{}}.

User Query:
    """

    GPT_MODEL = "mistral:7b-instruct-v0.2-q8_0"

    prompts = [
        "What's the weather like in Beijing?",
        "What is the distance from Shanghai to Hangzhou and how much do I need to fill up the gas in advance to drive from Shanghai to Hangzhou?",
        "Who's the author of the 'snake-game' on github?",
        "What is the exchange rate between US dollar and Japanese yen?",
    ]

    for prompt in prompts:
        print(f"❓{prompt}")
        question = functions_prompt + prompt
        response = generate_full_completion(GPT_MODEL, question)
        try:
            data = json.loads(response.get("response", response))
            # print(data)
            for tool_data in data["tools"]:
                execute_fuc(tool_data)
        except Exception:
            print('No tools found.')
        print(f"Total duration: {int(response.get('total_duration')) / 1e9} seconds")


def execute_fuc(tool_data):
    func_name = tool_data["tool"]
    func_input = tool_data["tool_input"]

    # 获取全局命名空间中的函数对象
    func = globals().get(func_name)

    if func is not None and callable(func):
        # 如果找到了函数并且是可调用的，调用它
        func(**func_input)
    else:
        print(f"Unknown function: {func_name}")


if __name__ == "__main__":
    main()
```

整段代码就是用来测试模型对问题的理解能力以及是否能正确判断调用哪个工具的。

我们来看下设定的4个问题：

```python
  "What's the weather like in Beijing?",
  "What is the distance from Shanghai to Hangzhou and how much do I need to fill up the gas in advance to drive from Shanghai to Hangzhou?",
  "Who's the author of the 'snake-game' on github?",
  "What is the exchange rate between US dollar and Japanese yen?",
```

按照我们的设想，如果模型理解了我提供的工具的功能以及读懂了用户的问题，应该按照以下规则选择工具：

- 问题1应该对应的是`get_weather('Beijing')`
- 问题2应该对应的是`get_directions('Shanghai', 'Hangzhou')`和`get_gas_prices('Shanghai')`
- 问题3应该对应的是`github('snake-game')`
- 问题4应该没有对应的函数，模型不选择任何工具

下一步，我们也写好了代码进行测试，我们在工具函数里进行参数打印，以查看是否达到我们的预期。
## 结果

```
❓What's the weather like in Beijing?
Getting weather for Beijing.
Total duration: 3.481918084 seconds

❓What is the distance from Shanghai to Hangzhou and how much do I need to fill up the gas in advance to drive from Shanghai to Hangzhou?
Get directions for Shanghai, China Hangzhou, China.
Get gas prices for Shanghai.
Total duration: 5.467253959 seconds

❓Who's the author of the 'snake-game' on github?
Access the github for snake-game.
Total duration: 2.510993791 seconds

❓What is the exchange rate between US dollar and Japanese yen?
{}
No tools found.
Total duration: 0.200526292 seconds
```

## 总结

本篇文章介绍了使用`function-calling`使得`Ollama`模型具备可以调用外部工具的能力。也对一些场景进行了测试，希望通过本系列的3篇文章，使大家对本地运行大语言模型有一些深入的了解。

这次的文章就到这里了，下回我们将继续介绍更多本地`LLM`的实用场景。