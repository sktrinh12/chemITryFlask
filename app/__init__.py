from flask import Flask
from flask_sqlalchemy import SQLAlchemy


hpath = '/Users/spencertrinh/GitRepos/Flask_chemITry/chemITryFlask'
app =Flask(__name__,static_folder='/Users/spencertrinh/GitRepos/Flask_chemITry/chemITryFlask/app/static')#,instance_path=hpath + '/protected')
app.config.from_object('config')
db = SQLAlchemy(app)
from app import views, models


