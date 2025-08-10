# config.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    VIEW_PASSWORD = os.environ.get('VIEW_PASSWORD')
    EDIT_PASSWORD = os.environ.get('EDIT_PASSWORD')
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 500 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'.mp3', '.ogg', '.wav', '.flac', '.m4a'}