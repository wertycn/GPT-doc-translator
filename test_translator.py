import os
import subprocess
import shutil
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

from langchain.prompts import PromptTemplate

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import json
import requests
import re


chat = ChatOpenAI()


def spliter_markdown(text):
    """将 markdown 文本分片为代码块和普通文本两种类型"""
    result = []
    current_chunk_type = 'text'
    current_chunk = []
    current_length = 0

    # 逐行读取文本
    for line in text.split('\n'):

        # 如果当前行是否为代码块  并且现有分片类型为text 则切换分片为代码块， 并创建新分片

        if line.strip().startswith('```'):
            if current_chunk_type == 'code':  # 关闭当前代码块
                # print("======代码块结束======")
                # print("当前分片:"+current_chunk_type+", 当前行:"+ line)
                current_chunk.append(line)
                result.append({'type': 'code', 'content': '\n'.join(current_chunk)})
                current_chunk_type = 'text'
                current_length = 0

                current_chunk = []
            elif current_chunk_type == "text" and len(current_chunk) > 0:
                # print("======代码块开始,新建分片,保存历史分片======")
                result.append({'type': 'text', 'content': '\n'.join(current_chunk)})
                current_chunk_type = 'code'
                current_chunk = []
                current_length = 0

                # print("当前分片:"+current_chunk_type+", 当前行:"+ line)
                current_chunk.append(line)

            else:  # 开启新的代码块
                # print("======代码块开始,新建分片======")

                current_chunk_type = 'code'
                current_chunk = []
                # print("当前分片:"+current_chunk_type+", 当前行:"+ line)
                current_chunk.append(line)
                current_length = len(line)

        elif current_length + len(line) > 1000 and current_chunk_type == 'text':
            result.append({'type': 'text', 'content': '\n'.join(current_chunk)})
            current_chunk = []
            current_chunk.append(line)
            current_length = len(line)
            # print("size tool big new chunk...")


        else:
            # print("当前分片:"+current_chunk_type+", 当前行:"+ line)
            current_chunk.append(line)
            current_length = current_length + len(line)

    # 添加最后一个分片
    if current_chunk_type == 'text':
        result.append({'type': 'text', 'content': '\n'.join(current_chunk)})
    else:
        result.append({'type': 'code', 'content': '\n'.join(current_chunk)})

    return result


# 获取当前分支最新commit id
def get_latest_commit():
    result = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
    return result.strip().decode()


# 读取执行记录存档中的上次commit id


def get_last_commit():
    if os.path.exists('.log/commit.log'):
        with open('.log/commit.log', 'r') as f:
            return f.readline().strip()
    else:
        return None


# 将本次commit id保存到执行记录存档中


def save_commit(commit_id):
    if not os.path.exists('.log'):
        os.makedirs('.log')
    with open('.log/commit.log', 'w') as f:
        f.write(commit_id)


# 判断文件是否符合白名单要求


def is_valid_file(filename, whitelist):
    for ext in whitelist:
        if filename.endswith(ext):
            return True
    return False


# 翻译文档


def translate_doc(doc_path, lang):
    with open(doc_path, 'r') as f:
        text = f.read()
    translator = Translator()
    result = translator.translate(text, dest=lang)
    translated_text = result.text
    translated_path = 'docs_{}'.format(lang)
    if not os.path.exists(translated_path):
        os.makedirs(translated_path)
    shutil.copy(doc_path, os.path.join(
        translated_path, os.path.basename(doc_path)))
    with open(os.path.join(translated_path, os.path.basename(doc_path)), 'w') as f:
        f.write(translated_text)


# 获取变更的文件列表


def get_changed_files(last_commit):
    if last_commit is None:
        # 遍历项目中的docs目录下的所有文件
        docs_path = os.path.join(os.getcwd(), "docs")
        files = []
        for root, dirs, filenames in os.walk(docs_path):
            for filename in filenames:
                path = os.path.join(root, filename)
                if os.path.isfile(path):
                    files.append(path)
        return files
    result = subprocess.check_output(
        ['git', 'diff', '--name-only', last_commit, 'HEAD'])
    return result.strip().decode().split('\n')


def get_target_path(file_path, lang):
    # 以 _ 分割文件名获取文件名和扩展名
    name, ext = os.path.splitext(os.path.basename(file_path))
    # 拼接翻译后的文件名和路径
    new_name = '{}_{}{}'.format(name, lang, ext)
    target_dir = os.path.join('docs_{}'.format(
        lang), os.path.relpath(os.path.dirname(file_path), 'docs'))
    target_path = os.path.join(target_dir, new_name)
    return target_path


