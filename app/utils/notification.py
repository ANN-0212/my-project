# 后续：实现通知服务
import smtplib
from email.mime.text import MIMEText
from app import db
from app.models import Notification, User, WeatherData


class NotificationService:
    def __init__(self):
        self.smtp_server = 'smtp.example.com'
        self.smtp_port = 587
        self.smtp_user = 'notifications@example.com'
        self.smtp_password = 'password'

    def send_email(self, user, subject, message):
        """发送邮件通知"""
        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = user.email

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            # 保存通知记录
            notification = Notification(
                user_id=user.id,
                message=f"邮件通知: {subject}"
            )
            db.session.add(notification)
            db.session.commit()

            return True
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            return False

    def check_extreme_weather(self):
        """检查极端天气并发送通知"""
        # 获取所有用户
        users = User.query.all()

        for user in users:
            # 获取用户收藏城市
            favorites = [f.city for f in user.favorite_cities]

            for city in favorites:
                # 获取最新天气数据
                data = WeatherData.query.filter_by(city=city).order_by(
                    WeatherData.timestamp.desc()).first()

                if not data:
                    continue

                # 检查极端天气条件
                if data.temperature > 35:
                    self.send_email(user, "高温预警",
                                    f"{city}当前温度高达{data.temperature}°C，请注意防暑降温！")

                if data.temperature < 0:
                    self.send_email(user, "低温预警",
                                    f"{city}当前温度低至{data.temperature}°C，请注意保暖！")

                if data.wind_speed > 10:
                    self.send_email(user, "大风预警",
                                    f"{city}当前风速高达{data.wind_speed}m/s，请注意安全！")