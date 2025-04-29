import torch
import os
from torchvision import transforms
import json
from flask import Flask, request, jsonify
from PIL import Image
import io
import requests
import pymysql

# 加载模型
work_dir = os.getcwd()
model_path = work_dir + '/model/model_full_epoch_100.pth'
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

convert_path = work_dir + '/model/pinyin_to_chinese_herbs.json'
with open(convert_path, 'r', encoding='utf-8') as f:
    convert_dict = json.load(f)

# 获取环境变量
APPID = 'wxa4c6a5aa471f6f75'
APPSECRET = os.getenv('APPSECRET')
MYSQLURL = os.getenv('MYSQLURL')
MYSQLUSER = os.getenv('MYSQLUSER')
MYSQLPASSWORD = os.getenv('MYSQLPASSWORD')
MYSQLDATABASE = os.getenv('MYSQLDATABASE')
MYSQLPORT = os.getenv('MYSQLPORT')
MYSQLCHARSET = os.getenv('MYSQLCHARSET')

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
        question = convert_dict[class_labels[str(predicted.item())]]
        url = "http://10.241.24.121:8001/chat/invoke"
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
            'class_name': convert_dict[class_labels[str(predicted.item())]],
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
        url = "http://10.241.24.121:8001/chat/invoke"
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
