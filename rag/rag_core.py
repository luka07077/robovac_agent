"""
RAG核心服务
"""
from model.factory import chat_model
from utils import format_parser
from utils.config_handler import chat_config
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from sqlalchemy.orm.attributes import get_history

from rag.vector_stores import vector_store_client
from langchain_core.runnables.history import RunnableWithMessageHistory
from rag.file_chat_history_store import get_history
from utils.prompt_handler import rag_summary_prompt


class RagCoreService:
    def __init__(self):
        # 向量存储
        self.vector_service = vector_store_client

        # 提示词模板
        self.prompt_template = rag_summary_prompt

        # LLM
        self.chat_model = chat_model

        # 执行chain
        self.chain = self.__get_chain()
        self.conversion_chain = self.__get_conversion_chain()

    def __get_chain(self):
        """
        获取最终的执行chain
        :return:
        """
        # 将原先的普通字典替换为 RunnableParallel 对象
        user_inputs = RunnableParallel(
            input=RunnablePassthrough(),
            context=format_parser.get_format_retriever_input_parser() |
                    self.vector_service.get_retriever() |
                    format_parser.get_format_retriever_output_parser()
        )

        return (
                user_inputs | format_parser.get_format_prompt_input_parser() |
                self.prompt_template | format_parser.get_print_parser() |
                self.chat_model | format_parser.get_str_parser()
        )

    def __get_conversion_chain(self, session_id=None):
        base_chain = self.__get_chain()

        return RunnableWithMessageHistory(
            base_chain,
            get_history,
            input_messages_key='input',
            history_messages_key='chat_history'
        )

    def rag_summary(self, query: str) -> str:
        # return self.chain.invoke({'input': f'{query}'})
        return self.conversion_chain.invoke({'input': f'{query}'}, chat_config['session_config'])


# 创建一个全局实例
rag_core_service = RagCoreService()


if __name__ == '__main__':
    rag_core = RagCoreService()
    res = rag_core.rag_summary('Hello')
    # res = rag_core.chain.invoke({'input': 'Hello, who are you?'})
    # res = rag_core.conversion_chain.invoke({'input': '测试一下'}, chat_config['session_config'])
    print(res)