# 遍历docs目录，翻译变更的文档
def translate_docs(lang, whitelist, changed_files):
    docs_dir = 'docs'
    valid_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if is_valid_file(file_path, whitelist) and file_path in changed_files:
                valid_files.append(file_path)
                print('Translating file: {}'.format(file_path))
                translate_doc(file_path, lang)
            elif file_path in changed_files:
                target_path = get_target_path(file_path, lang)
                if not os.path.exists(os.path.dirname(target_path)):
                    os.makedirs(os.path.dirname(target_path))
                shutil.copy2(file_path, target_path)
                print('Copying file: {}'.format(file_path))

    for file_path in valid_files:
        target_path = get_target_path(file_path, lang)
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))
        shutil.copy2(file_path, target_path)
        print('Copying file: {}'.format(file_path))


def get_relative_paths(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            file_list.append(relative_path)
    return file_list


def filter_files(file_list, white_list):
    white_files = []
    other_files = []
    for file in file_list:
        ext = os.path.splitext(file)[1].lstrip('.')
        if ext in white_list:
            white_files.append(file)
        else:
            other_files.append(file)
    return white_files, other_files


def translate_files(file_paths, source_lang, target_lang, destination_dir, source_dir):
    for file_path in file_paths:
        # 获取完整的文件路径
        file_path = os.path.join(source_dir, file_path)
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        print("即将翻译：" + file_path)
        # 翻译文本
        translated_text = translate_markdown(text, source_lang, target_lang)
        # 获取目标文件路径，并创建目录
        target_file_path = os.path.join(
            destination_dir, os.path.relpath(file_path, source_dir))
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        # 写入翻译后的文本到目标文件
        with open(target_file_path, 'w', encoding='utf-8') as f:
            f.write(translated_text)


def translate_markdown(content, source_lang, target_lang):
    chunk = spliter_markdown(content)
    result = []
    for item in chunk:
        if item['type'] == "text" and len(item['content'].strip()) > 0:
            print("翻译中 input=" + item['content'])
            res = translate(item['content']).content
            print("\n\n 翻译结果=" + res)
            result.append(res)
        else:
            result.append(item['content'])

    return "\n".join(result)


def translate(text):
    return chat([
        SystemMessage(content="""
你是一款专业的翻译程序，我需要协助翻译 英文技术文档为中文， 并使用风格转换使得翻译文本更符合中文习惯
我会输入markdown格式的文本内容，翻译过程中需要保持markdown 格式不变，除翻译结果外，不需要额外的解释,如果输入内容为空，请返回空内容无需增加解释
准备好了吗？
        """),
        AIMessage(content="好了，请输入需要翻译的内容"),
        HumanMessage(content="hello"),
        AIMessage(content="你好"),
        HumanMessage(content="\n"),
        AIMessage(content="\n"),
        HumanMessage(content="""
# Quickstart Guide


This tutorial gives you a quick walkthrough about building an end-to-end language model application with LangChain.

        """),
        AIMessage(content="""
# 快速上手指南


本教程将为您快速介绍如何使用LangChain构建一个端到端的语言模型应用程序。        
        """),
        HumanMessage(content=text)
    ])


def copy_files(file_paths, source_dir, destination_dir):
    for file_path in file_paths:
        # 获取完整的文件路径
        file_path = os.path.join(source_dir, file_path)
        # 获取目标文件路径，并创建目录
        target_file_path = os.path.join(
            destination_dir, os.path.relpath(file_path, source_dir))
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        # 复制文件
        shutil.copy2(file_path, target_file_path)


# 命令行交互界面


def main():
    files = get_relative_paths("docs")
    trans_files, wait_copy_files = filter_files(files, ['md'])

    print(trans_files, wait_copy_files)
    translate_files(trans_files, "en", "zh", "docs_zh", "docs")

    copy_files(wait_copy_files, "docs", "docs_zh")

    # lang = 'zh'
    # whitelist = ["md"]
    # last_commit = get_last_commit()
    # current_commit = get_latest_commit()
    # changed_files = get_changed_files(last_commit)
    # print(changed_files)
    # translate_docs(lang, whitelist, changed_files)
    # save_commit(current_commit)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error: {}'.format(str(e)))