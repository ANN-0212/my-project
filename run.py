import os
import threading
import time
import webbrowser

from app import create_app
from app.extensions import db
from app.models import User, WeatherData

app = create_app()


@app.cli.command("init-db")
def init_db():
    """初始化数据库"""
    with app.app_context():
        db.create_all()

        # 添加测试用户
        test_user = User(username='test', email='test@example.com')
        test_user.set_password('test123')
        db.session.add(test_user)

        # 添加测试天气数据
        cities = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']
        for city in cities:
            data = WeatherData(
                city=city,
                temperature=25.5,
                humidity=60.0,
                wind_speed=3.2
            )
            db.session.add(data)

        db.session.commit()
        print("数据库已初始化")

def open_browser():
    """在浏览器中打开首页"""
    time.sleep(1)  # 等待服务器启动
    webbrowser.open('http://127.0.0.1:5000/api/weather/home')

if __name__ == '__main__':
    # 只在主进程中打开浏览器
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("\n" + "*" * 50)
        print("* 智能气象云平台已启动")
        print("*" * 50 + "\n")

    # 在单独的线程中打开浏览器
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Thread(target=open_browser).start()

    app.run(debug=True)
