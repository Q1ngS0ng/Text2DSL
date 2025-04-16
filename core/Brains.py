from openai import OpenAI

def load_client(_, Model_URL, API_KEY):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：
        api_key=API_KEY, 
        base_url=Model_URL,
        )
    return client