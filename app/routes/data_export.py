from flask import Blueprint, send_file
import pandas as pd
from io import BytesIO
from app import db
from app.models import WeatherData

export_bp = Blueprint('export', __name__)


@export_bp.route('/export/csv/<city>')
def export_csv(city):
    """导出CSV格式数据"""
    with db.session.begin():
        data = WeatherData.query.filter_by(city=city).all()

        # 转换为DataFrame
        df = pd.DataFrame([{
            'date': d.timestamp.date(),
            'time': d.timestamp.time(),
            'temperature': d.temperature,
            'humidity': d.humidity,
            'wind_speed': d.wind_speed
        } for d in data])

        # 创建CSV文件
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{city}_weather_data.csv'
        )