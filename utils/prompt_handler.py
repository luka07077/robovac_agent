"""
提示词处理工具类
"""
from typing import Literal
from utils.config_handler import prompts_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

PM_TYPE = Literal['main_prompt_path', 'rag_summary_prompt_path', 'report_prompt_path']


def load_prompts(pm_type: PM_TYPE) -> str:
    """
    从文件中加载提示词
    :param pm_type: 提示词类型
    :return 提示词str
    """
    try:
        prompt_path = get_abs_path(prompts_config[pm_type])
    except Exception as e:
        logger.error(f'prompts_config中不存在{pm_type}')
        raise e

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f'解析提示词出错, 类型为{prompt_path}, error: {str(e)}')
        raise e


def load_rag_prompt_from_file() -> ChatPromptTemplate:
    """
    从 txt 文件加载rag服务提示词，并保留 system, chat_history, user 等角色结构

    :return: 组装好的 ChatPromptTemplate
    """
    # 1. 校验文件是否存在
    try:
        prompt_path = get_abs_path(prompts_config['rag_summary_prompt_path'])
    except Exception as e:
        logger.error(f'prompts_config中不存在[rag_summary_prompt_path]')
        raise e

    # 2. 读取文本文件内容
    with open(prompt_path, 'r', encoding='utf-8') as file:
        system_prompt_content = file.read()

    # 3. 按照期望的格式构建 Message 列表
    messages = [
        # 加载身份设定、参考资料 {context} 和约束条件
        ('system', system_prompt_content),

        # 插入历史会话占位符
        MessagesPlaceholder(variable_name='chat_history'),
    ]

    # 4. 返回 LangChain 识别的 Prompt Template
    return ChatPromptTemplate.from_messages(messages)


# 创建全局实例
main_prompt = load_prompts('main_prompt_path')
report_prompt = load_prompts('report_prompt_path')
rag_summary_prompt = load_rag_prompt_from_file()

if __name__ == '__main__':
    print(main_prompt)
