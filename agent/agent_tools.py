"""
Agent工具定义
"""
import random
import requests
import pandas as pd
from langchain_core.tools import tool

from rag.rag_core import rag_core_service
from utils.config_handler import agent_config
from utils.path_tool import get_abs_path


@tool(description="从向量库中检索参考资料")
def rag_summary(query: str) -> str:
    return rag_core_service.rag_summary(query)


# @tool(description='获取指定城市的天气')
# def get_weather(city: str) -> str:
#     return f'{city}的天气为晴天, 气温为29°, 空气湿度较高, 东北风, 风力小于3级, 建议出门携带雨具并注意防暑降温。'

# @tool(description='获取指定城市的天气')
def get_weather(city: str) -> str:
    """
    获取指定城市的实时天气，包含温度、湿度、风速和出行建议。
    Agent 会将识别到的城市名传入此函数的 city 参数。
    """
    try:
        # 1. 第一步：调用 Geocoding API 将城市名转换为经纬度
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=zh"
        geo_res = requests.get(geo_url, timeout=5)

        if geo_res.status_code != 200 or "results" not in geo_res.json():
            return f"未能找到 {city} 的地理位置信息，请检查城市名称是否准确。"

        location = geo_res.json()["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        standard_city_name = location.get("name", city)

        # 2. 第二步：查询实时天气，加入相对湿度 (relative_humidity_2m) 参数
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        weather_res = requests.get(weather_url, timeout=5)

        if weather_res.status_code == 200:
            data = weather_res.json()
            # 注意：使用了 current 参数后，返回的节点名称变成了 current
            current = data.get("current", {})

            temp = current.get("temperature_2m", "未知")
            humidity = current.get("relative_humidity_2m", "未知")
            wind_speed = current.get("wind_speed_10m", "未知")
            weather_code = current.get("weather_code", 0)

            # 3. WMO 国际气象代码解析
            weather_desc = "晴朗或多云"
            if 51 <= weather_code <= 67:
                weather_desc = "有雨 🌧️"
            elif 71 <= weather_code <= 77:
                weather_desc = "有雪 ❄️"
            elif weather_code >= 95:
                weather_desc = "雷暴 ⛈️"

            # 4. 🚀 核心新增：基于数据的智能出行建议逻辑
            advice_list = []

            # 根据天气状况给建议
            if "雨" in weather_desc or "雷暴" in weather_desc:
                advice_list.append("出门记得携带雨具，注意路滑")
            elif "雪" in weather_desc:
                advice_list.append("道路可能积雪，注意防滑保暖")

            # 根据温度给建议
            if isinstance(temp, (int, float)):
                if temp >= 30:
                    advice_list.append("天气炎热，请注意防晒和补充水分")
                elif temp <= 15:
                    advice_list.append("气温较低，建议多穿衣服注意保暖")

            # 根据湿度给建议
            if isinstance(humidity, (int, float)) and humidity >= 80:
                advice_list.append("空气湿度大，体感可能较为闷热或潮湿")

            # 如果以上都没命中，给个默认好心情建议
            if not advice_list:
                advice_list.append("气候较为适宜，祝您出行愉快")

            # 将建议拼接成一句话
            advice_str = "；".join(advice_list)

            # 5. 拼装丰满的结果返回给 Agent
            return (f"{standard_city_name} 的实时天气：{weather_desc}，"
                    f"气温 {temp}°，相对湿度 {humidity}%，风速 {wind_speed} km/h。\n"
                    f"💡 【小管家出行建议】：{advice_str}。")

        return f"接口响应异常，暂时无法获取 {city} 的天气数据。"

    except requests.exceptions.Timeout:
        return f"查询 {city} 天气时网络超时，请告诉用户直接查看手机天气App。"
    except Exception as e:
        return f"获取 {city} 天气失败，系统临时开小差了。"


# @tool(description='获取用户所在城市名称')
# def get_user_location() -> str:
#     return random.choice(['深圳', '北京', '上海', '广州', '成都', '杭州', '新加坡', '东京', '纽约'])

# @tool(description='获取用户所在城市名称')
def get_user_location() -> str:
    """
    通过公共 IP 地址获取用户当前所在的真实城市。
    """
    try:
        # 使用免费的 ip-api 服务获取基于 IP 的位置信息, lang=zh-CN 保证返回中文
        response = requests.get('http://ip-api.com/json/?lang=zh-CN', timeout=5)

        # 请求成功 (HTTP 状态码 200)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                # 提取城市名称，如果没有则默认返回"未知城市"
                city = data.get('city', '未知城市')
                return city

        # 如果接口没有成功返回，提供一个默认值兜底（避免Agent卡死）
        return "北京"

    except Exception as e:
        # 记录异常并给Agent一个友好的提示
        return f"获取位置失败, 系统报错: {str(e)}"


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
    # pass

    res = get_user_location()
    print(res)

    ret = get_weather(res)
    print(ret)

    # res = fetch_external_data('1001', '2025-01')
    # print(res)

    # res = get_current_month()
    # print(res)
