"""
中间件的使用：
1.Agent执行前
2.Agent执行后
3.model执行前
4.model执行后
5.工具执行时
6.模型执行时
"""
from langchain.agents import AgentState
from langchain.agents.middleware import before_model, wrap_tool_call, dynamic_prompt
from langgraph.runtime import Runtime

from utils.logger_handler import logger
from utils.prompt_handler import report_prompt, main_prompt


@wrap_tool_call
def monitor_tool(request, handler):
    logger.info(f'[monitor_tool] 执行工具: {request.tool_call['name']}')
    logger.info(f'[monitor_tool] 传入参数: {request.tool_call['args']}')
    try:
        res = handler(request)

        if request.tool_call['name'] == 'fill_context_for_report':
            request.runtime.context['report'] = True

        return res
    except Exception as e:
        logger.error(f'[monitor_tool] 工具调用失败, error: {str(e)}')


@before_model
def log_before_model(state: AgentState, runtime: Runtime) -> None:
    logger.info(f'[before_model] 即将调用模型, 并附带{len(state['messages'])}条消息')


@dynamic_prompt
def report_prompt_switch(request):
    """
    在每一次生成提示词之前进行调用
    :param request:
    :return:
    """
    is_report = request.runtime.context.get('report', False)
    if is_report:
        logger.info(f'[report_prompt_switch] 切换为生成报告提示词')
        return report_prompt

    return main_prompt





