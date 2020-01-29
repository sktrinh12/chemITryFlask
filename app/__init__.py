from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
app = Flask(__name__)
hpath = app.instance_path.replace('/instance','') 
# app =Flask(__name__,static_folder=hpath+'/app/static')#,instance_path=hpath + '/protected')
app.config.from_object('config')
db = SQLAlchemy(app)
from app import views, models


