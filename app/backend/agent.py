from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio
from flask import Flask, request, jsonify
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver

app = Flask(__name__)


llm = ChatOpenAI(
    model = 'deepseek-chat',
    temperature=0.8,
    base_url = 'https://api.deepseek.com',
    api_key = 'xxxxxx'
)


client = MultiServerMCPClient({
    "medicine": {
        "url": "http://10.101.173.217:8000/mcp",
        "transport": "streamable_http"
    }
})

agent = None
checkpointer = MemorySaver()
async def init_agent():
    global agent
    tools = await client.get_tools()
    agent = create_react_agent(llm, tools, checkpointer=checkpointer)

asyncio.run(init_agent())
#tools = asyncio.run(client.get_tools())
#agent = create_react_agent(llm, tools, checkpointer=checkpointer)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message")
    sid = data.get("session_id", "default")
    if not msg:
        return jsonify({"error": "message 必填"}), 400

    async def run():
        resp = await agent.ainvoke(
            {"messages": [HumanMessage(content=msg)]},
            config={"configurable":{"thread_id": sid}}
        )
        # resp 是 BaseMessage 类型，使用 .content 获取文本
        #return resp.content if hasattr(resp, "content") else str(resp)
        return resp["messages"][-1].content

    reply = asyncio.run(run())
    return jsonify({"reply": reply})

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True)
