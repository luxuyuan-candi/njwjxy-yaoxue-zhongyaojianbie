from fastapi import FastAPI, Query
from langserve import add_routes
from rag_chain import create_user_chain
from sync_document import sync_documents
from langchain_core.runnables import RunnableLambda
import uvicorn

app = FastAPI(title='慢病随访咨询', version='v1.0', description='提供咨询建议')

async def chat_invoke(input_data: dict):
    user_id = input_data.get("user_id")
    if not user_id:
        raise ValueError("请求中必须包含 user_id")

    query_input = input_data.get("input")
    if not query_input:
        raise ValueError("请求中必须包含 input")

    # 动态创建绑定该 user_id 的 chain
    chain = create_user_chain(user_id, query_input)
    if query_input == "清理缓存":
        return {"output": chain.invoke({"question": "你好"})["answer"]}
    # 通过 chain 推理
    return {"output": chain.invoke({"question": query_input})["answer"]}

add_routes(
    app,
    RunnableLambda(chat_invoke),
    path="/rag/query"
)

# 文档同步接口
@app.get("/rag/sync")
def sync():
    result = sync_documents()
    return {"status": result}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8002)