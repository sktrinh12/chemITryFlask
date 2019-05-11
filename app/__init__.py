from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS

hpath = '/Users/spencertrinh/GitRepos/chemITry'
app =Flask(__name__,static_folder=hpath+'/app/static')#,instance_path=hpath + '/protected')
app.config.from_object('config')
db = SQLAlchemy(app)
from app import views, models


