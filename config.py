from os import path
SECRET_KEY = 'nabwdmjBVDHVHAJKHjh- KJgkjGHJKgHJGjhg'
DEBUG = True
DB_HOST = 'localhost'

BASE_DIR = path.dirname(path.abspath(__file__))

DB_NAME = path.join(BASE_DIR, 'BANCO.FDB')
DB_USER = 'sysdba'
DB_PASSWORD = 'sysdba'
UPLOAD_FOLDER = r'C:\Users\Aluno\Documents\Github\Biblioteca-teste\imagens'
