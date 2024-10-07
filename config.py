import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a1234f458653c5864d9643ee'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///leetcode.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
