from django.shortcuts import render, redirect
from django.views.decorators.csrf import *
from app.models import *
import pandas as pd
from app.myutil import *
from django.http import HttpResponse
from app.main import *
import mimetypes
import pymysql

def index(request):
	dic={'data':CSVData.objects.all(),
		'fields':getFields()}
	return render(request,'index.html',dic)

def resetdb(request):
	CSVData.objects.all().delete()
	dic={'data':CSVData.objects.all(),
		'fields':getFields(),
		'msg1':'Database Deleted Successfully'}
	return render(request,'index.html',dic)

@csrf_exempt
def saveCSV(request):
	if request.method=='POST':
		mode=request.POST.get('mode')
		if mode=='csv':
			filesrc=request.FILES['filesrc']
			f="F00"
			x=1
			fid=f+str(x)
			while CSVData.objects.filter(File_ID=fid).exists():
				x=x+1
				fid=f+str(x)
			x=int(x)
			CSVData(
				File_ID=fid,
				File_Name=filesrc.name,
				File_Src=filesrc
				).save()
			dic={'data':CSVData.objects.all(),
			'fields':getFields()}
			return render(request,'index.html',dic)
		else:
			host=request.POST.get('engine')
			user=request.POST.get('user')
			password=request.POST.get('password')
			database=request.POST.get('db')
			DBData.objects.filter(Database=database).delete()
			if DBData.objects.filter(Database=database).exists():
				return redirect('/index/')
			else:
				DBData(Host=host,Username=user,Password=password,Database=database).save()
			db=pymysql.connect(host,user,password,database)
			cur=db.cursor()
			cur.execute("show tables")
			data=cur.fetchall()
			tables=[]
			for x in data:
				for y in x:
					tables.append(y)
			try:
				dic={}
				lt=[]
				for z in tables:
					query="show columns from "+z
					cur.execute(query)
					data=cur.fetchall()
					lt1=[]
					for x in data:
						lt1.append(x[0])
					dic={'table':z,'col':lt1}
					lt.append(dic)
				db.close()
			except:
				print('error')
			request.session['database'] = database
			dic={'data':CSVData.objects.all(),
			'data2':tables,
			'fields':getFields(),
			'fields2':lt}
			return render(request,'index.html',dic)
import csv
@csrf_exempt
def gen_df(request):
	if request.method=='POST':
		tables=[]
		lt=[]
		primary=[]
		if request.POST.get('mode')=='csv':
			fields=getFields()
			selected_fields=[]
			for x in fields:
				for y in x['fields']:
					primary.append(request.POST.get(x['fileid']+y))
					if not request.POST.get(x['fileid']+y+'fields')==None:
						selected_fields.append(request.POST.get(x['fileid']+y+'fields'))
			
			for x in CSVData.objects.all():
				lt1=[]
				df=pd.read_csv('media/'+str(x.File_Src))
				for y in df.keys():
					for z in selected_fields:
						if y==z:
							lt1.append(z)
					df2=df.loc[:, lt1]
					df2.to_csv('df_'+x.File_Name+'.csv', index=False)
		else:
			database=DBData.objects.filter(Database=request.session['database'])[0]
			db=pymysql.connect(database.Host,database.Username,database.Password,database.Database)
			cur=db.cursor()
			cur.execute("show tables")
			data=cur.fetchall()
			for x in data:
				for y in x:
					tables.append(y)
			try:
				dic={}
				for z in tables:
					query="show columns from "+z
					cur.execute(query)
					data=cur.fetchall()
					lt1=[]
					for x in data:
						lt1.append(x[0])
					dic={'table':z,'col':lt1}
					lt.append(dic)
			except:
				print('error')
			selected_fieldsstr=''
			selected_fields=[]
			for x in lt:
				for y in x['col']:
					if not request.POST.get(x['table']+y+'fields')==None and request.POST.get(x['table']+y)==None:
						primary.append(request.POST.get(x['table']+y))
						selected_fieldsstr=selected_fieldsstr+request.POST.get(x['table']+y+'fields')+','
						selected_fields.append(request.POST.get(x['table']+y+'fields'))
				selected_fieldsstr=selected_fieldsstr[0:len(selected_fieldsstr)-1]
				try:
					query="select "+selected_fieldsstr+" from "+x['table']
					cur.execute(query)
					data=cur.fetchall()
					data2=pd.DataFrame(data,columns=selected_fields)
					data2.to_csv(x['table']+'.csv', index=False)
				except:
					print('error')
			
			#df2.to_csv('df_'+x.File_Name+'.csv', index=False)
		print(primary)
		dic={'data':CSVData.objects.all(),
			'data2':tables,
			'fields':getFields(),
			'fields2':lt,
			'primary':primary,
			'selected_fields':selected_fields}
		return render(request,'index.html',dic)
@csrf_exempt
def gen_join(request):
	primary=request.GET.get('primary')
	join_type=request.GET.get('jointype')
	sort_col=request.GET.get('sortcol')
	sort_type=request.GET.get('sorttype')
	CSV_obj=CSVData.objects.all()
	df_a=pd.read_csv('df_'+CSV_obj[0].File_Name+'.csv')
	df_b=pd.read_csv('df_'+CSV_obj[1].File_Name+'.csv')
	df_c=Transform_join(df_a, df_b, primary, join_type)
	df_d=Transform_sort(df_c,sort_col,sort_type)
	out=df_d.to_html()
	dic={'data':CSVData.objects.all(),
			'fields':getFields(),
			'primary':primary,
			'outdata':out[36:len(out)-8]}
	return render(request,'index.html',dic)
def downloadCSV(request):
	fl_path = 'out2.csv'
	filename = 'out2.csv'
	fl = open(fl_path, 'r')
	mime_type, _ = mimetypes.guess_type(fl_path)
	response = HttpResponse(fl, content_type=mime_type)
	response['Content-Disposition'] = "attachment; filename=%s" % filename
	return response