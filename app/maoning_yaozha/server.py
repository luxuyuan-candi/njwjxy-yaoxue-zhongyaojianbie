from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os

MYSQLHOST = os.getenv('MYSQLHOST')
MYSQLPASSWD = os.getenv('MYSQLPASSWD')

app = Flask(__name__)
CORS(app)  # 允许跨域，微信小程序调用

# MySQL 连接配置
db_config = {
    'host': MYSQLHOST,
    'user': 'root',
    'password': MYSQLPASSWD,
    'database': 'zhongyao',
    'charset': 'utf8mb4'
}

def get_conn():
    return pymysql.connect(**db_config)

@app.route('/api/add_recycle', methods=['POST'])
def add_recycle():
    data = request.json
    unit = data.get('unit')
    contact = data.get('contact')
    date = data.get('date')
    location = data.get('location')
    weight = data.get('weight')
    herbs = data.get('herbs')  # 是列表

    if not all([unit, contact, date, location, weight]):
        return jsonify({'success': False, 'msg': '缺少必要字段'})

    # 将药材列表转为字符串存储，方便
    herbs_str = ','.join(herbs) if herbs else ''

    try:
        conn = get_conn()
        cursor = conn.cursor()
        sql = """
            INSERT INTO recycle_records(unit, contact, date, location, weight, herbs)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (unit, contact, date, location, weight, herbs_str))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print('数据库插入失败:', e)
        return jsonify({'success': False, 'msg': '服务器错误'})

@app.route('/api/get_recycles', methods=['GET'])
def get_recycles():
    try:
        conn = get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, unit AS name, contact, date, location AS address, state AS status FROM recycle_records ORDER BY created_at DESC")
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        # 将英文状态转为中文显示（可选）
        for r in records:
            if r['status'] == 'pending':
                r['status'] = '待处理'
            elif r['status'] == 'finish':
                r['status'] = '已回收'

        return jsonify({'success': True, 'data': records})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'msg': '查询失败'})

@app.route('/api/get_recycle', methods=['GET'])
def get_recycle():
    recycle_id = request.args.get('id')
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM recycle_records WHERE id = %s", (recycle_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return jsonify({'success': True, 'data': row})
    else:
        return jsonify({'success': False, 'msg': '未找到记录'})

@app.route('/api/update_state', methods=['POST'])
def update_state():
    data = request.json
    recycle_id = data.get('id')
    new_state = data.get('state')

    if new_state not in ['pending', 'finish']:
        return jsonify({'success': False, 'msg': '非法状态值'})

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE recycle_records SET state = %s WHERE id = %s", (new_state, recycle_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/recycle_summary', methods=['GET'])
def recycle_summary():
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 只统计状态为 finish 的
    cursor.execute("""
        SELECT 
            unit AS name, 
            location AS address,
            SUM(weight) AS total_weight
        FROM recycle_records
        WHERE state = 'finish'
        GROUP BY unit, location
    """)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'success': True, 'data': rows})

@app.route('/api/recycle_by_unit', methods=['GET'])
def get_recycle_by_unit():
    unit = request.args.get('unit')
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT
            DATE(date) AS date,
            SUM(weight) AS total_weight
        FROM recycle_records
        WHERE state = 'finish' AND unit = %s
        GROUP BY DATE(date)
        ORDER BY date ASC
    """, (unit,))
    records = cursor.fetchall()

    # 查询地址与总重量
    cursor.execute("""
        SELECT location, SUM(weight) as total
        FROM recycle_records
        WHERE state = 'finish' AND unit = %s 
        GROUP BY location
    """, (unit,))
    meta = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify({
        'success': True,
        'data': {
            'records': records,
            'location': meta['location'],
            'total': meta['total']
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
