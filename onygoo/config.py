import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@localhost/onygoo')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    # Add other config variables as needed

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
