#!/usr/bin/python3
# encoding: utf-8


from flask import Flask,redirect,url_for,render_template,request
import sqlite3
import json

app = Flask(__name__)


@app.route('/view')
def device_view():

    conn = sqlite3.connect('monitor.db', check_same_thread=False)
    print('Opened database successfully')
    # 建立游标
    c = conn.cursor()
    # 查询设备概览表
    device_info_cur = c.execute("SELECT * from device_info")
    device_info = device_info_cur.fetchall()

    # device_info表行数？
    table_rows = len(device_info)

    log_list = []
    for i in range(0,table_rows):
        device_id_flag = device_info[i][0]
        # 查询real_time表，最新的几行
        real_time_cur = c.execute("SELECT * from real_time_info where deviceID='"
                                  + str(device_id_flag)
                                  + "'order by logTime desc limit 1")
        real_time_info = real_time_cur.fetchone()
        # 元组---列表
        log_list.append(list(real_time_info))

    c.close()
    conn.close()

    context = {
        'device_info': device_info,
        'table_rows': table_rows,
        'log_list': log_list

    }
    # return '设备概览页面'
    return render_template('device_view.html',**context)


@app.route('/details')
def device_details():
    # 传入查询字符串
    device_id = request.args.get('deviceID')

    conn = sqlite3.connect('monitor.db', check_same_thread=False)
    # 建立游标
    c = conn.cursor()

    # 查找?deviceID 对应的实时信息
    real_time_cur = c.execute("SELECT * from real_time_info where deviceID='"
                              + str(device_id)
                              + "'order by logTime desc limit 1")
    real_time_info = real_time_cur.fetchone()
    before_list = real_time_info[0:6]

    position = c.execute("SELECT * from device_info where deviceID="
                         + str(device_id))
    company_info = position.fetchone()

    # 实时表的后面几个字段json转化为dict
    camera_info = json.loads(real_time_info[6])
    subprocess_info = json.loads(real_time_info[7])
    face_info = json.loads(real_time_info[8])
    exception_info = json.loads(real_time_info[9])

    # 取字典的键 传入模板
    camera_info_key = tuple(camera_info.keys())
    subprocess_info_key = tuple(subprocess_info.keys())
    face_info_key = tuple(face_info.keys())

    exception_info_key = ()
    for i in range(0,len(exception_info)):
        exception_info_key += tuple(exception_info[i].keys())

    # 进程数和异常数
    num_subprocess = len(subprocess_info_key)
    num_exception = len(exception_info_key) // 4

    # 参数传递
    context = {
        'camera_info': camera_info,
        'before_list': before_list,
        'subprocess_info': subprocess_info,
        'face_info': face_info,
        'exception_info': exception_info,
        'camera_info_key': camera_info_key,
        'subprocess_info_key': subprocess_info_key,
        'face_info_key': face_info_key,
        'exception_info_key': exception_info_key,
        'company_info': company_info,
        'num_subprocess': num_subprocess,
        'num_exception': num_exception
    }

    c.close()
    conn.close()
    # return '详情页面'
    return render_template('details.html',**context)


@app.route('/error')
def error_view():
    return render_template('error_view.html')


if __name__ == '__main__':
    app.run(debug = True)
