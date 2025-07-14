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
svc_file = os.path.join(dir_name, 'yaodianyaoping-test1-utf-8.csv')

# 1. 加载 TSV 文件（制表符分隔）
loader = CSVLoader(
    file_path=svc_file,
    csv_args={
        "delimiter": "\t",
        "quotechar": '"'  # 如果没有引号包围
    },
    encoding="utf-8",               # 明确指定编码
    autodetect_encoding=False
)
documents = loader.load()

# 打印前两条内容查看
for doc in documents[:2]:
    print(doc.page_content, doc.metadata)

# 2. 生成嵌入
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# 3. 建立向量库（FAISS）
db = FAISS.from_documents(documents, embedding=embeddings)

# 4. 初始化 LLM
llm = ChatOpenAI(
    model = 'deepseek-chat',
    temperature=0.8,
    base_url = 'https://api.deepseek.com',
    api_key = DEEPSEEK_API_KEY,
)

# 5. 构建 RAG Chain
rag = ConversationalRetrievalChain.from_llm(llm=llm, retriever=db.as_retriever())

mcp = FastMCP("DrugQA")

@mcp.tool()
def ask_drug(question: str) -> str:
    """
    用于查询药品的批准文号、规格、适应症、用法用量等信息。
    :param question: 用户提出的具体问题
    :return: 最终获得的答案
    """
    chat_history = [] 
    res = rag({"question": question, "chat_history":chat_history})
    return res["answer"]

if __name__ == "__main__":
    print("Starting MCP HTTP server...")
    mcp.run(transport="http", host="0.0.0.0", port=9000)
