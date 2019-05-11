from app import db
from wtforms import Form,BooleanField,StringField,PasswordField,TextAreaField,validators


#SQLAlchemy object maps tables to columns to classes and objects 

class Chemcmpd(db.Model):
   __tablename__ = 'CSdb_addn'
   csid = db.Column('ChemSpider_ID',db.Integer,primary_key=True)
   cname = db.Column('Common_Name', db.String(120))
   sname= db.Column('Systematic_Name',db.String(200))
   stdinchi= db.Column('Std_InChI',db.String(200))
   mform = db.Column('Molecular_Formula',db.String(120))
   amass= db.Column('Average_Mass',db.Numeric)
   smi = db.Column('SMILES',db.String(200))
   logp = db.Column('logP',db.Numeric)
   hbd = db.Column('H_Bond_Donors',db.Integer)
   hba = db.Column('H_Bond_Acceptors',db.Integer)
   numrotbonds= db.Column('Num_Rota_Bonds',db.Integer)
   lrfive= db.Column('Lipinski_Rule_5',db.Integer)
   psa= db.Column('Polar_Surface_Area',db.Numeric)
   enthalpy= db.Column('Enthalpy_Vap',db.String(60))
   density= db.Column('Density',db.String(100))
   bp= db.Column('Boiling_Point',db.String(100))
   arings= db.Column('Arom_rings',db.Integer)
   numN= db.Column('Num_Nitrogens',db.Integer)
   numO= db.Column('Num_Oxygens',db.Integer)
   sssr= db.Column('SSSR',db.Integer)
   stereoctr= db.Column('Stereocenters',db.Integer)
   isnp= db.Column('is_NP',db.String(30))
   veberv= db.Column('Veber_Violations',db.Integer)


class RegistrationForm(Form):
    username = StringField('Username',[validators.Length(min=4,max=20)])
    email = StringField('Email Address',[validators.Length(min=6,max=50)])
    password = PasswordField('New Password',[validators.DataRequired(),validators.EqualTo('confirm',message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the <a href="/tos/">Terms of Service </a> and the <a href="/privacy/"> Privacy Notice </a> (Last updated 8-Dec-2018)',[validators.DataRequired()])

class SendEmailForm(Form):
    topic = TextAreaField('topic',[validators.Length(min=2,max=100)])
    body = TextAreaField('body',[validators.Length(max=500)])
