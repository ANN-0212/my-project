# app/routes/weather.py

from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from app.models import WeatherData
from app.utils.advanced_predictor import AdvancedPredictor
from app.utils.weather_crawler import WeatherService
from datetime import datetime, timedelta
import time
import threading
import numpy as np
from app.extensions import db

weather_bp = Blueprint('weather', __name__)

# 支持的城市列表
SUPPORTED_CITIES = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']

@weather_bp.route('/home')
def home():
    """美化后的首页"""
    cities = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']
    cities_data = {}

    # 确保在应用上下文中执行查询
    for city in cities:
        data = db.session.query(WeatherData).filter_by(city=city).order_by(
            WeatherData.timestamp.desc()).first()
        cities_data[city] = data

    return render_template('home.html', cities_data=cities_data)

@weather_bp.route('/latest')
def get_latest_data():
    """获取并显示最新天气数据"""
    # 确保在应用上下文中执行查询
    data = db.session.query(WeatherData).order_by(
        WeatherData.timestamp.desc()).first()

    if not data:
        return jsonify({"error": "No data available"}), 404

    # 计算天气状况
    if data.temperature > 30:
        condition = "炎热"
    elif data.temperature > 25:
        condition = "温暖"
    elif data.temperature > 20:
        condition = "舒适"
    elif data.temperature > 15:
        condition = "凉爽"
    else:
        condition = "寒冷"

    return render_template(
        'weather_detail.html',
        city=data.city,
        temperature=round(data.temperature, 1),
        humidity=round(data.humidity, 1),
        wind_speed=round(data.wind_speed, 1),
        timestamp=data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        weather_condition=condition,
        feels_like=round(data.temperature - (data.humidity / 20), 1),
        visibility=round(10 - (data.humidity / 10), 1)
    )

def crawl_city_data(city):
    """采集单个城市数据"""
    service = WeatherService()
    start_time = time.time()

    try:
        # 获取天气数据
        data = service.get_weather_data(city)

        if not data:
            return {
                'status': 'failed',
                'city': city,
                'reason': 'crawl_failed',
                'time_cost': round(time.time() - start_time, 2)
            }

        # 保存到数据库
        if service.save_to_db(data):
            # 获取最新数据
            latest_data = db.session.query(WeatherData).filter_by(city=city).order_by(
                WeatherData.timestamp.desc()).first()

            return {
                'status': 'success',
                'city': city,
                'temperature': latest_data.temperature,
                'humidity': latest_data.humidity,
                'wind_speed': latest_data.wind_speed,
                'timestamp': latest_data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'time_cost': round(time.time() - start_time, 2)
            }

        return {
            'status': 'failed',
            'city': city,
            'reason': 'save_failed',
            'time_cost': round(time.time() - start_time, 2)
        }
    except Exception as e:
        return {
            'status': 'error',
            'city': city,
            'reason': str(e),
            'time_cost': round(time.time() - start_time, 2)
        }

@weather_bp.route('/crawl')
def crawl_select():
    """显示城市选择页面"""
    return render_template('crawl_select.html', cities=SUPPORTED_CITIES)

@weather_bp.route('/crawl/all')
def crawl_all_cities():
    """采集所有支持城市的天气数据"""
    results = []
    threads = []

    # 创建线程池
    for city in SUPPORTED_CITIES:
        thread = threading.Thread(target=lambda: results.append(crawl_city_data(city)))
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 按城市名称排序结果
    results.sort(key=lambda x: SUPPORTED_CITIES.index(x['city']))

    # 计算总耗时
    total_time = sum(r['time_cost'] for r in results)

    return render_template(
        'crawl_result.html',
        results=results,
        total_time=round(total_time, 2),
        success_count=sum(1 for r in results if r['status'] == 'success'),
        failed_count=sum(1 for r in results if r['status'] in ['failed', 'error'])
    )


@weather_bp.route('/data_collection_result')
def data_collection_result():
    """数据采集结果页面"""
    # 从查询参数中获取数据
    city = request.args.get('city', 'Beijing')
    status = request.args.get('status', 'success')
    temperature = request.args.get('temperature', '25.0')
    humidity = request.args.get('humidity', '60.0')
    wind_speed = request.args.get('wind_speed', '3.0')
    time_cost = request.args.get('time_cost', '0.0')

    return render_template(
        'data_collection_result.html',
        city=city,
        status=status,
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        time_cost=time_cost
    )


