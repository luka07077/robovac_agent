"""
文件会话记忆存储
"""
import os, json
from typing import Sequence
from utils.config_handler import chat_config
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory

from utils.path_tool import get_abs_path


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id, storage_path):
        # 会话ID
        self.session_id = session_id
        # 存储文件夹路径
        self.storage_path = storage_path
        # 文件路径
        self.file_path = os.path.join(self.storage_path, self.session_id)

        # 文件不存在则创建
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # Sequence类似于list
        # 已有的消息
        all_messages = list(self.messages)
        # 添加新消息
        all_messages.extend(messages)

        # 将数据同步写入到本地文件中
        # message_to_dict: 单个消息对象转为字典
        serialized = [message_to_dict(message) for message in all_messages]

        # 写入文件
        with open(self.file_path, "w", encoding="utf-8") as f:
            # 将Python对象（如dict、list）序列化为JSON格式，并直接写入到文件中
            json.dump(serialized, f)

    @property
    def messages(self) -> Sequence[BaseMessage]:
        # @property装饰器将message方法转为成员变量
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                # 将JSON文件反序列化，解析成原生的Python对象（通常dict或list）
                serialized = json.load(f)
                # 将[dict, dict, ...] 转为 [BaseMessage, BaseMessage, ...]
                return messages_from_dict(serialized)
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)


# 获取指定会话(用户)ID的历史会话的函数
def get_history(session_id):
    return FileChatMessageHistory(
        session_id,
        get_abs_path(chat_config['chat_history_store_path'])
    )
