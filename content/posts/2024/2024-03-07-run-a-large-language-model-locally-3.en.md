---
author: caol64
title: Run a large language models locally (3) - Enabling the Model to Use Tools Autonomously
slug: run-a-large-language-model-locally-3
description: Run LLMs on your machine and extend their capabilities!  This guide explores function calling in Ollama, allowing the model to connect with external tools and become more intelligent.
date: 2024-03-07 14:24:56
draft: false
ShowToc: true
TocOpen: true
tags:
  - Ollama
  - LLM
  - Function Calling
  - Local AI
  - Tutorial
categories:
  - AI
---
This article is the third in a series on running large language models (LLMs) locally. In the previous two articles, we introduced how to run `Ollama` locally and how to fine-tune the model's answers by providing an external database. This article will continue to explore how to use the `function-calling` feature to extend the model's capabilities and make it go further on the road to "intelligence".

## **Function-calling**

According to the `OpenAI` official documentation, `function-calling` is a way for large language models to connect to external tools. In short, **developers provide the model with a number of tools (functions) in advance. After the model understands the user's question, it decides whether to call the tool to obtain more context information to help the model make better decisions.**

For example, in the previous [article](https://babyno.top/en/posts/2024/03/run-a-large-language-model-locally-2/), we used `Document loaders` to provide pre-prepared text as context to the model. With `function-calling`, we only need to provide a "search function" as a tool, and the model can search through the search engine and get the answer by itself.

Thanks to the latest model training, the current model can detect when to call a function (depending on the input) and respond to JSON in a way that is closer to the function signature than previous models.

## **Use case**

What are the uses of `function-calling`? The official website provides 3 examples:

- **Create an assistant that answers questions by calling external APIs**
- **Convert natural language to API calls**
- **Extract structured data from text**

Below we will understand `function-calling` step by step.

## **Defining Functions**

First, let's define 4 `functions`, each with a different usage scenario.

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

## **Defining Prompts**

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

This is a complex prompt, let's take a look at it step by step:

First, it tells the model that I have provided 4 tools and let it query the metadata of these 4 tools. The content returned by the `function_to_json` function is as follows:

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

This step is to let the model understand the function based on the metadata of these functions, especially the `description` should be written as detailed as possible.

The second step prompts the model to make its own judgment. Based on the provided tools above, it should choose one or more to call and specifies the model's response data format - `JSON` and the `schema` of this `JSON`.

The third step waits for the user's question.

## **Complete Code**

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
        print(f"{prompt}")
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

    func = globals().get(func_name)

    if func is not None and callable(func):
        func(**func_input)
    else:
        print(f"Unknown function: {func_name}")


if __name__ == "__main__":
    main()
```

## **Testing**

This entire code snippet is used to test the model's ability to understand the problem and whether it can correctly determine which tool to call.

Let's take a look at the 4 questions we defined:

```python
  "What's the weather like in Beijing?",
  "What is the distance from Shanghai to Hangzhou and how much do I need to fill up the gas in advance to drive from Shanghai to Hangzhou?",
  "Who's the author of the 'snake-game' on github?",
  "What is the exchange rate between US dollar and Japanese yen?",
```

According to our design, if the model understands the functionalities of the provided tools and comprehends the user's questions, it should choose the tools based on the following rules:

- Question 1 should correspond to `get_weather('Beijing')`
- Question 2 should correspond to `get_directions('Shanghai', 'Hangzhou')` and `get_gas_prices('Shanghai')`
- Question 3 should correspond to `github('snake-game')`
- Question 4 should not have a corresponding function, and the model should not choose any tool

Next, we also wrote code for testing, where we perform parameter printing in the tool functions to see if it meets our expectations.

## **Results**

```
What's the weather like in Beijing?
Getting weather for Beijing.
Total duration: 3.481918084 seconds

What is the distance from Shanghai to Hangzhou and how much do I need to fill up the gas in advance to drive from Shanghai to Hangzhou?
Get directions for Shanghai, China Hangzhou, China.
Get gas prices for Shanghai.
Total duration: 5.467253959 seconds

Who's the author of the 'snake-game' on github?
Access the github for snake-game.
Total duration: 2.510993791 seconds

What is the exchange rate between US dollar and Japanese yen?
{}
No tools found.
Total duration: 0.200526292 seconds
```

## **Summary**

This article introduced how to use `function-calling` to enable the `Ollama` model to call external tools. We also tested some scenarios. Hopefully, through this series of 3 articles, you will have a deeper understanding of running large language models locally.

This is it for this article. In the next one, we will continue to introduce more practical use cases for local LLMs.