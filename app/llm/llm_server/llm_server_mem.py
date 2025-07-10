from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory,ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langserve import add_routes
from fastapi import FastAPI
from langchain_core.runnables import RunnableLambda
import uvicorn
import os
from langchain_openai import ChatOpenAI

REDIS_PASSWORD=os.getenv("REDIS_PASSWORD")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
redis_url = os.getenv("REDIS_URL") 

REDIS_URL = f"redis://:{REDIS_PASSWORD}@{redis_url}"
DEFUALT_TTL = None

llm = ChatOpenAI(
    model = 'deepseek-chat',
    temperature=0.8,
    base_url = 'https://api.deepseek.com',
    api_key = DEEPSEEK_API_KEY
)

def create_chain(memory):
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=(
            "你是一个中医药小助手钟小药。\n"
            "以下是之前的对话记录：\n{history}\n"
            "用户现在的问题是：\n{input}\n"
            "请专业、亲切、简明地回答："
        )
    )

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
    )

    return chain

app = FastAPI(title='中药介绍', version='v1.0', description='分析中药的信息')

#user_memories = {}

def create_user_chain(user_id, query_input):
    #if user_id not in user_memories:
    #    user_memories[user_id] = ConversationBufferMemory(memory_key="history")
    #memory = user_memories[user_id]
    #return create_chain(memory)
    history = RedisChatMessageHistory(
        url=REDIS_URL,
        session_id=user_id,
        ttl=DEFUALT_TTL
    )

    if "中国药典" in query_input:
        print("请求图片鉴别，清理缓存")
        history.clear()
        print("缓存成功")

    memory = ConversationBufferMemory(
        memory_key="history",
        chat_memory=history,
        return_messages=True
    )

    return create_chain(memory)

async def chat_invoke(input_data: dict):
    user_id = input_data.get("user_id")
    if not user_id:
        raise ValueError("请求中必须包含 user_id")

    query_input = input_data.get("input")
    if not query_input:
        raise ValueError("请求中必须包含 input")

    # 动态创建绑定该 user_id 的 chain
    chain = create_user_chain(user_id, query_input)

    # 通过 chain 推理
    return {"output": chain.predict(input=query_input)}

add_routes(
    app,
    RunnableLambda(chat_invoke),
    path="/chat"
)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001)
