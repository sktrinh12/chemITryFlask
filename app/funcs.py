import math
import random
import networkx as nx
from functools import reduce
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource,MultiLine, Circle
from bokeh.models.graphs import from_networkx
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

def genBarPlot(binNum,MWdata):
    binNum = int(binNum)
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
            mol.title = cname
            svg = mol.write('svg',opt={'C':None,'P':400,'u':None,'b':'transparent','B':'black','d':None}) #P - scale bond length, C-no carbon drawn, backgrd trans, bonds-black,d-no title shown
            return (svg,cname,'true')
        else:
            return (f'<strong>{csid} does not exist in the ChemSpider DB!</strong>','','false')
    except Exception as e:
        error_msg =  (f'An error occured when processing that ChemSpider ID ({e})','','false')
        return error_msg

def smrtSrch(query,dfm): 
    try:
        matchLst=[]  
        highlighter = pybel._operations['highlight']
        smarts = pybel.Smarts(query)
        for name,smi in zip(dfm['cname'],dfm['smi']):
            mol = pybel.readstring('smi',smi)
            if smarts.findall(mol):    
                mol.removeh()
                mol.title = name
                highlighter.Do(mol.OBMol, query+' red')
                matchLst.append( (name,mol.write('svg',opt={"u":None,"C":None,"P":150,'b':'transparent','B':'black','d':None} ) ) )
                # mol.OBMol.Clear() if allowed to run will clear form df entirely, & can't view in subsearch again
        LstRslt = sorted(matchLst,key=lambda x:(x[0],x[1]))
        lengthLst = len(LstRslt)
        return (LstRslt,lengthLst)
    except Exception as e: 
        print('An error occured')

def convertDFtoNumFeatures(dfm):
    dfm_numFeatures = dfm[['csid','cname','amass','logp','hbd','hba','numrotbonds','enthalpy','density','bp','arings','numN','numO','sssr','stereoctr','isnp','veberv']]
    dfm_numFeatures.loc[:,'csid'] =dfm_numFeatures['csid'].apply(lambda x : str(x))
    dfm_numFeatures = dfm_numFeatures.set_index('csid')
    clipStr = lambda x: round(float(x.split('±')[0]),1) if x else np.nan
    dfm_numFeatures.loc[:,'enthalpy'] = dfm_numFeatures['enthalpy'].apply(clipStr)
    dfm_numFeatures.loc[:,'density'] = dfm_numFeatures['density'].apply(clipStr)
    dfm_numFeatures.loc[:,'bp'] = dfm_numFeatures['bp'].apply(clipStr)
    dfm_numFeatures.loc[:,'isnp'] = dfm_numFeatures['isnp'].apply(lambda x : 0 if x == 'non-NP' else 1)
    dfm_numFeatures.loc[:,'enthalpy']=dfm_numFeatures['enthalpy'].fillna(round(dfm_numFeatures['enthalpy'].mean(),2))
    dfm_numFeatures.loc[:,'density']=dfm_numFeatures['density'].fillna(round(dfm_numFeatures['density'].mean(),2))
    dfm_numFeatures.loc[:,'bp']=dfm_numFeatures['bp'].fillna(round(dfm_numFeatures['bp'].mean(),2))
    return dfm_numFeatures

def cosine_similarity(x,y):
    return (x@y)/(np.sqrt(x@x)*np.sqrt(y@y))

