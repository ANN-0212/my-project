import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import WeatherData


def generate_test_data():
    """生成测试天气数据"""
    app = create_app()

    with app.app_context():
        cities = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']

        print("开始生成测试数据...")

        for city in cities:
            for i in range(7):  # 生成7天的数据
                day = datetime.now() - timedelta(days=6 - i)

                # 创建多个时间点的数据
                for hour in [8, 12, 16, 20]:
                    timestamp = day.replace(hour=hour, minute=0, second=0)

                    data = WeatherData(
                        city=city,
                        temperature=20 + i + random.uniform(-2, 2),
                        humidity=60 - i * 5 + random.uniform(-5, 5),
                        wind_speed=random.uniform(1.0, 5.0),
                        timestamp=timestamp
                    )
                    db.session.add(data)

        db.session.commit()
        print("测试数据生成完成！共添加", len(cities) * 7 * 4, "条记录")


if __name__ == '__main__':
    generate_test_data()