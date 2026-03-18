"""
路径工具类
"""
import os


def get_project_root() -> str:
    """
    获取工程的根目录
    :return: 根目录
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_abs_path(relative_path: str) -> str:
    """
    获取绝对路径
    :param relative_path: 指定文件的相对路径
    :return: 指定文件的绝对路径
    """
    return os.path.join(get_project_root(), relative_path)


if __name__ == '__main__':
    print(get_project_root())
    print(get_abs_path('data/'))
    print(get_abs_path('md5.txt'))




