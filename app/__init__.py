# app/__init__.py
import logging

from flask import Flask
from config import Config
from flask_login import LoginManager
from .extensions import db  # 导入全局 db 实例


def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler('app.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    # 加载配置
    app.config.from_object(Config)

    # 初始化 SQLAlchemy
    db.init_app(app)

    # 初始化迁移
    from flask_migrate import Migrate
    migrate = Migrate()
    migrate.init_app(app, db)

    # 初始化登录管理
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # 注册蓝图
    def register_blueprints():
        from .routes.auth import auth_bp
        from .routes.weather import weather_bp
        from .routes.visualization import vis_bp

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(weather_bp, url_prefix='/api/weather')
        app.register_blueprint(vis_bp, url_prefix='/visualization')

    register_blueprints()

    # 设置用户加载器
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        with app.app_context():
            return User.query.get(int(user_id))

    # 创建数据库表（如果不存在）
    @app.before_first_request
    def create_tables():
        try:
            with app.app_context():
                db.create_all()
                print("数据库表已创建/验证")
        except Exception as e:
            app.logger.error(f"创建数据库表失败: {str(e)}")

    return app