from core.prompts import SentenceClipPrompt, ConditionPrompt, TargetPrompt, Post_Refine, Post_Check, Post_Explain
from core.Brains import load_client
import json
from langchain_core.runnables import RunnablePassthrough,RunnableParallel
from langchain.schema import StrOutputParser
from history.utils import format_output,extract_between
from core.RAG import Retriever
from copy import deepcopy
from langchain.schema.runnable import RunnableLambda

def debug_print(x, label="Debug Output"):
    print(f"{label}: {x}")
    return x
class COT:
    def __init__(self, MODEL_NAME, MODEL_URL, API_KEY, messages, ret=True):
        self.client = load_client(MODEL_NAME, MODEL_URL, API_KEY)
        self.model_name = MODEL_NAME
        self.messages = messages
        if ret != None:
            self.init_ret()
    def init_ret(self):
        long_term = Retriever()
        long_term.get_retriever()

        def rett(query):
            return [knowledge.page_content for knowledge in long_term.query(query)]

        def conditionRett(query):
            retrieval = rett(query)
            return [i.split('|')[0].strip() for i in retrieval]
        
        self.conditionRett = conditionRett

    def get_answer(self, sys_prompt, input_prompt, show_cot=False):
        messages = deepcopy(self.messages)
        if show_cot:
            messages = self.messages
            messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": input_prompt})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        answer = response.choices[0].message.content
        return answer

    def invoke(self, input_prompt):
        response = self.get_answer(SentenceClipPrompt, input_prompt)
        data = json.load(response)
        condition = data["parsed"]["condition"]
        target = data["parsed"]["target"]
        condition_response = self.get_answer(ConditionPrompt, condition)
        target_response = self.get_answer(TargetPrompt, target)
        return condition_response + "|" + target_response

    def llm(self, input_prompt):
        return self.get_answer("", input_prompt.to_string())

    def cot_chain(self, input_prompt):
        UnifiedAgent = (
        RunnableParallel(
            raw_query=RunnablePassthrough(),
            parse_result=(
                SentenceClipPrompt 
                | self.llm 
                | format_output
                | RunnableLambda(lambda x: debug_print(x, "Parse Result"))  # 打印 parse_result
            )
        )
        | RunnableParallel(
            condition_result=(
                RunnablePassthrough.assign(
                    long_term=lambda x: self.conditionRett(x["parse_result"]["condition"]),
                    question=lambda x: x["parse_result"]["condition"]
                )
                | ConditionPrompt 
                | self.llm 
                | StrOutputParser()
            ),
            target_part=lambda x: x["parse_result"]["target"],
        )
        | RunnableParallel(
            final_condition=lambda x: x["condition_result"],
            final_target=(
                RunnablePassthrough.assign(
                    question=lambda x: x["target_part"],
                    condition=lambda x: x["condition_result"]
                )
                | TargetPrompt 
                | self.llm 
                | StrOutputParser()
                )
            )
        )
        response = UnifiedAgent.invoke(input_prompt)
        print("condition:",response["final_condition"])
        print("target:",response["final_target"])
        response = response["final_condition"] + " | " + response["final_target"]
        return response


class Checker:
    def __init__(self, MODEL_NAME, MODEL_URL, API_KEY, messages, ret=True):
        self.client = load_client(MODEL_NAME, MODEL_URL, API_KEY)
        self.model_name = MODEL_NAME
        self.messages = messages

    def get_answer(self, sys_prompt, input_prompt, show_cot=False):
        if show_cot:
            messages = self.messages
            messages.append({"role": "system", "content": sys_prompt})
        messages = deepcopy(self.messages)
        messages.append({"role": "user", "content": input_prompt})
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        answer = response.choices[0].message.content
        return answer

    def llm(self, input_prompt):
        return self.get_answer("", input_prompt.to_string())

    def post_refine(self, input_prompt, sls_command):
        Post_Refiner = (
            Post_Refine
            | self.llm
        )
        sls_command = Post_Refiner.invoke({"input_prompt":input_prompt,"sls_command":sls_command})
        print("sls_command:",sls_command)
        return sls_command
    
    def post_check(self, input_prompt, sls_command):    
        Post_Checker = (
            Post_Check
            | self.llm
        )
        response = Post_Checker.invoke({"input_prompt":input_prompt,"sls_command":sls_command})
        print("response:",response)
        return response

    def post_explain(self, sls_command, input_prompt, sls_response):
        Post_Explainer = (
            Post_Explain
            | self.llm
        )
        response = Post_Explainer.invoke({"sls_command":sls_command,"input_prompt":input_prompt,"sls_response":sls_response})
        return response

    def check(self, input_prompt, sls_command):
        sls_command = self.post_refine(input_prompt, sls_command)
        response = self.post_check(input_prompt, sls_command)
        if "不允许执行" in response:
            return 0 
        else:
            return sls_command
