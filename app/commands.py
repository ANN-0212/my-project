from app.extensions import db
from app.models import WeatherData, User
from datetime import datetime, timedelta
import random
import click
from flask.cli import with_appcontext


@click.command('seed-data')
@with_appcontext
def seed_data_command():
    """创建测试数据"""
    # 清除现有数据
    db.session.query(WeatherData).delete()

    # 创建测试用户
    if not User.query.filter_by(username='test').first():
        test_user = User(username='test', email='test@example.com')
        test_user.set_password('test123')
        db.session.add(test_user)

    # 为每个城市创建90天的历史数据
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
            db.session.add(data)

    db.session.commit()
    print("成功创建测试数据！")