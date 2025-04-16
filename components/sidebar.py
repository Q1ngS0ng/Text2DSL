import streamlit as st
import json
from dotenv import load_dotenv
import os
from core.Prase_Files import file_prase
load_dotenv()

def sidebar():
    with st.sidebar:

        st.markdown(
            "# 🐳 SLS 日志助手\n"
            "## 使用方法\n"
            "1. 选择模型、网址和API密钥🔑\n"
            "2. 上传你的日志文件📄\n"
            "3. 输入您的查询内容💬\n"
        )


        api_model_name = st.text_input(
            "模型名称 Model Name",
            type="default",
            placeholder="在这里粘贴您的模型名称 (qwen-...)",
            help="你可以在阿里云中获得你的[模型列表](https://help.aliyun.com/zh/model-studio/getting-started/models?spm=0.0.0.i1#9f8890ce29g5u)。", 
            value=os.environ.get("Model_Name", None)
            or st.session_state.get("Model_Name", ""),
        )


        
        api_base_url = st.text_input(
            "模型服务链接 Model URL",
            type="default",
            placeholder="在这里粘贴您的模型服务链接 (https://...)",
            help="你可以在阿里云中获得你的[模型服务链接](https://help.aliyun.com/zh/model-studio/developer-reference/use-qwen-by-calling-api?spm=a2c4g.11186623.0.0.617f1d1clkg8mP)。", 
            value=os.environ.get("Model_URL", None)
            or st.session_state.get("Model_URL", ""),
        )
        
        api_key_input = st.text_input(
            "服务密钥 Service API Key",
            type="password",
            placeholder="在这里粘贴您的服务密钥 (sk-...)",
            help="你可以在阿里云中获得你的[服务密钥](https://www.aliyun.com/product/bailian)。",
            value=os.environ.get("API_KEY", None)
            or st.session_state.get("API_KEY", ""),
        )

        if api_model_name is None or api_model_name is "":
            api_model_name = ""
        if api_base_url is None or api_base_url is "":
            api_base_url = ""
        if api_key_input is None or api_key_input is "":
            api_key_input = ""

        st.session_state["Model_Name"] = api_model_name
        st.session_state["Model_URL"] = api_base_url
        st.session_state["API_KEY"] = api_key_input

        st.sidebar.button('清除历史聊天记录', on_click=clear_chat_history)
        
        st.markdown("---")
        st.markdown("## 日志文件及字段含义")
        # 获得日志文件
        uploaded_file_logs = st.sidebar.file_uploader("上传JSON日志文件", type="json")
        if uploaded_file_logs is not None:
            data = file_prase(uploaded_file_logs)
            st.session_state["Uploaded_File"] = data.file
        else:
            st.session_state["Uploaded_File"] = None

        
        # 获得日志字段含义
        uploaded_file_keys = st.sidebar.file_uploader("上传JSON日志字段解析", type="json")
        if uploaded_file_keys is not None:
            data = file_prase(uploaded_file_keys)
            st.session_state["Uploaded_Keys"] = data.file
            # st.json(st.session_state["Uploaded_Keys"])
        else:
            st.session_state["Uploaded_Keys"] = None


        st.markdown("---")
        st.markdown("# 声明")
        st.markdown(
            "📖 本项目为SLSDSL问答机器人。本机器人采用ReAct框架，融合RAG、COT为主要实现框架。完成了全流程的Text2SLSDSL任务，实现了精确、可扩展的响应能力。" 
            "📖 本项目由WHU-YuwanLab搭建。"  
        )

        # 重启程序
        st.markdown("---")
        st.sidebar.button("重启程序",on_click=clear_cache)
def clear_chat_history():
    st.session_state["messages"] = [{"role": "system", "content": "你是一个擅长处理自然语言到编程语言的助手，能够将人类的查询语言转化为阿里云日志服务语言SLS。"}]
    st.session_state["messages"] = [{"role": "assistant", "content": "你好，我是日志助手，有什么可以帮助您的吗？"}]
def clear_cache():
    st.cache_data.clear()
    st.cache_resource.clear()