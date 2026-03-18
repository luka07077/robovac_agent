"""
基于 Streamlit 完成的Web网页上传服务

当Web页面元素发生变化时, 代码都会重新运行一次
"""
import os
import sys
import streamlit as st

# --- 必须放在最前面：新增路径配置代码开始 ---
# 1. 先指路：获取当前文件所在目录的上一级目录（项目根目录），并加入系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.append(project_root)
# --- 新增路径配置代码结束 ---

from rag.vector_stores import vector_store_client


# 获取并保存知识库更新服务对象
if 'service' not in st.session_state:
    st.session_state['service'] = vector_store_client

st.title('知识库 Web 更新服务')

# 1. 修改允许的类型，增加 pdf 和 docx 等
upload_file = st.file_uploader(
    label='请上传知识库文件 (.txt, .pdf, .docx)',
    type=['txt', 'pdf', 'docx', 'doc'],
    accept_multiple_files=False,
)

if upload_file is not None:
    file_name = upload_file.name
    file_type = upload_file.type
    file_size = upload_file.size / 1024  # 转为KB

    st.subheader(f'📄 文件名: {file_name}')
    st.write(f'格式: {file_type} | 大小: {file_size: .2f} KB')

    # 增加一个按钮，点击后才开始上传并解析
    if st.button('开始入库处理'):
        with st.spinner('正在解析并载入知识库中，请稍候...'):
            # 2. 获取文件的二进制流 (bytes)
            file_bytes = upload_file.getvalue()

            # 3. 直接调用向量存储的方法处理字节流
            service = st.session_state['service']
            if service is not None:
                res = service.upload_document_from_web(file_bytes, file_name)

            # 4. 根据返回结果显示提示
            if "成功" in res:
                st.success(res)
            elif "已存在" in res:
                st.info(res)
            else:
                st.error(res)
