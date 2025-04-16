from langchain.embeddings.base import Embeddings
from langchain_community.embeddings import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer
from typing import List
import csv
from langchain_chroma import Chroma
import chromadb

class CustomEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return [self.model.encode(d).tolist() for d in documents]

    def embed_query(self, query: str) -> List[float]:
        return self.model.encode([query])[0].tolist()

class Retriever():
    def __init__(self, persist_directory_path = "./retr_datasets/", embeddings_name="m3e-base", dataset_path = "dataset/text2dsl_examples.csv", dataset_mapping=None):
        self.persist_directory_path = persist_directory_path
        self.embeddings_name = embeddings_name
        self.embedding_function = self.load_embedding_fuction()
        self.dataset_path = dataset_path
    
    def load_embedding_fuction(self):
        if self.embeddings_name == "all-MiniLM-L6-v2":
            embedding_function = SentenceTransformerEmbeddings(model_name="../hf_models/"+"sentence-transformers/all-MiniLM-L6-v2", model_kwargs = {'device': 'cuda'})
        elif self.embeddings_name == "m3e-base":
            embedding_function = CustomEmbeddings("../hf_models/"+"moka-ai/m3e-base") # .to('cuda')
            embedding_function = embedding_function
        return embedding_function

    def get_retriever(self):
        chroma_client = chromadb.PersistentClient(path=self.persist_directory_path+self.embeddings_name+'/') # 
        try:
            collection_sql = chroma_client.get_collection(name=self.embeddings_name)
        except:
            # 加载数据集
            with open(self.dataset_path, 'r', encoding='utf-8') as file:
                dataset = list(csv.reader(file))[1:]
            embeddings=self.embedding_function.embed_documents([row[1] for row in dataset])
            documents = ['用户提问: '+ row[1] + ' 查询语句：' + row[2] for row in dataset]
            # 初始化数据库
            collection_sql = chroma_client.get_or_create_collection(name=self.embeddings_name)
            collection_sql.add( # 添加数据
                embeddings=embeddings,
                documents=documents,
                ids=[str(id) for id in range(len(dataset))],
                )

        # 数据库数据编码
        self.db = Chroma(
            persist_directory=self.persist_directory_path+self.embeddings_name+'/',
            client=chroma_client,
            collection_name=self.embeddings_name,
            embedding_function=self.embedding_function,
        )

    def query(self, query, k = 4, format_output = False):
        if format_output:
            docs = self.db.similarity_search(query, k=k)
            return "\n\n".join(doc.page_content for doc in docs)
        return self.db.similarity_search(query, k=k)
