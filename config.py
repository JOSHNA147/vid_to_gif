import os

class Config: 
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
    GIF_FOLDER = os.path.join(BASE_DIR, 'static/gifs')
    MONGO_URI = 'mongodb://localhost:27017/video_processing_db'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    WHISPER_MODEL = "base.en"
