# 可加html
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db  # 导入全局 db 实例
from app.models import User, FavoriteCity

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    username = request.form.get('username')
    password = request.form.get('password')

    # 使用全局 db 实例
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify({"status": "success", "message": "登录成功"})

    return jsonify({"status": "failed", "message": "用户名或密码错误"}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    return jsonify({"status": "success", "message": "已登出"})


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    # 确保在应用上下文中执行查询
    with current_app.app_context():
        if not username or not password:
            return jsonify({"status": "failed", "message": "用户名和密码不能为空"}), 400

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({"status": "failed", "message": "用户名已存在"}), 400

        # 创建新用户
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"status": "success", "message": "注册成功"})


# app/routes/auth.py
@auth_bp.route('/favorites', methods=['POST'])
@login_required
def add_favorite():
    """添加收藏城市"""
    city = request.form.get('city')

    if not city:
        return jsonify({"status": "failed", "message": "城市不能为空"}), 400

    # 检查是否已收藏
    existing = FavoriteCity.query.filter_by(user_id=current_user.id, city=city).first()
    if existing:
        return jsonify({"status": "failed", "message": "已收藏该城市"}), 400

    # 添加收藏
    favorite = FavoriteCity(user_id=current_user.id, city=city)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"status": "success", "message": "收藏成功"})


@auth_bp.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    """获取收藏城市列表"""
    favorites = FavoriteCity.query.filter_by(user_id=current_user.id).all()
    cities = [f.city for f in favorites]

    return jsonify({"status": "success", "cities": cities})