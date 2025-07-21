from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import pymysql
import uuid
import os

MYSQLHOST = os.getenv('MYSQLHOST')
MYSQLPASSWD = os.getenv('MYSQLPASSWD')
MINIOHOST = os.getenv('MINIOHOST')
MINIOPASSWD = os.getenv('MINIOPASSWD')


app = Flask(__name__)
CORS(app)

# 配置 MinIO
minio_client = boto3.client(
    's3',
    endpoint_url=f'http://{MINIOHOST}:9000',  # 修改为你的 MinIO 地址
    aws_access_key_id='minioadmin',
    aws_secret_access_key=MINIOPASSWD
)
BUCKET_NAME = 'cat-litter'

# 配置 MySQL
db = pymysql.connect(
    host=MYSQLHOST,
    user='root',
    password=MYSQLPASSWD,
    database='zhongyao',
    charset='utf8mb4'
)

@app.route('/api/maoning_maosha/products', methods=['GET'])
def get_products():
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    return jsonify(cursor.fetchall())

@app.route('/api/maoning_maosha/upload', methods=['POST'])
def upload():
    image = request.files['image']
    spec = request.form.get('spec')
    price = request.form.get('price')
    location = request.form.get('location')
    phone = request.form.get('phone')

    ext = image.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    # 上传至 MinIO
    minio_client.upload_fileobj(image, BUCKET_NAME, filename)
    image_url = f"https://www.njwjxy.cn:30443/{BUCKET_NAME}/{filename}"

    # 保存到数据库
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO products (image, spec, price, location, phone)
        VALUES (%s, %s, %s, %s, %s)
    """, (image_url, spec, price, location, phone))
    db.commit()

    return jsonify({"msg": "success", "url": image_url})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

