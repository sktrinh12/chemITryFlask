from flask import (flash,render_template,redirect,url_for,request,session,send_file,send_from_directory,jsonify)
from passlib.hash import sha256_crypt
# from MySQLdb import escape_string as thwart
import gc
import json
#from flask_mail import Mail, Message
import os
from app import app,hpath
from app.models import RegistrationForm#SendEmailForm
from flask_paginate import Pagination, get_page_args
from bokeh.embed import components
from bokeh.models.sources import AjaxDataSource
from app.funcs import genHeatMapTanimoto,pd,np,pybel,Chemcmpd,db,dplyStruc_ob,smrtSrch,genBarPlot,prosDf,plotNetXBokeh,genUnitCircle,genPCAdata, genMolLinks,genMolNodes,genMOL
from functools import wraps
#mail = Mail(app)
colnames=[ 'csid', 'sname', 'cname', 'stdinchi',  'mform','amass' ,'smi', 'logp', 'hbd', 'hba',  'numrotbonds',  'lrfive',  'psa',  'enthalpy',  'density',  'bp',  'arings',  'numN',  'numO',  'sssr',  'stereoctr',  'isnp',  'veberv' ] 

sqldata = db.session.query(Chemcmpd).order_by('Common_Name')#.limit(100)
dfm_main = pd.read_sql(sqldata.statement,db.session.bind)
dfm_main.columns = colnames

# dfm_molc = dfm_main[ ['csid','cname','smi']]
# dfm_molc.smi = dfm_molc.smi.apply(lambda x: pybel.readstring('smi',x))
# dfm_molc.columns = ['csid','cname','molec' ]

dfm_fps = pd.DataFrame({'fps':dfm_main.smi.apply(lambda x: pybel.readstring('smi',x).calcfp())})
dfm_fps.index = dfm_main.csid #have to change index after ; causes Nan problem in calcfp() otherwise

MWdata = np.array(dfm_main.amass)


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
            # data = c.execute('SELECT * FROM users WHERE username = (%s)', thwart(request.form['username']))
            query = f"SELECT * FROM users WHERE username = {request.form['username']}"
            data = c.execute(query)
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
            # x = c.execute("SELECT * FROM users WHERE username = (%s)",(thwart(username),))
            query_ = f"SELECT * FROM users WHERE username = {username}"
            x = c.execute(query)
            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html',form=form)
            else:
                query = "INSERT INTO users (username,password,email) VALUES (%s,%s,%s);"
                c.executemany(query,username,password,email )
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
 

# @app.route('/test/',methods=['POST','GET'])
# def test():
#     if request.method=="POST":
#         query=request.form['smrtsrch_input']
#         print(query)
#         res = smrtSrch(query,dfm_molc)
#         print(res)
#     else:
#         res = ('','')
#     return render_template('dplysubsrch.html',svgoutput=res[0],query=res[1]) 

@app.route('/smrtsrch/')
def smrtsrch():
    return render_template('dplysubsrch.html')
        
@app.route('/dplysmrtsrch/')
def dplysmrtsrch():
    gc.collect()
    query = request.args.get('smrtstr')
    result = smrtSrch(query,dfm_main)
    svgoutput = result[0]
    lengthSrchResult = result[1]
    return jsonify(htmlTable=render_template('updateSubsrch.html',svgoutput=svgoutput), query=query, lengthSrchResult=lengthSrchResult)

# @app.route('/dplystruc/',methods=['GET','POST'])
# def dplystruc():
#     try:       
#         gc.collect() 
#         if request.method=='POST':
#             csid  = request.form['csid']
#             svg = dplyStruc_ob(csid)
#             return render_template('displaystructure.html',svg=svg[0],cname=svg[1],csid=csid)
#         elif request.method =='GET': 
#             return render_template('displaystructure.html')  
#     except Exception as e:      
#         blank = f'<strong>No image to display - {e}</strong>'
#         return render_template('displaystructure.html',svg=blank)


@app.route('/dplystruc/')
def dplystruc():
    return render_template('displaystructure.html')

# @app.route('/dplystruc/')
# def dplystruc():
#     try:       
#         gc.collect() 
#         csid = request.args.get('csid')
#         if len(csid) > 3 and int(csid): 
#             svg = dplyStruc_ob(csid)
#             return render_template('displaystructure.html',svg=svg[0],cname=svg[1],csid=csid)
#         else:
#             svg = ""
#             blank = f'<strong>No image to display - {e}</strong>'
#             return render_template('displaystructure.html',svg=blank)
#     except Exception as e:      
#         svg = ""
#         return render_template('displaystructure.html',svg=svg)

