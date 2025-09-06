# seed_data.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.models import WeatherData, User
from app.extensions import db

# 数据库连接字符串
DATABASE_URI = 'mysql://root:123456@localhost:3306/weather_db?charset=utf8mb4'


def create_tables(engine):
    """创建数据库表"""
    # 使用 db.Model 的元数据创建表
    db.Model.metadata.create_all(engine)
    print("数据库表创建成功！")


def seed_data():
    # 创建引擎和会话
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. 创建表（如果不存在）
        create_tables(engine)

        # 2. 清除现有数据
        session.query(WeatherData).delete()
        session.query(User).delete()
        session.commit()

        # 3. 创建测试用户
        test_user = User(username='test', email='test@example.com')
        test_user.set_password('test123')
        session.add(test_user)

        # 4. 为每个城市创建90天的历史数据
        cities = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']
        start_date = datetime.now() - timedelta(days=90)

        for city in cities:
            for i in range(90):
                date = start_date + timedelta(days=i)
                data = WeatherData(
                    city=city,
                    temperature=20 + random.uniform(-5, 10),
                    humidity=60 + random.uniform(-20, 20),
                    wind_speed=3 + random.uniform(-2, 4),
                    timestamp=date
                )
                session.add(data)

        session.commit()
        print("成功创建测试数据！")
    except Exception as e:
        session.rollback()
        print(f"创建数据失败: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印完整错误堆栈
    finally:
        session.close()


if __name__ == '__main__':
    seed_data()