---
author: caol64
title: Run a large language models locally (2)
slug: run-a-large-language-model-locally-2
description: Make your local large language models (LLMs) smarter! This guide shows how to use LangChain and RAG to let them retrieve data from external knowledge bases, improving answer accuracy.
date: 2024-03-04 11:18:00
draft: false
ShowToc: true
TocOpen: true
tags:
  - Ollama
  - AI
categories:
  - Tutorial
---
In the previous [article](https://babyno.top/en/posts/2024/02/running-a-large-language-model-locally/), we demonstrated how to run large language models (LLMs) locally using `Ollama`. This article focuses on enhancing LLM accuracy by allowing them to retrieve custom data from external knowledge bases, making them appear "smarter."

This article involves the concepts of `LangChain` and `RAG`, which will not be explained in detail here.

## Prepare the Model

Visit `Ollama`'s model page, search for `qwen`, and this time we will use the "[Tongyi Qianwen](https://ollama.com/library/qwen:7b)" model, which has a better understanding of Chinese semantics, for the experiment.

## Run the Model

```shell
ollama run qwen:7b
```

## First Round of Testing

Write the following code:

```python
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


model_local = ChatOllama(model="qwen:7b")
template = "{topic}"
prompt = ChatPromptTemplate.from_template(template)
chain = model_local | StrOutputParser()
print(chain.invoke("身长七尺，细眼长髯的是谁？"))
```

The model returns the following answer:

> 这句话描述的是中国古代文学作品《三国演义》中的角色刘备。刘备被描绘为一位身高七尺（约1.78米），眼睛细小但有神，长着长须的蜀汉开国皇帝。(This sentence describes Liu Bei, a character in the Chinese classical novel "Romance of the Three Kingdoms." Liu Bei is depicted as the emperor of Shu Han, who is seven feet tall (about 1.78 meters), has small but bright eyes, and a long beard.)

As you can see, I asked the model a question: "Who is seven feet tall, with thin eyes and a long beard?" This is an open-ended question with no specified context, and the answer is uncertain. The answer given by the model is "Liu Bei." As a model trained on Chinese data, it is not surprising that it can associate the question with the characters in the Three Kingdoms. However, the answer is still incorrect.

## Introducing RAG

Retrieval Augmented Generation (RAG) works by retrieving facts from an external knowledge base in a shared semantic space and using these facts as part of the decision-making process to improve the accuracy of the large language model. Therefore, in the second round of testing, we will let the model read a pre-prepared chapter of "Romance of the Three Kingdoms" before answering the question, allowing it to find the answer we need in this chapter.

The workflow of RAG before: ask the model a question -> the model queries the data from the trained data -> organizes the language -> generates the answer.

The workflow of RAG after: read the document -> tokenize -> embed -> store the embedded data in a vector database -> ask the model a question -> the model queries the data from the vector database -> organizes the language -> generates the answer.

## Embedding

In artificial intelligence, `embedding` is the process of vectorizing data. It can be understood as the process of converting human language into the computer language required by large language models. Before we start the second round of testing, let's download an embedding model: [nomic-embed-text](https://ollama.com/library/nomic-embed-text) . It can enable our `Ollama` to vectorize documents.

```shell
ollama run nomic-embed-text
```

## Using LangChain

Next, we need a `Document loaders`, documentation: [https://python.langchain.com/docs/modules/data_connection/document_loaders/](https://python.langchain.com/docs/modules/data_connection/document_loaders/).

```python
from langchain_community.document_loaders import TextLoader  
  
loader = TextLoader("./index.md")  
loader.load()
```

Next, we need a tokenizer `Text Splitter`, documentation: [https://python.langchain.com/docs/modules/data_connection/document_transformers/split_by_token](https://python.langchain.com/docs/modules/data_connection/document_transformers/split_by_token).

```python
from langchain_text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
  chunk_size=100, chunk_overlap=0
)
texts = text_splitter.split_text(state_of_the_union)
```

Next, we need a vector database to store the data vectorized using the `nomic-embed-text` model. Since this is a test, we will use the memory-based `DocArray InMemorySearch`, documentation: [https://python.langchain.com/docs/integrations/vectorstores/docarray_in_memory](https://python.langchain.com/docs/integrations/vectorstores/docarray_in_memory).

```python
embeddings = OllamaEmbeddings(model='nomic-embed-text')
vectorstore = DocArrayInMemorySearch.from_documents(doc_splits, embeddings)
```

**Second Round of Testing**

First, download the test [document](http://babyno.top/data/%E4%B8%89%E5%9B%BD%E6%BC%94%E4%B9%89.txt). This document will act as our external database for the model to search. Note that this document mentions:

> 忽见一彪军马，尽打红旗，当头来到，截住去路。为首闪出一将，身长七尺，细眼长髯，官拜骑都尉，沛国谯郡人也，姓曹，名操，字孟德。 (Suddenly, a mighty army with red flags appeared in front, blocking their way. A general emerged from the front, seven feet tall with thin eyes and a long beard. He was Cao Cao, courtesy name Mengde, from Peiguo County in Qiao Commandery.)

Here's the code for the second round:

```python
from langchain_community.document_loaders import TextLoader
from langchain_community import embeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.embeddings import OllamaEmbeddings

model_local = ChatOllama(model="qwen:7b")

# 1. Read and tokenize the document
documents = TextLoader("../../data/三国演义.txt").load()
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
doc_splits = text_splitter.split_documents(documents)

# 2. Embed and store
embeddings = OllamaEmbeddings(model='nomic-embed-text')
vectorstore = DocArrayInMemorySearch.from_documents(doc_splits, embeddings)
retriever = vectorstore.as_retriever()

# 3. Ask the model a question
template = """Answer the question based only on the following context:
{context}
Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = (
  {"context": retriever, "question": RunnablePassthrough()}
  | prompt
  | model_local
  | StrOutputParser()
)
print(chain.invoke("身长七尺，细眼长髯的是谁？"))
```

**The model's answer for the second round:**

> 身长七尺，细眼长髯的人物是曹操，字孟德，沛国谯郡人。在《三国演义》中，他是主要人物之一。(The person who is seven feet tall with thin eyes and a long beard is Cao Cao, courtesy name Mengde, from Peiguo County in Qiao Commandery. In Romance of the Three Kingdoms, he is one of the main characters.)

As you can see, after using `RAG`, the model provides the correct answer.

## Conclusion

In this article, we `fine-tuned` a large language model using `LangChain` and `RAG`. This allows the model to search within a document we provided before generating an answer, resulting in more accurate answers.

`RAG` stands for Retrieval Augmented Generation. Its primary function is to enable users to provide the model with additional information. This is very useful because we can provide the model with various knowledge bases, allowing it to take on various roles.

`LangChain` is a framework designed for developing large language model applications. It includes many helpful functionalities, such as text reading, tokenization, and embedding. By leveraging these built-in features, we can easily build a RAG application.

This concludes this article. In the next one, we will continue to explore more practical applications of local LLMs.