@app.route('/testing/')
def testing():
    csid = request.args.get('csid')
    return jsonify(csid = csid)

@app.route('/updateDplyStrc/')
def updateDplyStrc():
    csid = request.args.get('csid',type=int)
    svg = dplyStruc_ob(csid)
    return jsonify(html_content=render_template('updateDplyStrc.html',svg=svg[0]),csid=csid)

@app.route('/datatable/')
def datatable():
    try: 
        page = request.args.get('page',1,type=int)
        datTbl= sqldata.paginate(page=page,per_page=12)
        return render_template('datatable.html',output=datTbl,page=page)
    except Exception as e:
        return str(e)

@app.route('/barplot/')
def barplot(): 
    binNum = 10 
    plot = genBarPlot(binNum,MWdata)
    script,div = components(plot)
    return render_template('barplot.html',binNum=binNum,barplot_div=div,barplot_script=script)

@app.route('/updateBar/')
def updateBar():
    binNum = request.args.get('binNum', type=int)
    plot = genBarPlot(binNum,MWdata)
    script,div = components(plot)
    return jsonify(html_plot=render_template('update_barplot.html', barplot_div=div,barplot_script=script))

@app.route('/tanimoto/',methods=['POST','GET'])
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
            error=f'<h5>{csid} was not found in the database, try a different CSID#</h5>'
            script,div,csid,cname=['']*4
    else:
        script,div,csid,cname,error = ['']*5
    return render_template('dplytanihm.html',script=script,div=div,csid=csid,cname=cname,error=error) 

@app.route('/updateTani/')
def updateTani():
    csid=request.args.get('csid',type=int)
    stmt=db.session.query(db.exists().where(Chemcmpd.csid==csid)).scalar()
    if stmt:
        csid_lst = dfm_fps.index.tolist()
        tanimotoLst = [dfm_fps.loc[csid].item() | dfm_fps.loc[int(cs)].item() for cs in csid_lst]
        cname = db.session.query(Chemcmpd.cname).filter(Chemcmpd.csid==csid).scalar()
        p = genHeatMapTanimoto(tanimotoLst,csid,csid_lst)
        script,div = components(p)
    else:
        div=f'<h5>{csid} was not found in the database!</h5>'
        script=''
    return jsonify(html_content=render_template('updateFigure.html',div=div,script=script),csid=csid)

@app.route('/networkx/',methods=['GET','POST'])
def dplynetx():
    if request.method=='POST':
        csid = str(request.form['csid'])
        stmt=db.session.query(db.exists().where(Chemcmpd.csid==csid)).scalar()
        if stmt:
            src_a, src_b = prosDf(csid,dfm_main)
            p = plotNetXBokeh(src_a,src_b,csid) 
            script,div = components(p)
            error=''
        else:
            error=f'{csid} was not found in the database, try a different CSID#'
            script,div,csid,cname=['']*4
    else:
        script,div,csid,error = ['']*4
    return render_template('dplynetx.html',script=script,div=div,csid=csid,error=error) 

@app.route('/updateNetx/')
def updateNetx():
    csid = request.args.get('csid') 
    stmt=db.session.query(db.exists().where(Chemcmpd.csid==csid)).scalar()
    if stmt:
        src_a, src_b = prosDf(csid,dfm_main)
        p = plotNetXBokeh(src_a,src_b,csid) 
        script,div = components(p)
    else:
        div=f'<h5>{csid} was not found in the database!</h5>'
        script=''
    return jsonify(html_content=render_template('updateFigure.html',div=div,script=script),csid=csid)

@app.route('/pca/')
def pca():
    # scalar_type = request.args.get('scalarType')
    scalar_type = 'norm'
    p =  genPCAdata(scalar_type,dfm_main)
    script,div = components(p)
    return render_template('pca.html',script=script,div=div)

@app.route('/exploredata/')
def exploredata():
    return render_template('exploredata.html')

@app.route('/exportGraphtoJSON/')
def exportGraphtoJSON():
    csid = request.args.get('csid')
    stmt=db.session.query(db.exists().where(Chemcmpd.csid==csid)).scalar()
    if stmt:
        cname = db.session.query(Chemcmpd.cname).filter(Chemcmpd.csid==csid).scalar()
        mol = genMOL(csid)
        links = genMolLinks(mol)
        nodes = genMolNodes(mol)
    return jsonify(nodes=nodes,links=links,cname=cname)

@app.route('/som/')
def som():
    return render_template('som.html')
