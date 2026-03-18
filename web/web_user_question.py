import os
import sys
import time

import streamlit as st

# --- 必须放在最前面：新增路径配置代码开始 ---
# 1. 先指路：获取当前文件所在目录的上一级目录（项目根目录），并加入系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.append(project_root)
# --- 新增路径配置代码结束 ---

from agent.agent_react import agent_core


# 初始化
if 'agent_service' not in st.session_state:
    st.session_state['agent_service'] = agent_core
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# 标题
st.title('🚀 智扫通机器人智能管家')

# 分割线
st.divider()

# CSS魔法
css = """
<style>
/* 1. 整体容器横向反转：让头像靠最右侧 */
.stChatMessage:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
}

/* 2. 核心调整：让文本框变成自适应宽度的“气泡” */
.stChatMessage:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    flex-grow: 0 !important;           /* 核心：取消自动拉伸占满整行 */
    width: fit-content !important;     /* 核心：气泡宽度由文字长度决定 */
    max-width: 75% !important;         /* 防止文字特别长时占满屏幕，强制换行 */

    /* 3. 美化气泡样式 (可选：打造微信风) */
    background-color: #95ec69 !important; /* 经典的微信气泡绿 */
    color: #000000 !important;            /* 强制文字为黑色以适配绿色背景 */
    border-radius: 12px !important;       /* 给气泡加上圆角 */
    padding: 10px 15px !important;        /* 给气泡内部增加舒适的留白 */
    margin-right: 15px !important;        /* 让气泡和右边的头像保持一点距离 */
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 打印历史会话
if st.session_state['messages']:
    for message in st.session_state['messages']:
        st.chat_message(message['role']).write(message['content'])

# 消息输入框
user_question = st.chat_input('请输入你的问题: ')
if user_question:
    # 显示用户问题
    st.chat_message('user').write(user_question)
    # 保存消息上下文 [{"role": "xxx", "content": "xxx"}, {"role": "xxx", "content": "xxx"}...]
    st.session_state['messages'].append({"role": "user", "content": user_question})

    # # 调用Agent, 流式输出
    # with st.spinner('思考与执行中...'):
    #     with st.chat_message('assistant'):
    #         res = st.session_state['agent_service'].execute_stream(user_question)
    #         full_response = st.write_stream(res)

    # === 替换原有的流式输出部分 ===
    with st.spinner('思考与执行中...'):
        with st.chat_message('assistant'):
            # 准备UI容器
            status_box = None  # 用于显示工具调用状态的折叠框
            text_placeholder = st.empty()  # 用于动态刷新文字的空白容器
            full_response = ""  # 收集完整回答

            # 获取我们刚才修改后的生成器
            generator = st.session_state['agent_service'].execute_stream(user_question)

            # 遍历生成器抛出的数据
            for item in generator:
                # 🛡️ 双保险：如果收到的居然是纯字符串，直接当做文字输出，防止崩溃
                if isinstance(item, str):
                    full_response += item
                    text_placeholder.markdown(full_response + "▌")
                    continue  # 跳过下面的字典解析逻辑

                # 如果收到的是字典，走正常的解析逻辑
                if isinstance(item, dict):
                    # 【情况A：Agent 正在调用工具】
                    if item.get("type") == "tool":
                        if status_box is None:
                            status_box = st.status("🛠️ Agent 正在思考与执行...", expanded=True)
                        status_box.write(f"正在调用工具: `{item.get('content')}`")

                        # 【情况B：Agent 正在输出文字】
                    elif item.get("type") == "text":
                        if status_box is not None:
                            status_box.update(label="✅ 执行完毕，正在生成回答", state="complete", expanded=False)
                            status_box = None

                        # 💡 核心优化：把收到的文本块拆成单个字符，强制逐字输出
                        chunk_text = item.get("content", "")
                        for char in chunk_text:
                            full_response += char
                            # 渲染加上光标
                            text_placeholder.markdown(full_response + "▌")
                            # 加上微小的延迟（例如 0.01 到 0.03 秒，你可以根据喜好调节快慢）
                            time.sleep(0.01)

            # 整个流式输出结束后，把最后面的模拟光标去掉
            text_placeholder.markdown(full_response)

    # 保存消息
    st.session_state['messages'].append({"role": "ai", "content": full_response})





