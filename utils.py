from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
import chromadb
import csv
import datasets
from sentence_transformers import SentenceTransformer
from typing import List
from langchain.embeddings.base import Embeddings
import json

class CustomEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return [self.model.encode(d).tolist() for d in documents]

    def embed_query(self, query: str) -> List[float]:
        return self.model.encode([query])[0].tolist()

collection_name_dict = {
    "all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
    "m3e-base":"m3e-base",
}

class Retriever():
    def __init__(self, persist_directory_path = "./retr_datasets/", embeddings_name="m3e-base", dataset_path = None, dataset_mapping=None):
        self.persist_directory_path = persist_directory_path
        self.embeddings_name = embeddings_name
        self.embedding_function = self.load_embedding_fuction()
        

        if dataset_path:
            self.dataset_path = dataset_path
            self.dataset_mapping = dataset_mapping
        self.db = self.get_retriever()
        
    
    def load_embedding_fuction(self):
        if self.embeddings_name == "all-MiniLM-L6-v2":
            embedding_function = SentenceTransformerEmbeddings(model_name="../../hf_models/"+"sentence-transformers/all-MiniLM-L6-v2", model_kwargs = {'device': 'cuda'})
        elif self.embeddings_name == "m3e-base":
            embedding_function = CustomEmbeddings("../../hf_models/"+"moka-ai/m3e-base") # .to('cuda')
            embedding_function = embedding_function
        return embedding_function

    def get_retriever(self):
        chroma_client = chromadb.PersistentClient(path=self.persist_directory_path+collection_name_dict[self.embeddings_name]+'/') # 
        try:
            collection_sql = chroma_client.get_collection(name=self.embeddings_name)
        except:
            # 加载数据集
            dataset = datasets.load_dataset(self.dataset_path, split="train[:30000]").map(function=self.dataset_mapping) 
            embeddings=self.embedding_function.embed_documents(dataset['document'][:])
            # 初始化数据库
            collection_sql = chroma_client.get_or_create_collection(name=collection_name_dict[self.embeddings_name])
            collection_sql.add( # 添加数据
                embeddings=embeddings,
                documents=dataset['document'][:],
                ids=[str(id) for id in dataset["id"][:]],
                )
        # 数据库数据编码
        db = Chroma(
            persist_directory=self.persist_directory_path+collection_name_dict[self.embeddings_name]+'/',
            client=chroma_client,
            collection_name=collection_name_dict[self.embeddings_name],
            embedding_function=self.embedding_function,
        )
        return db

    def query(self, query, k = 4, format_output = False):
        if format_output:
            docs = self.db.similarity_search(query, k=k)
            return "\n\n".join(doc.page_content for doc in docs)
        return self.db.similarity_search(query, k=k) 
def format_output(outputString):
    outputString=outputString.replace("\n", "").replace(" ", "").replace("```", "")
    start_index = outputString.rfind('{"query":')
    end_index = outputString.find('}}', start_index) + 2
    if start_index != -1:
        extracted_json = outputString[start_index:end_index]
        try:
            # 转换为字典
            result_dict = json.loads(extracted_json)
            parsed = result_dict.get("parsed", {})
            return parsed
        except json.JSONDecodeError:
            print("JSON解析失败，提取内容可能有问题。")
    else:
        print("未找到有效的JSON内容。")
def Log_Loader(log_id, log_template_path = 'dataset/sls_log_type.CSV'):
    with open(log_template_path, 'r', encoding='utf-8') as file:
    # Create a CSV reader object
        reader = csv.reader(file)

        # Iterate over each row in the CSV file
        for row in reader:
            # Print the key and value
            print(row)
        # 识别用哪个日志文件，关键词？
        # 读取日志数据库
    
def load_llm(llm_name, device_num=0):
    llm_dir_path = "../hf_models/"
    if llm_name in ['Qwen/Qwen2-7B-Instruct',"meta-llama/Llama-2-7b-chat-hf",'lmsys/vicuna-7b-v1.5','bigscience/bloom-7b1','Salesforce/xgen-7b-8k-base','codellama/CodeLlama-7b-Instruct-hf']:
        from langchain_community.llms import VLLM
        llm = VLLM(
            model=llm_dir_path + llm_name,
            trust_remote_code=True,  # mandatory for hf models
            max_new_tokens=512,
            # top_k=10,
            top_p=0.95,
            temperature=0.8,
            device_map=device_num,
            vllm_kwargs={"disable_log_stats":True}
        )

    elif llm_name in ['WeOpenML/Alpaca-7B-v1']:
        from langchain_community.llms import VLLM
        llm = VLLM(
            model=llm_dir_path + llm_name,
            trust_remote_code=True,  # mandatory for hf models
            max_new_tokens=512,
            # top_k=10,
            top_p=0.95,
            temperature=0.8,
            device_map=device_num,
            dtype='float16',
        )

    elif llm_name in ['Qwen/CodeQwen1.5-7B-Chat','tiiuae/falcon-7b-instruct']:
        from transformers import AutoModelForCausalLM, AutoTokenizer
 
        model_id = llm_dir_path+ llm_name
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id).to('cuda')
        def llm_hf(text):
            inputs = tokenizer(text, return_tensors="pt").to(0)
            output = model.generate(**inputs, max_new_tokens=1024, do_sample=True, temperature=0.8, top_p=0.95)
            output = tokenizer.decode(output[0], skip_special_tokens=True)
            return output
        
        llm = llm_hf

    elif llm_name in ['tiiuae/falcon-mamba-7b-BF16-GGUF']:
        from llama_cpp import Llama
        llm = Llama.from_pretrained(
            repo_id=llm_name,
            local_dir=llm_dir_path + llm_name,
            filename=llm_name,
            device=0,
        )

    elif llm_name in ['gpt-3.5-turbo', "gpt-4o-mini"]:
        from langchain_openai import ChatOpenAI
        import os
        os.environ["OPENAI_API_KEY"] = "" 
        os.environ["http_proxy"] = 'http://127.0.0.1:7891'
        os.environ["https_proxy"] = 'http://127.0.0.1:7891'
        llm = ChatOpenAI(model=llm_name, temperature=0.8, top_p=0.95)
    return llm


if __name__ == "__main__":
    
    def dataset_mapping(x): # 数据集格式转换
        return {
            "document": "Question: " + x["sql_prompt"] + " SQLQuery: " + x["sql"]
        }
    dataset_path = "../hf_models/" + "gretelai/synthetic_text_to_sql"
    db = Retriever(embeddings_name="m3e-base")
    res = db.query("What is the average salary of all employees?")
    print(res)