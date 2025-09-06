import os

class Config:
    # 确保连接字符串包含 charset=utf8mb4
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost:3306/weather_db?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁止信号追踪[3](@ref)
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}  # 连接池保活

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    TESTING = False  # 测试模式开关