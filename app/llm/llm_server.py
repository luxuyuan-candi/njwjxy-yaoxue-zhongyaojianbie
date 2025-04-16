from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from fastapi import FastAPI
from langserve import add_routes
import uvicorn

# 创建模型
model = ChatOllama(model='deepseek-r1:7b')

# 创建prompt
prompt = ChatPromptTemplate.from_messages([
    ('system', '你现在是一名中药专家，根据我提问的中药材，结合中国药典的内容，给出其鉴别特性、所属科名、入药部位、全部功效。'),
    ('user', '{question}')
])

# 创建chain
output_parser = StrOutputParser()
chain = prompt | model | output_parser

# 创建服务
# 创建fastAPI的应用
app = FastAPI(title='中药介绍', version='v1.0', description='分析中药的信息')

add_routes(
    app,
    chain,
    path="/desc",
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
