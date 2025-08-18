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
def create_minio_client():
    minio_client = boto3.client(
        's3',
        endpoint_url=f'http://{MINIOHOST}:9000',  # 修改为你的 MinIO 地址
        aws_access_key_id='minioadmin',
        aws_secret_access_key=MINIOPASSWD
    )
    return minio_client

BUCKET_NAME = 'cat-litter'

def create_mysql_client():
    # 配置 MySQL
    db = pymysql.connect(
        host=MYSQLHOST,
        user='root',
        password=MYSQLPASSWD,
        database='zhongyao',
        charset='utf8mb4'
    )
    return db

@app.route('/api/maoning_maosha/products', methods=['GET'])
def get_products():
    db = create_mysql_client()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    cursor.close()
    db.close()
    return jsonify(cursor.fetchall())
'''
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
    minio_client = create_minio_client()
    minio_client.upload_fileobj(image, BUCKET_NAME, filename)
    image_url = f"https://www.njwjxy.cn:30443/{BUCKET_NAME}/{filename}"

    # 保存到数据库
    db = create_mysql_client()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO products (image, spec, price, location, phone)
        VALUES (%s, %s, %s, %s, %s)
    """, (image_url, spec, price, location, phone))
    db.commit()
    cursor.close()
    db.close()

    return jsonify({"msg": "success", "url": image_url})
'''
@app.route('/api/maoning_maosha/upload', methods=['POST'])
def upload():
    upload_id = request.form.get('uploadId')  # 前端传的ID
    image = request.files.get('image')
    erweiimage = request.files.get('erweiimage')
    ywymimage = request.files.get('ywymimage')

    spec = request.form.get('spec')
    price = request.form.get('price')
    location = request.form.get('location')
    phone = request.form.get('phone')

    minio_client = create_minio_client()

    def save_to_minio(file_obj):
        if file_obj:
            ext = file_obj.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            minio_client.upload_fileobj(file_obj, BUCKET_NAME, filename)
            return f"https://www.njwjxy.cn:30443/{BUCKET_NAME}/{filename}"
        return None

    image_url = save_to_minio(image)
    erweiimage_url = save_to_minio(erweiimage)
    ywymimage_url = save_to_minio(ywymimage)

    db = create_mysql_client()
    cursor = db.cursor()

    if not upload_id:  # 第一次上传，先插入
        cursor.execute("""
            INSERT INTO products (image, erweiimage, ywymimage, spec, price, location, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (image_url, erweiimage_url, ywymimage_url, spec, price, location, phone))
        db.commit()
        upload_id = cursor.lastrowid
    else:  # 后续上传，更新同一行
        if image_url:
            cursor.execute("UPDATE products SET image=%s WHERE id=%s", (image_url, upload_id))
        if erweiimage_url:
            cursor.execute("UPDATE products SET erweiimage=%s WHERE id=%s", (erweiimage_url, upload_id))
        if ywymimage_url:
            cursor.execute("UPDATE products SET ywymimage=%s WHERE id=%s", (ywymimage_url, upload_id))
        db.commit()

    cursor.close()
    db.close()

    return jsonify({"msg": "success", "uploadId": upload_id})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

