import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(CURRENT_DIR, "chroma_db")
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "qwen2.5:7b"
REDIS_PASSWORD="luweike"
REDIS_URL = f"redis://:{REDIS_PASSWORD}@170.106.150.85:32000"
DEFAULT_TTL = None

def build_rag_chain(memory):
    embedding = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
    retriever = vectordb.as_retriever()
    llm = ChatOllama(model=LLM_MODEL)

    prompt = PromptTemplate(
        input_variables=["chat_history", "question", "context"],
        template=(
            "你是一个慢病随访小助手。\n"
            "以下是之前的对话记录：\n{chat_history}\n"
            "用户现在的问题是：\n{question}\n"
            "以下是相关文档的内容：\n{context}\n"
            "请专业、亲切、简明地回答："
        )
    )
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )

    return chain

def create_user_chain(user_id, query_input):
    #if user_id not in user_memories:
    #    user_memories[user_id] = ConversationBufferMemory(memory_key="history")
    #memory = user_memories[user_id]
    #return create_chain(memory)
    history = RedisChatMessageHistory(
        url=REDIS_URL,
        session_id=user_id,
        ttl=DEFAULT_TTL
    )

    if query_input == "清理缓存":
        print("随访并清理缓存")
        history.clear()
        print("缓存成功")

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=history,
        return_messages=True
    )

    return build_rag_chain(memory)

if __name__ == '__main__':
    chain = create_user_chain("luweike_rag_test", "清理缓存")
    print(chain.invoke({"question": "陆维轲的年龄？"}))