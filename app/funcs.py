import math
from functools import reduce
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.plotting import figure
import pybel
from app.models import Chemcmpd
from app import db



colourSet = ['#045fb4',
 '#2b67b8',
 '#406fbd',
 '#4e76c0',
 '#5a7ec4',
 '#6886c8',
 '#758fcd',
 '#8298d1',
 '#8ea1d6',
 '#9aaada',
 '#a6b4de',
 '#b2bde2',
 '#bdc7e7',
 '#c9d0eb',
 '#d4daef',
 '#fbfbfb']

def primeFactors(n):
    if n == 0:
        return None
    lstOfPrimes=[]  
    # Print the number of two's that divide n 
    while n % 2 == 0: 
        lstOfPrimes.append(2), 
        n = int(n / 2)
          
    # n must be odd at this point 
    # so a skip of 2 ( i = i + 2) can be used 
    for i in range(3,int(math.sqrt(n))+1,2): 
          
        # while i divides n , n divide by i 
        while n % i== 0: 
            lstOfPrimes.append(i), 
            n = int(n / i) 
              
    # Condition if n is a prime 
    # number greater than 2 
    if n > 2: 
        lstOfPrimes.append(n)
    return lstOfPrimes

def isPrime(x):
    if x >= 2:
        for y in range(2,x):
            if not ( x % y ):
                return False
    else:
        return False
    return True

def genFakeData(length):
    return [normalvariate(1,100) for _ in range(length)]

def estmRowCol(length):
    loopUntilFind=True
    while loopUntilFind: #loop until it finds a good pair of integers for row and colm
        primeNums = primeFactors(length) #list of prime numbers of the length
        if length == 1 or primeNums == None: 
            loopUntilFind=False
            return None
        if  len(primeNums) <= 3 and len(str(length))>2: #if list of prime #s is less than 3 and the length is under 10
            length+=1 #increase until find a number that has a longer list of prime #s
        elif len(str(length)) <3 and isPrime(length): #if the length is less than 100 and it is a prime number just return the prime # and 1
            loopUntilFind=False
            return (primeNums[0],1)
        else:
            loopUntilFind=False
    return genRowCol(length)

def genRowCol(length):
    div = []
    accumm=[]
    diff=[]
    PrmNumLst = primeFactors(length)
    for enum,item in enumerate(PrmNumLst):
        length /= item
        div.append(length)
        acm = reduce(lambda x,y:x*y,PrmNumLst[:enum+1]) #reduce will multiply iteratively the values in the list
        accumm.append(acm)
        diff.append(abs(length-acm))
        dfm = pd.DataFrame({'div':div,'accumm':accumm,'diff':diff})
        minIdx = dfm.idxmin()[2] #3rd index is the index of the minimum difference
        cols = int(dfm['accumm'][minIdx])
        rows = int(dfm['div'][minIdx])
        if rows < cols:
            rows,cols = cols,rows #swap values so rows are always larger
    return (rows,cols)

def genColourMap(lstOfVals,colourSet):
    nphist,edges = np.histogram(a=np.array(lstOfVals),bins=len(colourSet)) #generate histogram based on # of HEX codes in colourSet
    colourSet = list(reversed(colourSet)) #reverse so that dark is affiliated with high #s
    lamDiff = lambda x: [abs(x-i) for i in edges].index(min([abs(x-i) for i in edges])) #find index of the minimum values in the difference list
    bin_colours=[]
    for i in lstOfVals:
        bin_category = lamDiff(i)
        bin_colours.append(bin_category)
    colours = [colourSet[i] if i<len(colourSet) else colourSet[len(colourSet)-1] for i in bin_colours] #bc the binning has 16 elemnts due to bin edges
    return colours

def genHeatMapTanimoto(lstOfVals,q_csid,csids):
    lengthLst = len(lstOfVals)
    row,col = estmRowCol(lengthLst) #find pseudo row,col
    remainderAsBlanks= row*col - lengthLst #get remainder (difference) since we overshoot the rows/colms
    colours = genColourMap(lstOfVals,colourSet)
    xs = list(range(col)) * row
    ys = range(row)
    ys = [[i]*col for i in ys]
    ys = [item for sublist in ys for item in sublist]
    if remainderAsBlanks >0:
        lstOfVals = lstOfVals + [np.nan]*remainderAsBlanks #add NaN as blanks
        colours = colours + ['#e6e8ed']*remainderAsBlanks #change colour of cells to grey for the remainders
        xs[-remainderAsBlanks:] = [np.nan]*remainderAsBlanks 
        ys[-remainderAsBlanks:] = [np.nan]*remainderAsBlanks
        csids = csids + [np.nan]*remainderAsBlanks
    src = ColumnDataSource({'x':xs,'y':ys,'val':lstOfVals,'col':colours,'csids':csids})
    hm = figure(y_range=(-0.5,row-0.5),
            sizing_mode='scale_width',
            tools="box_zoom,reset,wheel_zoom,hover,pan",
            tooltips = [('CSID', f'@csids - {q_csid}'), ('Tanimoto', '@val')])
    hm.rect('x', 'y', width=1, height=1, color='col', line_color="white",source=src)
    hm.toolbar.logo = None
    hm.min_border = 0
    hm.axis.visible = False
    hm.x_range.range_padding = 0
    hm.toolbar.autohide = True 
    hm.grid.visible = False 
    return hm 

def genBarPlot(binNum):
    hist,edges = np.histogram(MWdata,bins=binNum)
    source = ColumnDataSource( data = dict( top = hist,bottom=np.zeros(len(hist)),left=edges[:-1],right=edges[1:] ) )
    p = figure(title=f'Bins = {binNum}',plot_width=700,plot_height=700,tools='hover,save',tooltips = [('MW range','@left{0}-@right{0}'),('count', '@top')])
    p.quad(top='top',left='left',right='right',alpha=0.75,bottom='bottom',source=source)
    p.toolbar.logo=None
    p.xaxis.axis_label='Average mass'
    p.yaxis.axis_label='Count'
    return p

def dplyStruc_ob(csid):
    try: 
        stmt = db.session.query(db.exists().where(Chemcmpd.csid==csid)).scalar()
        if stmt:
            result  = [(cn,sm) for cn,sm in db.session.query(Chemcmpd.cname,Chemcmpd.smi).filter_by(csid=csid)]   
            mol = pybel.readstring('smi',result[0][1])
            cname = result[0][0]
            svg = mol.write('svg',opt={'C':None,'P':500,'u':None,'b':'transparent','B':'black'}) 
            return (svg,cname)
        else:
            return (f'<strong>{csid} does not exist in the ChemSpider DB!</strong>','')
    except Exception as e:
        error_msg =  (f'An error occured when processing that ChemSpider ID ({e})','')
        return error_msg

def smrtSrch(query,dfm): 
    try:
        matchLst=[]  
        highlighter = pybel._operations['highlight']
        smarts = pybel.Smarts(query)
        for name,mol in zip(dfm['cname'],dfm['molec']):
            if smarts.findall(mol):    
                mol.removeh()
                highlighter.Do(mol.OBMol, query+' red')
                matchLst.append( (name,mol.write('svg',opt={"u":None,"C":None,"P":325,'b':'transparent','B':'black'} ) ) )
        return sorted(matchLst,key=lambda x:(x[0],x[1]))
    except Exception as e: 
        print('An error occured')
