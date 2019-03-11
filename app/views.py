from flask import (flash,render_template,redirect,url_for,request,session,send_file,send_from_directory,jsonify)
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
#from flask_mail import Mail, Message
import os
from app import app,hpath
from app.models import RegistrationForm,SendEmailForm
from flask_paginate import Pagination, get_page_args
from bokeh.embed import components
from app.funcs import genHeatMapTanimoto,pd,np,pybel,Chemcmpd,db,dplyStruc_ob,smrtSrch,genBarPlot
from functools import wraps

#mail = Mail(app)
dfm = pd.DataFrame([(csid,cname,pybel.readstring('smi',smi)) for csid,cname,smi in db.session.query(Chemcmpd.csid,Chemcmpd.cname,Chemcmpd.smi).order_by(Chemcmpd.csid).all()],columns =['csid','cname','molec'])
dfm_fps = pd.DataFrame({'fps': dfm['molec'].apply(lambda x : x.calcfp())})
dfm_fps.index = dfm['csid'] #have to change index after ; causes Nan problem in calcfp() otherwise
dfm_amass = [float(amass[0]) for amass in db.session.query(Chemcmpd.amass).all()]
MWdata = np.array(dfm_amass)

@app.route('/')
def main():
    return redirect(url_for('dplystruc'))

@app.errorhandler(404)
def page_not_found(e):
    try:
        gc.collect()
        rule = request.path #grab url user attempted to visit
        if any(txtstr in rule for txtstr in ['feed','favicon','wp-content','wp-login','wp-logout']):
            pass
        else:
            errorlogging = open(hpath + '/app/static/fourohfour/404errorlogs.txt','a') #log url sites to this directory
            errorlogging.write((str(rule)+'\n'))
        #flash(str(rule))
        return render_template('404.html')
    except Exception as exp:
        return(str(exp))

@app.errorhandler(405)
def method_not_found(e):
    return render_template('405.html')

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('You need to login first!')
            return redirect(url_for('login_page'))
    return wrap

def special_requirement(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        try:
            if 'sktrinh12' == session['username']:
                return f(*args,**kwargs)
            else:
                return redirect(url_for('dplystruc'))
        except:
            flash('You do not have vision privledges!')
            return redirect(url_for('dplystruc'))
    return wrap

@app.route('/logout/')
@login_required #can't click logout unless logged in
def logout():
    session.clear()
    flash('You have been logged out!')
    gc.collect()
    return redirect(url_for('dplystruc'))

@app.route('/jinjaman/')
def jinjaman():
    try:
        gc.collect()
        data = [15, '15', 'Python is good','Python, Java, php, SQL, C++','<p><strong>Hey there!</strong></p>']
        return render_template('jinja-templating.html',data=data)
    except Exception as e:
        return(str(e))

@app.route('/login/', methods=["GET","POST"])
def login_page():
    error = ''
    try:
        c, conn = create_connection(app,'chemitryusers')
        if request.method == "POST":
            data = c.execute('SELECT * FROM users WHERE username = (%s)', thwart(request.form['username']))
            data = c.fetchone()[2] #hash pwd of username [usrnm, email, pwd]

            if sha256_crypt.verify(request.form['password'],data): #returns boolean, equivalent starting data
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash('you are now logged in!')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid credentials, try again'
        gc.collect()

        return render_template("login.html", error = error)

    except Exception as e:
        #flash(e)
        error = 'Invalid credentials, try again'
        return render_template('login.html',error = error)

@app.route('/register/', methods=['GET','POST'])
def register_page():
    try:
        form = RegistrationForm(request.form) #render the form
        if request.method =='POST' and form.validate(): #the user is making a post (clicking submit) & all the validators are checked
            username = form.username.data #textfield
            email = form.email.data
            password = sha256_crypt.encrypt(str(form.password.data)) #password hashing
            c, conn = create_connection(app,'chemitryusers')
            x = c.execute("SELECT * FROM users WHERE username = (%s)",(thwart(username),))
            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html',form=form)
            else:
                c.execute("INSERT INTO users (username,password,email) VALUES (%s,%s,%s)",
                            (thwart(username),thwart(password),thwart(email)))
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] =True
                session['username'] = username
                return redirect(url_for('dplystruc'))
        return render_template("register.html",form=form)
    except Exception as e:
        return (str(e))

