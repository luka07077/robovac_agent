from abc import ABC, abstractmethod
from typing import Optional

from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from utils.config_handler import rag_config


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass

class DashScopeEmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Embeddings | BaseChatModel:
        return DashScopeEmbeddings(model=rag_config['embedding_model_name'])

class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Embeddings | BaseChatModel:
        return ChatTongyi(model=rag_config['chat_model_name'])


# 创建全局模型
chat_model = ChatModelFactory().generator()
embedding_model = DashScopeEmbeddingsFactory().generator()




