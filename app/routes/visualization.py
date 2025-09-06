from flask import Blueprint, render_template, request, jsonify, current_app
from app.models import WeatherData
from app.utils.advanced_predictor import AdvancedPredictor
from datetime import datetime, timedelta
from app.extensions import db

vis_bp = Blueprint('visualization', __name__)


@vis_bp.route('/dashboard')
def dashboard():
    """气象数据仪表盘"""
    # 获取所有支持的城市
    cities = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']
    cities_data = {}

    for city in cities:
        # 使用全局 db
        data = db.session.query(WeatherData).filter_by(city=city).order_by(
            WeatherData.timestamp.desc()).first()
        cities_data[city] = data

    return render_template('dashboard.html', cities_data=cities_data)

@vis_bp.route('/7days_forecast')
def seven_days_forecast():
    """7天天气预报页面"""
    city = request.args.get('city', 'Beijing')
    days = request.args.get('days', 7, type=int)

    predictor = AdvancedPredictor()
    if predictor.train_model(city):
        forecast = predictor.predict_7days()
        return render_template('7days_forecast.html', forecast=forecast, city=city)
    else:
        return "无法生成预测，数据不足", 400


@vis_bp.route('/api/temperature_trend')
def temperature_trend():
    """获取温度趋势数据API"""
    city = request.args.get('city', 'Beijing')
    days = request.args.get('days', 7, type=int)

    # 创建预测器时传递城市参数
    predictor = AdvancedPredictor(city)
    if predictor.train_model():
        forecast = predictor.predict_7days()
        dates = [day['date'] for day in forecast]
        temperatures = [day['temperature'] for day in forecast]
        return jsonify({
            'dates': dates,
            'temperatures': temperatures
        })
    else:
        return jsonify({'error': '数据不足'}), 400


@vis_bp.route('/api/humidity_trend')
def humidity_trend():
    """获取湿度趋势数据API"""
    city = request.args.get('city', 'Beijing')
    days = request.args.get('days', 7, type=int)

    # 创建预测器时传递城市参数
    predictor = AdvancedPredictor(city)
    if predictor.train_model():
        forecast = predictor.predict_7days()
        dates = [day['date'] for day in forecast]
        humidities = [day['humidity'] for day in forecast]
        return jsonify({
            'dates': dates,
            'humidities': humidities
        })
    else:
        return jsonify({'error': '数据不足'}), 400


@vis_bp.route('/api/wind_trend')
def wind_trend():
    """获取风速趋势数据API"""
    city = request.args.get('city', 'Beijing')
    days = request.args.get('days', 7, type=int)

    # 创建预测器时传递城市参数
    predictor = AdvancedPredictor(city)
    if predictor.train_model():
        forecast = predictor.predict_7days()
        dates = [day['date'] for day in forecast]
        wind_speeds = [day['wind_speed'] for day in forecast]
        return jsonify({
            'dates': dates,
            'wind_speeds': wind_speeds
        })
    else:
        return jsonify({'error': '数据不足'}), 400


@vis_bp.route('/api/city_comparison')
def city_comparison():
    """获取城市对比数据API"""
    days = request.args.get('days', 7, type=int)

    cities = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']
    result = {}

    for city in cities:
        # 为每个城市创建预测器，并传递城市参数
        predictor = AdvancedPredictor(city)
        if predictor.train_model():
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


@vis_bp.route('/api/current_weather')
def current_weather():
    """获取当前天气数据API"""
    city = request.args.get('city', 'Beijing')

    # 确保在应用上下文中执行查询
    with current_app.app_context():
        data = current_app.db.session.query(WeatherData).filter_by(city=city).order_by(
            WeatherData.timestamp.desc()).first()

        if not data:
            return jsonify({"error": "No data available"}), 404

        return jsonify({
            'city': data.city,
            'temperature': data.temperature,
            'humidity': data.humidity,
            'wind_speed': data.wind_speed,
            'timestamp': data.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

@vis_bp.route('/history/<city>')
def history_chart(city):
    """显示城市历史数据图表"""
    return render_template('history_chart.html')

@vis_bp.route('/api/historical_data/<city>')
def historical_data(city):
    """获取历史天气数据API"""
    try:
        days = request.args.get('days', 30, type=int)  # 默认获取30天数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 使用全局 db
        data = db.session.query(WeatherData).filter(
            WeatherData.city == city,
            WeatherData.timestamp.between(start_date, end_date)
        ).order_by(WeatherData.timestamp.asc()).all()

        if not data:
            return jsonify({
                "error": "No data available",
                "city": city,
                "days": days
            }), 404

        result = []
        for item in data:
            result.append({
                'date': item.timestamp.strftime('%Y-%m-%d'),
                'time': item.timestamp.strftime('%H:%M:%S'),
                'temperature': item.temperature,
                'humidity': item.humidity,
                'wind_speed': item.wind_speed
            })

        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"获取历史数据失败: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "city": city
        }), 500