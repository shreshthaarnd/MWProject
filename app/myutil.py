import pandas as pd
from app.models import *
from app.main import *

def getFields():
	lt=[]
	dic={}
	for x in CSVData.objects.all():
		lt1=[]
		df=pd.read_csv('media/'+str(x.File_Src))
		for y in df.keys():
			lt1.append(y)
		dic={'fileid':x.File_ID,
			'fields':lt1}
		lt.append(dic)
	return lt

def performjoin():
	df=''
	df2=''
	for x in CSVData.objects.all():
		df=pd.read_csv('media/'+str(x.File_Src))
		break
	for x in CSVData.objects.all():
		df2=pd.read_csv('media/'+str(x.File_Src))
	return Transform_join(df,df2,'CustomerID','inner')