"""
构建 chain 中所需解析器
"""
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda


def __print_prompt(prompt_template):
    """
    提示词打印
    :param prompt_template:
    :return:
    """
    # print('=' * 10, '提示词为: ', prompt_template.to_string(), '=' * 10)
    # print()
    return prompt_template

def __format_retriever_output(docs: list[Document]):
    """
    格式化检索器结果
    :param docs:
    :return:
    """
    if not docs:
        return '暂无参考资料'
    # print(docs)
    return str([doc.page_content for doc in docs])

def __format_retriever_input(input_dict: dict) -> str:
    """
    格式化检索器输入
    :param input_dict:
    :return:
    """
    # print(input_dict['input'])
    return input_dict['input']

def __format_prompt_input(input_dict: dict) -> dict:
    ret_dict = {
        'input': input_dict['input']['input'],
        'context': input_dict['context'],
    }

    if 'chat_history' in input_dict['input']:
        ret_dict['chat_history'] = input_dict['input']['chat_history']

    return ret_dict

def get_str_parser():
    return StrOutputParser()

def get_print_parser():
    return RunnableLambda(__print_prompt)

def get_format_retriever_output_parser():
    return RunnableLambda(__format_retriever_output)

def get_format_retriever_input_parser():
    return RunnableLambda(__format_retriever_input)

def get_format_prompt_input_parser():
    return RunnableLambda(__format_prompt_input)