@app.route('/send-mail/', methods=['GET','POST'])
@login_required
def send_mail():
    error =''
    try:
        emailform = SendEmailForm(request.form)
        if request.method == 'POST' and emailform.validate():
            c, conn = create_connection(app,'chemitryusers')
            emailRecipt = c.execute('SELECT email FROM users WHERE username = (%s)', session['username'])
            emailRecipt = c.fetchone()[0]
            msg = Message(f"Mail sent from {request.base_url} - topic: {emailform.topic.data}!",
                            sender=MAIL_USERNAME,
                            recipients=[emailRecipt])
            msg.body = emailform.body.data
            msg.html = render_template('sendEmail.html', username=session['username'],emailRecipt=emailRecipt,baseurl=request.base_url)
            mail.send(msg)
            flash('Email Sent! :)')
        gc.collect()
        return render_template('sendEmailForm.html',form=emailform,error=error)

    except Exception as e:
        #flash(e)
        error='The minimum or maximum amount of characters for Topic/Body were not met'
        return render_template('sendEmailForm.html',error=error)

@app.route('/protected/<path:filename>')
@special_requirement
def protected(filename):
    try:
        return send_from_directory(os.path.join(app.instance_path,''),filename)
    except:
        return redirect(url_for('main'))
 
@app.route('/smrtsrch/',methods=['POST','GET'])
def smrtsrch():
    try:
        gc.collect()
        if request.method=='POST':
            query = request.form['smrtsrch'] 
            return render_template('dplysubsrch.html',svgoutput= smrtSrch(query,dfm) ,query=query)    
        elif request.method=='GET':
            return render_template('dplysubsrch.html')
    except Exception as e: 
        error = f'Problem child - ({e})'
        return render_template('dplysubsrch.html',error=error)

@app.route('/dplystruc/',methods=['GET','POST'])
def dplystruc():
    try:       
        gc.collect() 
        if request.method=='POST':
            csid  = request.form['csid']
            svg = dplyStruc_ob(csid)
            return render_template('displaystructure.html',svg=svg[0],cname=svg[1],csid=csid)
        elif request.method =='GET': 
            return render_template('displaystructure.html')  
    except Exception as e:      
        blank = f'<strong>No image to display - {e}</strong>'
        return render_template('displaystructure.html',svg=blank)

@app.route('/datatable/')
def datatable():
    try: 
        page = request.args.get('page',1,type=int)
        datTbl=db.session.query(Chemcmpd).order_by('Common_Name').paginate(page=page,per_page=12)
        return render_template('datatable.html',output=datTbl,page=page)
    except Exception as e:
        return str(e)

@app.route('/barplot/',defaults={'binNum':15},methods=['GET','POST'])
@app.route('/barplot/<int:binNum>')
def barplot(binNum):
    plot = genBarPlot(binNum) 
    script,div = components(plot)
    return render_template('barplot.html',barplot_div=div,barplot_script=script)

@app.route('/update_barplot',methods=['GET','POST'])
def update_barplot(): 
    if request.form == 'POST':
        binNum = request.form['form-barplot']  
    plot = genBarPlot(binNum)
    script,div = components(plot)
    return render_template('update_barplot.html',binNum=binNum,barplot_div=div,barplot_script=script)

@app.route('/tanimoto/',methods=['GET','POST'])
def tanimoto():
    if request.method=='POST':
        csid = int(request.form['csid'])
        stmt=db.session.query(db.exists().where(Chemcmpd.csid==csid)).scalar()
        if stmt:
            csid_lst = dfm_fps.index.tolist()
            tanimotoLst = [dfm_fps.loc[int(csid)].item() | dfm_fps.loc[int(cs)].item() for cs in csid_lst]
            cname = db.session.query(Chemcmpd.cname).filter(Chemcmpd.csid==csid).scalar()
            p = genHeatMapTanimoto(tanimotoLst,csid,csid_lst)
            script,div = components(p)
            error=''
        else:
            error=f'{csid} was not found in the database, try a different CSID#'
            script,div,csid,cname=['']*4
    else:
        script,div,csid,cname,error = ['']*5
    return render_template('dplytanihm.html',script=script,div=div,csid=csid,cname=cname,error=error) 
