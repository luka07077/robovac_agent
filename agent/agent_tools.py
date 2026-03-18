"""
Agent工具定义
"""
import random

import pandas as pd
from langchain_core.tools import tool

from rag.rag_core import rag_core_service
from utils.config_handler import agent_config
from utils.path_tool import get_abs_path


@tool(description="从向量库中检索参考资料")
def rag_summary(query: str) -> str:
    return rag_core_service.rag_summary(query)


@tool(description='获取指定城市的天气')
def get_weather(city: str) -> str:
    return f'{city}的天气为晴天, 气温为29°, 空气湿度较高, 东北风, 风力小于3级, 建议出门携带雨具并注意防暑降温。'


@tool(description='获取用户所在城市名称')
def get_user_location() -> str:
    return random.choice(['深圳', '北京', '上海', '广州', '成都', '杭州', '新加坡', '东京', '纽约'])


@tool(description='获取用户ID')
def get_user_id() -> str:
    return str(random.randint(1001, 1011))


@tool(description='获取当前月份')
def get_current_month() -> str:
    month = random.randint(1, 12)
    return f"2025-{month:02d}"


@tool(description="模拟从外部系统中, 获取指定用户指定月份的使用记录")
def fetch_external_data(user_id: str, month: str) -> str:
    """
    检索指定用户在指定月份的扫地/扫拖机器人完整使用记录。

    :param user_id: 用户ID，纯文本数字字符串，例如 "1001"
    :param month: 月份，严格遵循 "YYYY-MM" 格式，例如 "2025-01"
    :return: 包含清洁效率、耗材状态、使用对比等核心报告数据的字符串
    """
    file_path = get_abs_path(agent_config['record_path'])

    try:
        # 1. 读取 CSV 文件
        # 注意：如果文件中存在空值，fillna('') 可以将 NaN 替换为空字符串，避免报错
        df = pd.read_csv(file_path).fillna('')

        # 2. 统一数据类型：确保用户ID和时间列都是字符串类型，防止类型不匹配导致查不到数据
        df['用户ID'] = df['用户ID'].astype(str)
        df['时间'] = df['时间'].astype(str)

        # 3. 过滤出匹配 user_id 和 month 的数据
        matched_records = df[(df['用户ID'] == user_id) & (df['时间'] == month)]

        # 4. 判断是否查到了数据
        if matched_records.empty:
            return f"系统提示：未查询到用户 {user_id} 在 {month} 的扫地机器人使用记录。"

        # 5. 提取匹配到的第一条数据（假设一个用户一个月只有一条总记录）
        row = matched_records.iloc[0]

        # 6. 拼装结构化的出参字符串
        # 我们使用换行符 \n 将数据清晰地分隔开，这非常利于大模型阅读和提取重点
        report_data = (
            f"--- 用户 {user_id} 的 {month} 月使用记录 ---\n"
            f"【用户特征】: {row.get('特征', '暂无数据')}\n"
            f"【清洁效率】:\n{row.get('清洁效率', '暂无数据')}\n"
            f"【耗材状态】:\n{row.get('耗材', '暂无数据')}\n"
            f"【使用对比】: {row.get('对比', '暂无数据')}"
        )

        return report_data

    except FileNotFoundError:
        return "系统报错：未找到数据文件 records.csv，请检查文件路径。"
    except Exception as e:
        return f"系统报错：读取外部数据时发生未知错误: {str(e)}"


@tool(description='调用后触发中间件自动为报告生成场景动态注入上下文信息，为后续提示词切换提供上下文支撑')
def fill_context_for_report():
    return


if __name__ == '__main__':
    pass

    # res = fetch_external_data('1001', '2025-01')
    # print(res)

    # res = get_current_month()
    # print(res)
