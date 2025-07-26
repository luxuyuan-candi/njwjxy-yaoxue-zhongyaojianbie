from fastmcp import FastMCP
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import os

# 设置 API Key
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# 获取当前目录
dir_name = os.path.dirname(os.path.abspath(__file__))

# 1. 获取当前目录下所有 CSV 文件（或指定多个）
csv_files = [
    os.path.join(dir_name, f) for f in os.listdir(dir_name)
    if f.endswith('.csv')  # 根据需求过滤文件名
]

# 2. 加载所有 CSV 文件，组合为 documents 列表
documents = []
for file in csv_files:
    loader = CSVLoader(
        file_path=file,
        csv_args={
            "delimiter": "\t",
            "quotechar": '"'
        },
        encoding="utf-8",
        autodetect_encoding=False
    )
    docs = loader.load()
    documents.extend(docs)  # 合并到总文档列表

# 打印前两条内容查看
for doc in documents[:2]:
    print(doc.page_content, doc.metadata)

# 3. 生成嵌入
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# 4. 建立向量库（FAISS）
db = FAISS.from_documents(documents, embedding=embeddings)

# 5. 初始化 LLM
llm = ChatOpenAI(
    model='deepseek-chat',
    temperature=0.8,
    base_url='https://api.deepseek.com',
    api_key=DEEPSEEK_API_KEY,
)

# 6. 构建 RAG Chain
rag = ConversationalRetrievalChain.from_llm(llm=llm, retriever=db.as_retriever())

mcp = FastMCP("DrugQA")

@mcp.tool()
def ask_drug(question: str) -> str:
    """
    用于查询药品的批准文号、规格、适应症、用法用量等信息，查询食品的商品编码、规格、生产企业、批准文号、最新进价、类别名称、剂型、售价等信息。
    :param question: 用户提出的具体问题
    :return: 最终获得的答案
    """
    chat_history = []
    res = rag({"question": question, "chat_history": chat_history})
    return res["answer"]

if __name__ == "__main__":
    print("Starting MCP HTTP server...")
    mcp.run(transport="http", host="0.0.0.0", port=9000)
