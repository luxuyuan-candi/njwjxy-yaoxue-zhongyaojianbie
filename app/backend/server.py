import torch
import os
from torchvision import transforms
import json
from flask import Flask, request, jsonify
from PIL import Image
import io
import requests

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

APPID = 'wxa4c6a5aa471f6f75'
APPSECRET = 'fcc409ab536a04f022c7e46aa889668b'

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
                'openid': data['openid'],
                'session_key': data['session_key']
            })
        else:
            return jsonify({'error': 'WeChat API error', 'detail': data}), 500
    except Exception as e:
        return jsonify({'error':'Server error', 'message':str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)