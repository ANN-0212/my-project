import logging
import random
import requests
import time
from datetime import datetime
from app.models import WeatherData
from app.extensions import db

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self):
        # 支持的API服务列表
        self.api_services = [
            self._openweathermap_api,
            self._weatherbit_api,
            self._local_fallback
        ]

        # 城市ID映射
        self.city_ids = {
            'Beijing': {
                'openweathermap': 1816670,
                'weatherbit': 1816670
            },
            'Shanghai': {
                'openweathermap': 1796236,
                'weatherbit': 1796236
            },
            'Guangzhou': {
                'openweathermap': 1809858,
                'weatherbit': 1809858
            },
            'Shenzhen': {
                'openweathermap': 1795565,
                'weatherbit': 1795565
            }
        }

        # API密钥
        self.api_keys = {
            'openweathermap': 'cb9902cd516183ee3e8ebe75f5e76df5',
            'weatherbit': '041c5e20f68340048fab8999a820922f'
        }

    def get_weather_data(self, city):
        """获取指定城市天气数据"""
        if city not in self.city_ids:
            return None

        # 随机选择一个API服务
        api_service = random.choice(self.api_services)

        try:
            # 尝试获取数据
            return api_service(city)
        except Exception as e:
            logger.error(f"API服务调用失败: {str(e)}")
            return None

    def _openweathermap_api(self, city):
        """使用OpenWeatherMap API获取天气数据"""
        city_id = self.city_ids[city]['openweathermap']
        api_key = self.api_keys['openweathermap']
        url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={api_key}&units=metric"

        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=(3.05, 15))  # 连接超时3秒，读取超时15秒
                data = response.json()

                # 检查返回数据是否有效
                if 'main' in data and 'wind' in data:
                    return {
                        'city': city,
                        'temperature': data['main']['temp'],
                        'humidity': data['main']['humidity'],
                        'wind_speed': data['wind']['speed'],
                        'timestamp': datetime.now(),
                        'source': 'openweathermap'
                    }
                else:
                    logger.warning(f"OpenWeatherMap API返回无效数据: {data}")
                    # 尝试下一个API
                    return self._weatherbit_api(city)

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    logger.warning(f"OpenWeatherMap API请求超时，重试 {attempt + 1}/{max_retries}")
                    time.sleep(0.5)  # 等待0.5秒后重试
                    continue
                else:
                    logger.error(f"OpenWeatherMap API请求超时，放弃重试")
                    # 尝试下一个API
                    return self._weatherbit_api(city)
            except Exception as e:
                logger.error(f"OpenWeatherMap API错误: {str(e)}")
                # 尝试下一个API
                return self._weatherbit_api(city)

        return None

    def _weatherbit_api(self, city):
        """使用Weatherbit API获取天气数据"""
        city_id = self.city_ids[city]['weatherbit']
        api_key = self.api_keys['weatherbit']
        url = f"https://api.weatherbit.io/v2.0/current?city_id={city_id}&key={api_key}"

        # 重试机制
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=(3.05, 15))  # 连接超时3秒，读取超时15秒
                data = response.json()

                # 检查返回数据是否有效
                if 'data' in data and len(data['data']) > 0:
                    return {
                        'city': city,
                        'temperature': data['data'][0]['temp'],
                        'humidity': data['data'][0]['rh'],
                        'wind_speed': data['data'][0]['wind_spd'],
                        'timestamp': datetime.now(),
                        'source': 'weatherbit'
                    }
                else:
                    logger.warning(f"Weatherbit API返回无效数据: {data}")
                    # 使用本地后备
                    return self._local_fallback(city)

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    logger.warning(f"Weatherbit API请求超时，重试 {attempt + 1}/{max_retries}")
                    time.sleep(0.5)  # 等待0.5秒后重试
                    continue
                else:
                    logger.error(f"Weatherbit API请求超时，放弃重试")
                    # 使用本地后备
                    return self._local_fallback(city)
            except Exception as e:
                logger.error(f"Weatherbit API错误: {str(e)}")
                # 使用本地后备
                return self._local_fallback(city)

        return self._local_fallback(city)

    def _local_fallback(self, city):
        """本地后备数据源 - 使用最近的数据"""
        logger.warning(f"使用本地后备数据源: {city}")
        try:
            # 获取最近的数据
            latest_data = WeatherData.query.filter_by(city=city).order_by(
                WeatherData.timestamp.desc()).first()

            if latest_data:
                return {
                    'city': city,
                    'temperature': latest_data.temperature,
                    'humidity': latest_data.humidity,
                    'wind_speed': latest_data.wind_speed,
                    'timestamp': datetime.now(),
                    'source': 'local_fallback'
                }
        except Exception as e:
            logger.error(f"获取本地后备数据失败: {str(e)}")

        # 如果连本地数据都没有，返回默认值
        return {
            'city': city,
            'temperature': 25.0,
            'humidity': 60.0,
            'wind_speed': 3.0,
            'timestamp': datetime.now(),
            'source': 'default'
        }

    def save_to_db(self, data):
        """保存天气数据到数据库"""
        try:
            # 创建新记录
            new_data = WeatherData(
                city=data['city'],
                temperature=data['temperature'],
                humidity=data['humidity'],
                wind_speed=data['wind_speed'],
                timestamp=data['timestamp']
            )

            # 使用全局db
            db.session.add(new_data)
            db.session.commit()
            logger.info(f"成功保存{data['city']}数据到数据库")
            return True
        except Exception as e:
            logger.error(f"保存{data['city']}数据失败: {str(e)}")
            db.session.rollback()
            return False