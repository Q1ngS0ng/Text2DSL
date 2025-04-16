import streamlit as st
from openai import OpenAI
from components.sidebar import sidebar
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
from core.Brains import load_client
from core.COT import COT,Checker
from core.RAG import Retriever
from components.sidebar import clear_chat_history
from core.SLS_Commit import sls_query
import re


st.set_page_config(page_title="SLS日志助手", page_icon="favicon.ico", layout="centered", initial_sidebar_state="auto", menu_items=None)

side_bar = sidebar()
st.title("阿里云SLS日志助手🐳")

# 启动模型服务
API_KEY = st.session_state.get("API_KEY")
MODEL_URL = st.session_state.get("Model_URL")
MODEL_NAME = st.session_state.get("Model_Name")
# print(API_KEY, MODEL_URL, MODEL_NAME)

if not API_KEY or not MODEL_URL or not MODEL_NAME:
    st.warning(
        "请在侧边栏输入您的模型名称、模型服务链接和API密钥。"
    )
client = load_client(MODEL_NAME, MODEL_URL, API_KEY)

# 初始化会话内容
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "你是一个擅长处理自然语言到编程语言的助手，能够将人类的查询语言转化为阿里云日志服务语言SLS。"}]
    st.session_state["messages"] = [{"role": "assistant", "content": "你好，我是日志助手，有什么可以帮助您的吗？"}]
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 启动思维链
cot = COT(MODEL_NAME, MODEL_URL, API_KEY, st.session_state.messages)
check = Checker(MODEL_NAME, MODEL_URL, API_KEY, st.session_state.messages)
# 开始对话
if prompt := st.chat_input("请输入您的需求:"):
    if st.session_state["Uploaded_Keys"] is not None:
        uploaded_keys = st.session_state["Uploaded_Keys"]
        st.session_state.messages.append({"role": "system", "content": "日志的关键词及其释义为"+str(uploaded_keys)})
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.spinner("思考中..."):
        response = cot.cot_chain(prompt)
    print('*'*20)
    print(response)
    print('*'*20)

    # Checker 执行指令审计
    with st.spinner("检查中..."):
        response = check.check(prompt,response)

    with st.spinner("执行中..."):
        if response:
            # 执行sls指令
            match = re.search(r'```(.*?)```', response, re.DOTALL)
            if match:
                command = match.group(1)
            # print(response)
            response = sls_query(command)
            response = check.post_explain(command,prompt,response)
    answer = response
    print(answer)
    if answer == 0:
        pass
    else:
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)