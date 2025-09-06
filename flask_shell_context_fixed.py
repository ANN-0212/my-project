import requests
import json
import time
import random
import logging
from datetime import datetime, timedelta
from app import create_app
from app.models import db, WeatherData

from app.models import db, User, WeatherData
from run import app


def make_shell_context():
    return {'db': db, 'User': User, 'WeatherData': WeatherData}
# 在应用上下文中执行
with app.app_context():
    # 设置查询参数
    city = '北京'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    print(f"查询条件: 城市={city}, 时间范围={start_date} 到 {end_date}")

    # 执行查询
    try:
        data = WeatherData.query.filter(
            WeatherData.city == city,
            WeatherData.record_time.between(start_date, end_date)
        ).all()

        if not data:
            print("未找到匹配的数据")
        else:
            print(f"找到 {len(data)} 条记录:")
            for record in data[:5]:
                print(f"ID: {record.id}, 温度: {record.temp}°C, 湿度: {record.humidity}%, "
                      f"时间: {record.record_time.strftime('%Y-%m-%d %H:%M')}")

            if len(data) > 5:
                print(f"...省略 {len(data) - 5} 条记录")

    except Exception as e:
        print(f"查询失败: {str(e)}")