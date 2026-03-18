"""
文件处理工具类
"""
import hashlib
import os
from typing import Literal

from langchain_core.documents import Document
from utils.config_handler import chroma_config
from utils.path_tool import get_abs_path
from utils.logger_handler import logger
from langchain_community.document_loaders import PyPDFLoader, TextLoader

# md5存储文件路径定义
md5_path = get_abs_path(chroma_config['md5_path'])


def __is_file(file_path: str) -> bool:
    if not (os.path.exists(file_path)):
        logger.error(f'{file_path} is not exist')
        return False

    if not (os.path.isfile(file_path)):
        logger.error(f'{file_path} is not a file')
        return False

    return True


def check_md5_exist(md5_str: str) -> bool:
    """
    检查传入的md5字符串是否存在
    :param md5_str: 传入的md5字符串
    :return: False-不存在 True-存在
    """
    if md5_str is None:
        logger.warning("传入的 MD5 为空，跳过保存。")
        return False

    if not (os.path.exists(md5_path)):
        with open(md5_path, 'w', encoding='utf-8') as f:
            pass
        return False
    else:
        with open(md5_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if md5_str == line.strip():
                    return True
            return False


def save_md5(md5_str: str):
    """
    将传入的md5字符串保存到文件中
    """
    res = check_md5_exist(md5_str)

    if not res:
        with open(md5_path, 'a', encoding='utf-8') as f:
            f.write(md5_str + '\n')


def get_str_md5(text_str: str, encoding: str = 'utf-8') -> str:
    """
    将传入的字符串转为md5, 其中两个相同字符串的md5一定相等
    :param text_str: 输入的字符串
    :param encoding: 编码格式, 默认为"utf-8"
    :return: 32位的md5十六进制字符串
    """
    # 将str转为bytes数组
    str_bytes = text_str.encode(encoding=encoding)

    # 得到md5的十六进制字符串
    return hashlib.md5(str_bytes).hexdigest()


def get_file_md5(file_path: str) -> str | None:
    if not __is_file(file_path):
        return None

    md5_obj = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:  # 必须二进制读取
            while chunk := f.read(chroma_config['md5_chunk_size']):
                md5_obj.update(chunk)

            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f'计算文件: {file_path} 的md5失败, error: {str(e)}')
        return None


def listdir_with_allowed_types(
        dir_path: str,
        allowed_types: tuple[str] = chroma_config['allowed_file_types']
) -> tuple[str] | None:
    """
    返回文件夹内指定类型的文件
    :param dir_path: 文件夹路径
    :param allowed_types: 允许的类型, 例如.txt .pdf等
    :return: 文件tuple
    """
    file_list = []

    if not (os.path.isdir(dir_path)):
        logger.error(f'{dir_path} is not a directory')
        return None

    for f in os.listdir(dir_path):
        if f.endswith(allowed_types):
            file_list.append(os.path.join(dir_path, f))

    return tuple(file_list)


def pdf_loader(file_path: str, mode: Literal["single", "page"]='page',
               password: str=None) -> list[Document] | None:
    """
    加载PDF文件
    :param file_path: 文件路径
    :param mode: 读取模式
    :param password: 文件密码
    :return: list[Document]
    """
    if not __is_file(file_path):
        return None

    return PyPDFLoader(file_path, mode=mode, password=password).load()


def text_loader(file_path: str, encoding: str = 'utf-8') -> list[Document] | None:
    """
    加载TXT文件
    :param file_path: 文件路径
    :param encoding 编码格式
    :return: list[Document]
    """
    if not __is_file(file_path):
        return None

    return TextLoader(file_path, encoding=encoding).load()


def load_document(file_path: str)-> list[Document] | None:
    if file_path.endswith('.pdf'):
        return pdf_loader(file_path)
    elif file_path.endswith('.txt'):
        return text_loader(file_path)
    else:
        return None







