from os import environ
SQLALCHEMY_TRACK_MODIFICATIONS = False #for sqlalchemy suppress deprecation error
#DOCKER MYSQL
SQLALCHEMY_DATABASE_URI =f"mysql+pymysql://{environ['MYSQL_USER']}:{environ['MYSQL_PASSWORD']}@localhost:3306/chemitrycmpds"
# SQLALCHEMY_DATABASE_URI ='mysql+pymysql://sktrinh12:bon78952@localhost/chemitrycmpds'
# MYSQL_DATABASE_USER = 
# MYSQL_DATABASE_PASSWORD =
# MYSQL_DATABASE_PASSWORD =
# MYSQL_DATABASE_DB = 
# MYSQL_DATABASE_HOST =
# MAIL_USERNAME=  
# SECRET_KEY = 'bon' #needs this or flash does not work?

'''FOR MAILING SERVICES'''
#DEBUG=True
# MAIL_SERVER='smtp.gmail.com'
# MAIL_PORT=465
# MAIL_USE_SSL=True
# MAIL_USERNAME='sktrinh12@gmail.com'
# MAIL_PASSWORD='bon'
