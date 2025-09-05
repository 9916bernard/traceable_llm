from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 확장 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # 블루프린트 등록
    from app.routes.llm_routes import llm_bp
    from app.routes.verification_routes import verification_bp
    from app.routes.blockchain_routes import blockchain_bp
    
    app.register_blueprint(llm_bp, url_prefix='/api/llm')
    app.register_blueprint(verification_bp, url_prefix='/api/verification')
    app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
    
    return app
