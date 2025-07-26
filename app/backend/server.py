import torch
import os
from torchvision import transforms
import json
from flask import Flask, request, jsonify
from PIL import Image
import io
import requests
import pymysql
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver

# 加载模型
work_dir = os.getcwd()
model_path = work_dir + '/model/model_full_epoch_379_100.pth'
model = torch.load(model_path, weights_only=False, map_location=torch.device('cpu'))
model.eval()

# 定义图像装换器
transformer = transforms.Compose([
    transforms.Resize((224, 224)),   # 调整图像大小
    transforms.ToTensor(),           # 转成 Tensor
    transforms.Normalize(mean=[0.5]*3, std=[0.5]*3)  # 简单归一化
])

# 加载类别标签
class_path = work_dir + '/model/class.json'
with open(class_path, 'r', encoding='utf-8') as f:
    class_labels = json.load(f)


# 获取环境变量
APPID = 'wxa4c6a5aa471f6f75'
APPSECRET = os.getenv('APPSECRET')
MYSQLURL = os.getenv('MYSQLURL')
MYSQLUSER = os.getenv('MYSQLUSER')
MYSQLPASSWORD = os.getenv('MYSQLPASSWORD')
MYSQLDATABASE = os.getenv('MYSQLDATABASE')
MYSQLPORT = os.getenv('MYSQLPORT')
MYSQLCHARSET = os.getenv('MYSQLCHARSET')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
MEDICINE_URL = os.getenv('MEDICINE_URL')
DRUGQA_URL = os.getenv('DRUGQA_URL')
LLM_SERVER_URL = os.getenv('LLM_SERVER_URL')

def insert_users_username(user_id):
    connection = pymysql.connect(
        host=MYSQLURL,
        user=MYSQLUSER,
        password=MYSQLPASSWORD,
        database=MYSQLDATABASE,
        port=int(MYSQLPORT),
        charset=MYSQLCHARSET
    )
    try:
        with connection.cursor() as cursor:
            username_to_insert = user_id
            insert_sql = '''
            INSERT IGNORE INTO users (username)
            VALUES (%s)
            '''
            affected_rows = cursor.execute(insert_sql, (username_to_insert))
            connection.commit()

            if affected_rows == 1:
                print(f"用户名 {username_to_insert} 插入成功！")
            else:
                print(f"用户名 {username_to_insert} 已存在，忽略插入。")
    finally:
        connection.close()

def increment_or_insert_recognition(user_id):
    connection = pymysql.connect(
        host=MYSQLURL,
        user=MYSQLUSER,
        password=MYSQLPASSWORD,
        database=MYSQLDATABASE,
        port=int(MYSQLPORT),
        charset=MYSQLCHARSET
    )
    try:
        with connection.cursor() as cursor:
            # 1. 查询是否已经有记录
            select_sql = """
            SELECT username FROM recognition WHERE username = %s
            """
            cursor.execute(select_sql, (user_id))
            result = cursor.fetchone()

            if result:
                username = result[0]
                # 2. 有记录，更新 recognition_count +1
                update_sql = """
                UPDATE recognition
                SET recognition_count = recognition_count + 1
                WHERE username = %s
                """
                cursor.execute(update_sql, (username,))
                print(f"用户 {user_id} 的识别记录已存在，已加1。")
            else:
                # 3. 没有记录，插入一条新的
                insert_sql = """
                INSERT INTO recognition (username, recognition_count)
                VALUES (%s, 1)
                """
                cursor.execute(insert_sql, (user_id))
                print(f"用户 {user_id} 没有识别记录，已新建。")

            connection.commit()

    finally:
        connection.close()

def get_recognition_count(user_id):
    connection = pymysql.connect(
        host=MYSQLURL,
        user=MYSQLUSER,
        password=MYSQLPASSWORD,
        database=MYSQLDATABASE,
        port=int(MYSQLPORT),
        charset=MYSQLCHARSET
    )
    try:
        with connection.cursor() as cursor:
            select_sql = """
            SELECT recognition_count 
            FROM view_user_recognition 
            WHERE username = %s
            """
            cursor.execute(select_sql, (user_id,))
            result = cursor.fetchone()

            if result:
                recognition_count = result[0]
                if recognition_count is None:
                    return 0  # 如果是NULL，返回0
                else:
                    return recognition_count
            else:
                return 0  # 如果查不到记录，也返回0
    finally:
        connection.close()

# 定义agent
llm = ChatOpenAI(
    model = 'deepseek-chat',
    temperature=0.8,
    base_url = 'https://api.deepseek.com',
    api_key = DEEPSEEK_API_KEY,
)


client = MultiServerMCPClient({
    "medicine": {
        "url": MEDICINE_URL,
        "transport": "streamable_http"
    },
    "drugqa": {
        "url": DRUGQA_URL,
        "transport": "streamable_http"
    },
})

