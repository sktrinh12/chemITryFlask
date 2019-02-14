from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import SQLALCHEMY_DATABASE_URI
from app import app, db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists

migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session=Session()

if __name__ == '__main__':
    manager.run()



