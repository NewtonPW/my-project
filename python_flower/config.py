import os

class Config:
    """ตั้งค่าทั่วไป"""
    # 🔐 รหัสลับของแอป
    SECRET_KEY = 'super_secret_cat_flower_key'
    
    # 📁 โฟลเดอร์เก็บรูปภาพ
    UPLOAD_FOLDER = 'static/uploads'
    
    # 🗄️ ฐานข้อมูล
    SQLALCHEMY_DATABASE_URI = 'sqlite:///shop.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """ตั้งค่า Development (ตอนพัฒนา)"""
    DEBUG = True


class ProductionConfig(Config):
    """ตั้งค่า Production (ตอน Release)"""
    DEBUG = False


# เลือกว่าใช้ config ไหน
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
