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

# 定义后端服务
app = Flask(__name__)
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

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
                "user_id": "luweike_init"
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

    input_content = data.get('input')
    try:
        input_content = input_content.get('input')
        url = "http://10.241.24.121:8001/chat/invoke"
        data = {
            "input": {
                "input": input_content,
                "user_id": "luweike_init"
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)