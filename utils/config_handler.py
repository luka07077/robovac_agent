"""
获取配置文件
"""
import yaml
from utils.path_tool import get_abs_path


def load_config(config_file: str, encoding: str='utf-8') -> dict:
    with open(config_file, 'r', encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


# 创建全局实例
common_config = load_config(get_abs_path('conf/common_config.yaml'))
rag_config = load_config(get_abs_path('conf/rag_config.yaml'))
chroma_config = load_config(get_abs_path('conf/chroma_config.yaml'))
prompts_config = load_config(get_abs_path('conf/prompts_config.yaml'))
agent_config = load_config(get_abs_path('conf/agent_config.yaml'))
chat_config = load_config(get_abs_path('conf/chat_config.yaml'))


if __name__ == '__main__':
    print(rag_config['chat_model_name'])




