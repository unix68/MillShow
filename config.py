import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    ADMIN_URL = os.environ.get('ADMIN_URL') or 'admin-secret-path-12345'
    MAX_TEAMS = 10