agent = None
#checkpointer = MemorySaver()
async def init_agent():
    global agent
    tools = await client.get_tools()
    agent = create_react_agent(llm, tools)

asyncio.run(init_agent())

# 定义后端服务
app = Flask(__name__)
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    user_id = request.form.get('openid')
    if file.filename == '' or user_id == '':
        return jsonify({'error': 'No selected file OR No openid'}), 400
    
    try:
        # 读取并处理图像
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))

        if image.mode != 'RGB':
            image = image.convert('RGB')

        image_tensor = transformer(image).unsqueeze(0)

        # 预测
        with torch.no_grad():
            outputs = model(image_tensor)
            _, predicted = torch.max(outputs.data, 1)
        question = class_labels[str(predicted.item())]
        url = f"http://{LLM_SERVER_URL}/chat/invoke"
        data = {
            "input": {
                "input": "结合中国药典，给出#"+question+"#鉴别特性、所属科名、入药部位、全部功效。以普通文本格式输出。",
                "user_id": user_id
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        res = requests.post(url, json=data, headers=headers)
        print(res)
        
        # 更新数据库 
        insert_users_username(user_id)        
        increment_or_insert_recognition(user_id) 
        # 返回结果
        result = {
            'class_id': predicted.item(),
            'class_name': class_labels[str(predicted.item())],
            'confidence': torch.nn.functional.softmax(outputs, dim=1)[0][predicted.item()].item(),
            'content': res.json()['output']['output']
        }
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    print("收到的数据:", data)

    data = data.get('input')
    input_content = data.get('input')
    user_id = data.get('openid')
    if user_id == '':
        return jsonify({'error': ' No openid'}), 400
    try:
        url = f"http://{LLM_SERVER_URL}/chat/invoke"
        data = {
            "input": {
                "input": input_content,
                "user_id": user_id
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        res =  requests.post(url, json=data, headers=headers)
        print(res.json())
        result = {
            'output': res.json()['output']['output']
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/wx-login', methods=['POST'])
def wx_login():
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'Missing code'}), 400

    url = (
        f'https://api.weixin.qq.com/sns/jscode2session'
        f'?appid={APPID}&secret={APPSECRET}&js_code={code}&grant_type=authorization_code'
    )
    try:
        response = requests.get(url)
        data = response.json()

        if 'openid' in data:
            return jsonify({
                'openid': data['openid']
            })
        else:
            return jsonify({'error': 'WeChat API error', 'detail': data}), 500
    except Exception as e:
        return jsonify({'error':'Server error', 'message':str(e)}), 500

@app.route('/recognition', methods=['POST'])
def recognition():
    data = request.json
    user_id = data.get('openid')

    if not user_id:
        return jsonify({'error': 'Missing openid'}), 400
    try:
        # 后去评估次数
        recognition_count = get_recognition_count(user_id)
        
        return jsonify({
            'recognition_count': recognition_count
        })
    except Exception as e:
        return jsonify({'error':'Server error', 'message':str(e)}), 500

@app.route('/rag/query', methods=['POST'])
def rag_query():
    data = request.get_json()
    print("收到的数据:", data)

    data = data.get('input')
    input_content = data.get('input')
    user_id = 'rag-' + data.get('openid')
    if user_id == '':
        return jsonify({'error': ' No openid'}), 400
    try:
        async def run():
            resp = await agent.ainvoke(
                    {"messages": [SystemMessage(content="你是一个问病荐药+用药指导+养生建议助手。根据提出的用药问题，给出西药、中成药、西药加中药组合、保健品的用药建议，并给出药品的批准文号、规格、适应症、用法用量和保健品的批准文号、规格、价格等信息。其中如果是涉及感冒的，就回复'西药:复方氨酚烷胺片[感康]、对乙酰氨基酚片、盐酸羟甲唑啉喷雾剂；中成药：感冒清热颗粒、桑菊感冒颗粒、连花清瘟胶囊；中药加西药组合：维C银翘片(薄膜衣)；康复的保健品和事物：维生素C泡腾片、生姜红糖水。'"),HumanMessage(content=input_content)]},
                config={"configurable":{"thread_id": user_id}}
            )
            # resp 是 BaseMessage 类型，使用 .content 获取文本
            #return resp.content if hasattr(resp, "content") else str(resp)
            return resp["messages"][-1].content
        reply = asyncio.run(run())
        result = {
            'output': reply
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#@app.route('/rag/sync', methods=['GET'])
#def rag_sync():
#    try:
#        url = "http://10.241.24.121:8002/rag/sync"
#        headers = {
#            "Content-Type": "application/json"
#        }
#        res =  requests.get(url, headers=headers)
#        print(res.json())
#        result = {
#            'output': res.json()['status']
#        }
#        return jsonify(result), 200
#    except Exception as e:
#        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