@weather_bp.route('/crawl/<city_name>')
def crawl_single_city(city_name):
    """采集指定城市天气数据"""
    if city_name not in SUPPORTED_CITIES:
        return jsonify({"status": "error", "message": "Unsupported city"}), 400

    result = crawl_city_data(city_name)

    # 重定向到结果页面
    return redirect(url_for(
        'weather.data_collection_result',
        city=result.get('city', city_name),
        status=result.get('status', 'unknown'),
        temperature=result.get('temperature', '0.0'),
        humidity=result.get('humidity', '0.0'),
        wind_speed=result.get('wind_speed', '0.0'),
        time_cost=result.get('time_cost', '0.0')
    ))

# 添加7天预报路由
# 支持两种URL格式：带城市参数的路径和查询参数
@weather_bp.route('/forecast/7days')
@weather_bp.route('/forecast/7days/<city_name>')
def seven_days_forecast(city_name=None):
    """7天天气预报页面"""
    city = city_name or request.args.get('city', 'Beijing')

    # 创建预测器
    predictor = AdvancedPredictor(city)

    if predictor.train_model():
        forecast = predictor.predict_7days()
        return render_template('7days_forecast.html', forecast=forecast, city=city)
    else:
        try:
            # 尝试使用默认预测
            forecast = predictor._default_forecast()
            return render_template('7days_forecast.html', forecast=forecast, city=city)
        except:
            # 如果默认预测也失败，返回错误页面
            return render_template('prediction_error.html', city=city), 400

# 修复路由：添加API端点
@weather_bp.route('/api/weather/temperature_trend')
def temperature_trend():
    """获取温度趋势数据API"""
    city = request.args.get('city', 'Beijing')
    days = request.args.get('days', 7, type=int)

    predictor = AdvancedPredictor(city)
    if predictor.train_model():  # 不需要传递city参数
        forecast = predictor.predict_7days()
        dates = [day['date'] for day in forecast]
        temperatures = [day['temperature'] for day in forecast]
        return jsonify({
            'dates': dates,
            'temperatures': temperatures
        })
    else:
        return jsonify({'error': '数据不足'}), 400

@weather_bp.route('/api/weather/humidity_trend')
def humidity_trend():
    """获取湿度趋势数据API"""
    city = request.args.get('city', 'Beijing')
    days = request.args.get('days', 7, type=int)

    predictor = AdvancedPredictor()
    if predictor.train_model(city):
        forecast = predictor.predict_7days()
        dates = [day['date'] for day in forecast]
        humidities = [day['humidity'] for day in forecast]
        return jsonify({
            'dates': dates,
            'humidities': humidities
        })
    else:
        return jsonify({'error': '数据不足'}), 400

@weather_bp.route('/api/weather/wind_trend')
def wind_trend():
    """获取风速趋势数据API"""
    city = request.args.get('city', 'Beijing')
    days = request.args.get('days', 7, type=int)

    predictor = AdvancedPredictor()
    if predictor.train_model(city):
        forecast = predictor.predict_7days()
        dates = [day['date'] for day in forecast]
        wind_speeds = [day['wind_speed'] for day in forecast]
        return jsonify({
            'dates': dates,
            'wind_speeds': wind_speeds
        })
    else:
        return jsonify({'error': '数据不足'}), 400

@weather_bp.route('/api/weather/city_comparison')
def city_comparison():
    """获取城市对比数据API"""
    days = request.args.get('days', 7, type=int)

    cities = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']
    result = {}

    for city in cities:
        predictor = AdvancedPredictor()
        if predictor.train_model(city):
            forecast = predictor.predict_7days()
            # 计算平均值
            avg_temp = sum(day['temperature'] for day in forecast) / len(forecast)
            avg_humidity = sum(day['humidity'] for day in forecast) / len(forecast)
            avg_wind = sum(day['wind_speed'] for day in forecast) / len(forecast)

            result[city] = {
                'temperature': round(avg_temp, 1),
                'humidity': round(avg_humidity, 1),
                'wind_speed': round(avg_wind, 1)
            }

    return jsonify(result)