def cosine_similarityV(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/np.sqrt(sumxx*sumyy)

def euclidean_dist(xx,yy):
    return np.sqrt(sum([(x - y) ** 2 for x, y in zip(xx, yy)]))

def histBins(lst,bins=10):
    if bins:
        hist,edges = np.histogram(lst,bins=bins)
    else:
        hist,edges = np.histogram(lst)
    return (hist,edges)

def calcAB(dist,rads):
    '''pythagoras theorem to calcuate SOH CAH TOA'''
    c = math.sqrt(dist)
    b = math.sin(rads)*c
    a = math.cos(rads)*c
    return (a,b)

def genWeightVals(dfe):
    '''dfe = dataframe with stdEucd,threshold
       lstOfVals = the column values 
       edges = edge numbers from histogram
       #returns tuple of index and weight value based on euclidean value'''
    lstOfVals = dfe['stdEucd'].tolist()
    _,edges = histBins(lstOfVals)
    lamDiff = lambda x: [abs(x-i) for i in edges].index(min([abs(x-i) for i in edges])) #find index of the minimum values in the difference list
    bin_weight=[]
    for i in lstOfVals:
        bin_category = lamDiff(i)
        bin_weight.append(bin_category)
    wtvals = [list(range(len(edges)))[i] for i in bin_weight]
    return wtvals

def genUnitCircle():
    unitCir_sections = list(map(lambda x: math.pi*x,[1/12,1/12,1/12,1/12,1/12,1/12]))*4 #more radians for the unit circle to make smaller sections
    add=0
    unitCir=[]
    for i in unitCir_sections:
        add += i
        unitCir.append(add) #unit circle in radians, totals to 2pi
    return unitCir

unitCir=genUnitCircle()

def genNetXforBokeh(dfm,q_csid,minThreshold=0.25):
    '''generate networkx dataframe from sql database'''    
    q_cname = dfm.cname[dfm.index==q_csid].item()
    q_csid=str(q_csid)
    dfm_filter = dfm.copy().drop(index=q_csid)
    cnames = dfm_filter.cname.tolist()
    csid_Idx = dfm_filter.index.tolist()
    dfm_filter.drop('cname',axis='columns',inplace=True)
    dfm.drop('cname',axis='columns',inplace=True) 
    dfm_proc = pd.DataFrame({'csid':csid_Idx,
                             'euclidist':[euclidean_dist(dfm.loc[q_csid,:],dfm_filter.loc[csid,:]) for csid in csid_Idx]})
    nrow = dfm_proc.shape[0]
    minEucd = dfm_proc.euclidist.min()
    dfm_proc['stdEucd'] = dfm_proc['euclidist'].apply(lambda x: round(minEucd/x,2))
    dfm_proc[f'threshold_{int(minThreshold*100)}'] = dfm_proc['stdEucd'].apply(lambda x: 0 if x< minThreshold else 1)
    nearestNbr = dfm_proc[dfm_proc[f'threshold_{int(minThreshold*100)}']==1].sort_values(by=['stdEucd'],ascending=False).index #sort based on stdEucd descending
    dfm_proc['weights'] = [0.5]*nrow
    dfm_proc['alpha'] = dfm_proc.weights.copy()
    dfm_proc['lcolour'] = ['#1C7293']*nrow        
    linespace = np.linspace(4,1,len(nearestNbr)) #weights of 4 to 1, spaced by 10 units 
    edgelst = []
    for enum,idx in enumerate(nearestNbr):
        edgelst.append((q_csid,dfm_proc.csid[idx])) #connect edges to the query csid; ones with higher than 0.25 threshold
    lsSeries = pd.Series(data= linespace, index=nearestNbr)
    for idx,val in zip(lsSeries.index,lsSeries): #re-define those weight values to a mapping represented by linespace from 4-1 
        dfm_proc.loc[idx,'weights'] = val #values for above the threshold
        dfm_proc.loc[idx,'alpha'] = 1
        dfm_proc.loc[idx,'lcolour'] = '#1B3B6F' 
    posixy={i:"" for i in dfm_proc['csid']}
    n=len(unitCir)
    for i,cs in enumerate(dfm_proc['csid']): 
        if i > n-1:
            posixy[cs] = calcAB(dfm_proc['euclidist'][i],math.pi/random.randint(3,36)+unitCir[i%n]) #cycle thru list with an addition of pi/28 (slight angle increase)
        else:
            posixy[cs] = calcAB(dfm_proc['euclidist'][i],unitCir[i])
    nodesWithEdges = [el[1] for el in edgelst]
    colour_map = []
    for cs in posixy.keys():
        if cs in nodesWithEdges:
            colour_map.append('#065A82')
        else: 
            colour_map.append('#9EB3C2')  
    dfm_proc['colour'] = colour_map
    dfm_proc['position'] = [posixy[k] for k in posixy.keys()]
    dfm_proc['size'] = [10]*nrow #for node size
    dfm_proc['cname'] = cnames #put back names in final dataframe; had to take out for euclidean distance calcs
    return (dfm_proc.reindex(sorted(dfm_proc.columns), axis=1),q_cname)

def prosDf(q_csid,dfm):
    '''process the dataframe. first convert to numerical based dfm, then generate a new columns for plotting, 
       separate the dataframe into above/below threshold so that the plots can be plotted in certain
       order to maintain correct overlay'''
    dfm_nf = convertDFtoNumFeatures(dfm) #filter columns with numeric values and cleans up
    data,_cname = genNetXforBokeh(dfm_nf,q_csid)
    _alpha=1
    _colour='#21295C'
    _euclidist=0
    _lcolour='#21295C'
    _position=(0,0)
    _size=18
    _stdEucd=0
    _threshold=0
    _weights=0
    data.loc[len(data)] = [_alpha,_cname,_colour,q_csid,_euclidist,_lcolour,_position,_size,_stdEucd,_threshold,_weights] 
    condition = np.array(data['alpha']!=_alpha) #turn into nparray because the '~' invert sign only takes arrays and booleans
    data_b = data[condition] #anything that does not have alpha=1; the nodes that have line_alpha of 0.5
    data_a = data[~condition]
    cs_a = data_a.csid.tolist() #csids from above the threshold
    cs_b = data_b.csid.tolist()
    G = nx.Graph()
    G.add_nodes_from(data.csid) #add nodes to network to run kamada kawai algorithm
    pos={csid:pos for csid,pos in zip(data.csid,data.position)}    
    xs_line_a=[]
    ys_line_a=[]
    xs_node_a=[]
    ys_node_a=[]
    xs_line_b=[]
    ys_line_b=[]
    xs_node_b=[]
    ys_node_b=[]
    position=nx.kamada_kawai_layout(G,pos=pos) #deeper algorithm that further maximizes node spaces
    for cs,pos in position.items():
        if cs == q_csid:
            pos[0],pos[1] = (0,0)  #force query csid to be at (0,0) because the algorithm shifts the x,y values slightly
        if cs in cs_a:
            xs_line_a.append((0,pos[0])) # a line from origin to the node, (0,xi) - (0,yi)
            ys_line_a.append((0,pos[1]))
            xs_node_a.append(pos[0]) 
            ys_node_a.append(pos[1])
        else:
            xs_line_b.append((0,pos[0])) 
            ys_line_b.append((0,pos[1]))
            xs_node_b.append(pos[0]) 
            ys_node_b.append(pos[1])
    src_a = { #dictionary for lines/edges above the threshold
           'xs_line':xs_line_a,'ys_line':ys_line_a,
           'xs_node':xs_node_a,'ys_node':ys_node_a,
           'weight':data_a['weights'],
           'euclidist':data_a['euclidist'],
           'csid':data_a['csid'],
           'colour': data_a['colour'],
           'size':data_a['size'],
           'cname':data_a['cname'],
            'alpha':data_a['alpha'],
            'lcolour':data_a['lcolour']
          }
    src_b = { #dictionary for lines/edges below the threshold
           'xs_line':xs_line_b,'ys_line':ys_line_b,
           'xs_node':xs_node_b,'ys_node':ys_node_b,
           'weight':data_b['weights'],
           'euclidist':data_b['euclidist'],
           'csid':data_b['csid'],
           'colour': data_b['colour'],
           'size':data_b['size'],
           'cname':data_b['cname'],
            'alpha':data_b['alpha'],
            'lcolour':data_b['lcolour']
          }
    return (src_a,src_b)

def plotNetXBokeh(src_abv,src_belw,q_csid):
    max_XNodeVal = max(src_belw['xs_node'])
    max_YNodeVal = max(src_belw['ys_node'])
    buffer = 0.1
    plot = figure(title=f"CSID {q_csid} network", sizing_mode='scale_width',x_range=(-max_XNodeVal-buffer, max_XNodeVal+buffer),y_range=(-max_YNodeVal-buffer, max_YNodeVal+buffer))
    source_belw = ColumnDataSource(src_belw)
    source_abv = ColumnDataSource(src_abv)
    glyph = MultiLine(xs="xs_line", ys="ys_line", line_color='lcolour', line_width='weight',line_alpha='alpha')
    plot.add_glyph(source_belw, glyph)
    plot.add_glyph(source_abv, glyph) #add the above threshold lines last so it overlays the below lines
    plot.circle('xs_node', 'ys_node', source=source_belw, size='size', color='colour',line_color='#020c15',line_width=0.5,name='showhover')
    plot.circle('xs_node', 'ys_node', source=source_abv, size='size', color='colour',line_color='#020c15',line_width=0.5,name='showhover')
    node_hover_tool = hover = HoverTool(names=['showhover'], tooltips="""
        <div style="word-wrap: break-word; width: 400px;">
            <p><span style="font-size: 5; font-weight: bold;">CSID: @csid</span><p>
            <p><span style="font-size: 5; font-weight: bold;">Name: @cname</span><p>
            <p><span style="font-size: 5; font-weight: bold;">EucliDist: @euclidist</span><p>
        </div>
              """)
    plot.add_tools(node_hover_tool)
    plot.toolbar.logo = None
    plot.min_border = 0
    plot.axis.visible = False
    plot.toolbar.autohide = True 
    plot.grid.visible = False
    return plot

