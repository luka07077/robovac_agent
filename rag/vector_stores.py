"""
向量存储
"""
import os

from langchain_core.vectorstores import VectorStoreRetriever
from utils.config_handler import chroma_config
from model.factory import embedding_model
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.file_handler import listdir_with_allowed_types, get_file_md5, check_md5_exist, load_document, text_loader, \
    pdf_loader, save_md5
from utils.logger_handler import logger
from utils.path_tool import get_abs_path

persist_dir = get_abs_path(chroma_config['persist_directory'])
original_file_dir = get_abs_path(chroma_config['original_file_dir'])
original_file_dir_tmp = get_abs_path(chroma_config['original_file_dir_tmp'])


class VectorStores:
    def __init__(self):
        # 确保向量数据库存储路径存在
        os.makedirs(persist_dir, exist_ok=True)

        # 向量数据库
        self.vector_db = Chroma(
            collection_name=chroma_config['collection_name'],
            embedding_function=embedding_model,
            persist_directory=persist_dir,
        )

        # 文本分割器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config['chunk_size'],
            chunk_overlap=chroma_config['chunk_overlap'],
            separators=chroma_config['separators'],
            length_function=len
        )

    def get_vector_db(self):
        return self.vector_db

    def get_splitter(self):
        return self.splitter

    def get_retriever(self) -> VectorStoreRetriever:
        """
        获取向量检索器
        :return: VectorStoreRetriever
        """
        return self.vector_db.as_retriever(
            search_type=chroma_config['retrieve_search_type_default'],  # 默认就是相似度搜索
            search_kwargs={
                "k": chroma_config['retrieve_search_max_return_num'],  # 把你原本的 k=3 参数放在这里
                # "score_threshold": chroma_config['retrieve_search_score_threshold']  # 可选, 只有匹配度大于80%的结果才返回
            }
        )

    def upload_document(self):
        """
        从data文件夹中读取文件, 转为向量存入向量库
        根据文件的MD5做去重处理
        :return: True-成功 False-失败
        """
        file_path_list = listdir_with_allowed_types(original_file_dir)
        for file_path in file_path_list:
            # 获取文件MD5
            file_md5_hex = get_file_md5(file_path)

            # 校验
            if check_md5_exist(file_md5_hex):
                logger.info(f"{file_path} exist")
                continue

            # 获取docs
            try:
                doc_list = load_document(file_path)
                if doc_list is None:
                    logger.info(f"{file_path} 没有有效文本")
                    continue

                split_doc_list = self.get_splitter().split_documents(doc_list)
                self.get_vector_db().add_documents(split_doc_list)

            except Exception as e:
                logger.error(f'error: {str(e)}', exc_info=True)

    def upload_document_from_web(self, file_bytes: bytes, file_name: str) -> str:
        """
        接收从 Streamlit 传来的文件流，并存入向量库。
        支持 .txt, .pdf, .docx
        """
        # 1. 拼接暂存路径，将网页传来的二进制流保存到本地
        save_path = os.path.join(original_file_dir_tmp, file_name)
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        # 2. 获取文件MD5并校验是否已存在（复用你现有的工具方法）
        file_md5_hex = get_file_md5(save_path)
        logger.info(f'{file_md5_hex}')

        if check_md5_exist(file_md5_hex):
            logger.info(f"{file_name} 已存在于知识库")
            return f"文件 {file_name} 已存在，请勿重复上传。"

        # 3. 根据文件后缀名选择合适的 LangChain 加载器
        file_extension = os.path.splitext(file_name)[1].lower()
        try:
            if file_extension == '.txt':
                load_docs = text_loader(save_path)
            elif file_extension == '.pdf':
                load_docs = pdf_loader(save_path)
            # elif file_extension in ['.doc', '.docx']:
            #     # 注意：处理 doc/docx 推荐使用 Docx2txtLoader
            #     loader = Docx2txtLoader(save_path)
            else:
                return f"暂不支持的文件格式: {file_extension}"

            # 读取文档
            doc_list = load_docs
            if not doc_list:
                logger.info(f"{file_name} 没有有效文本")
                return f"文件 {file_name} 中未读取到有效文本。"

            # 4. 文本切分与向量入库
            split_doc_list = self.get_splitter().split_documents(doc_list)
            self.get_vector_db().add_documents(split_doc_list)

            # 5.存储该文件内容存入md5文件
            save_md5(file_md5_hex)

            logger.info(f"{file_name} 上传并向量化成功")
            return f"🎉 文件 {file_name} 成功载入知识库！"

        except Exception as e:
            logger.error(f'上传解析 error: {str(e)}', exc_info=True)
            return f"❌ 文件 {file_name} 解析失败: {str(e)}"


# 创建一个全局实例
vector_store_client = VectorStores()

if __name__ == '__main__':
    vector = VectorStores()
    retriever = vector.get_retriever()
    print(type(retriever))
