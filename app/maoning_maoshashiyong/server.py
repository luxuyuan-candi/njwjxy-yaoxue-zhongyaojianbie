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

BUCKET_NAME = 'maosha-shiyong'

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

@app.route('/api/maoning_maoshashiyong/products', methods=['GET'])
def get_products():
    db = create_mysql_client()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM maosha_shiyong ORDER BY id DESC")
    cursor.close()
    db.close()
    return jsonify(cursor.fetchall())

@app.route('/api/maoning_maoshashiyong/upload', methods=['POST'])
def upload():
    image = request.files['image']
    name = request.form.get('name')
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
        INSERT INTO maosha_shiyong (image, name, phone)
        VALUES (%s, %s, %s)
    """, (image_url, name, phone))
    db.commit()
    cursor.close()
    db.close()

    return jsonify({"msg": "success", "url": image_url})

@app.route('/api/maoning_maoshashiyong/product', methods=['GET'])
def get_product():
    """获取单个申请详情"""
    id = request.args.get('id')
    if not id:
        return jsonify({"success": False, "msg": "缺少id参数"}), 400

    db = create_mysql_client()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM maosha_shiyong WHERE id=%s", (id,))
    row = cursor.fetchone()
    cursor.close()
    db.close()

    if row:
        return jsonify(row)
    else:
        return jsonify({"success": False, "msg": "未找到记录"}), 404


@app.route('/api/maoning_maoshashiyong/update', methods=['POST'])
def update_status():
    """更新申请状态"""
    data = request.get_json()
    id = data.get('id')
    state = data.get('state')

    if not id or not state:
        return jsonify({"success": False, "msg": "缺少必要参数"}), 400

    db = create_mysql_client()
    cursor = db.cursor()
    cursor.execute("UPDATE maosha_shiyong SET status=%s WHERE id=%s", (state, id))
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()

    if affected > 0:
        return jsonify({"success": True, "msg": "更新成功"})
    else:
        return jsonify({"success": False, "msg": "更新失败或未找到记录"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

