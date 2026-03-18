from langchain.agents import create_agent

from agent.agent_middleware import log_before_model, monitor_tool, report_prompt_switch
from agent.agent_tools import rag_summary, get_weather, get_user_location, get_current_month, \
    fetch_external_data, get_user_id, fill_context_for_report
from model.factory import chat_model
from utils.prompt_handler import main_prompt


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=main_prompt,
            tools=[
                rag_summary, get_weather,
                get_user_location, get_user_id,
                get_current_month, fetch_external_data,
                fill_context_for_report
            ],
            middleware=[
                monitor_tool, log_before_model, report_prompt_switch
            ]
        )

    # def execute_stream(self, query: str):
    #     user_dict = {
    #         'messages': [
    #             {'role': 'user', 'content': query}
    #         ]
    #     }
    #
    #     # context为middleware中runtime中的值
    #     res = self.agent.stream(user_dict, stream_mode='messages', context={'report': False})
    #     for chunk, metadata in res:
    #         # 只提取属于 AI 助手 (AIMessageChunk) 的文本片段
    #         # 排除掉用户的提问或工具调用的内部消息
    #         if chunk.type == 'ai' and isinstance(chunk.content, str) and chunk.content:
    #             yield chunk.content

    def execute_stream(self, query: str):
        user_dict = {
            'messages': [
                {'role': 'user', 'content': query}
            ]
        }

        # context为middleware中runtime中的值
        res = self.agent.stream(user_dict, stream_mode='messages', context={'report': False})
        for chunk, metadata in res:
            if chunk.type == 'ai':
                # 1. 拦截【工具调用】的动作，返回字典
                if hasattr(chunk, 'tool_call_chunks') and chunk.tool_call_chunks:
                    for tc in chunk.tool_call_chunks:
                        if tc.get('name'):
                            yield {"type": "tool", "content": tc['name']}

                # 2. 拦截【纯文本回复】的动作，返回字典
                elif chunk.content and isinstance(chunk.content, str):
                    yield {"type": "text", "content": chunk.content}


# 创建一个全局实例
agent_core = ReactAgent()


if __name__ == '__main__':
    res = agent_core.execute_stream('扫地机器人在我所在的地区的气温下应该如何保养？')
    for chunk in res:
        print(chunk, end='', flush=True)





