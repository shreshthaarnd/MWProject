from django.shortcuts import render, redirect
from django.views.decorators.csrf import *
from app.models import *
import pandas as pd
from app.myutil import *
from django.http import HttpResponse
from app.main import *
import mimetypes
import pymysql
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, filters
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework import status

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
			lt2=[]
			for x in lt:
				z=x['table']
				for y in x['col']:
					primary_key=request.POST.get(z+y)
					field=request.POST.get(z+y+'fields')
					if not primary_key==None:
						primary.append(primary_key)
					if not field==None:
						selected_fields.append(field)
						dic={'table':z,'col':field}
						lt2.append(dic)
				try:
					selected_fieldslt=[]
					selected_fieldsstr=''
					count=0
					for a in lt2:
						if a['table']==z:
							session_key='table'+str(count+1)
							request.session[session_key]=a['table']
							selected_fieldslt.append(a['col'])
							selected_fieldsstr=selected_fieldsstr+a['col']+','
					query="select "+selected_fieldsstr[0:len(selected_fieldsstr)-1]+" from "+z
					#print(query)
					cur.execute(query)
					data=cur.fetchall()
					data2=pd.DataFrame(data,columns=selected_fieldslt)
					data2.to_csv(z+'.csv', index=False)
				except:
					print('error')
		dic={'data':CSVData.objects.all(),
			'data2':tables,
			'fields':getFields(),
			'fields2':lt,
			'primary':primary,
			'selected_fields':selected_fields}
		return render(request,'index.html',dic)
import urllib3
@csrf_exempt
def gen_join(request):
	primary=request.GET.get('primary')
	join_type=request.GET.get('jointype')
	sort_col=request.GET.get('sortcol')
	sort_type=request.GET.get('sorttype')
	out=''
	
	http = urllib3.PoolManager()
	
	try:
		a=request.session['table1']
		CSV_obj=CSVData.objects.all()
		df_a=pd.read_csv('df_'+CSV_obj[0].File_Name+'.csv')
		df_b=pd.read_csv('df_'+CSV_obj[1].File_Name+'.csv')
		df_c=Transform_join(df_a, df_b, primary, join_type)
		df_d=Transform_sort(df_c,sort_col,sort_type)
		out=df_d.to_html()
		r = http.request(
	     'POST',
	     'http://127.0.0.1:8000/CallTransformAPI/',
	     fields={'type':'csv','primary': primary,'join_type':join_type,'sort_col':sort_col,'sort_type':sort_type})
		
	except:
		df_a=pd.read_csv('table1.csv')
		df_b=pd.read_csv('table2.csv')
		df_c=Transform_join(df_a, df_b, primary, join_type)
		df_d=Transform_sort(df_c,sort_col,sort_type)
		out=df_d.to_html()

	dic={'data':CSVData.objects.all(),
			'fields':getFields(),
			'primary':primary,
			'outdata':out[36:len(out)-8]}
	return render(request,'index.html',dic)

@csrf_exempt
@api_view(['POST',])
def CallTransformAPI(request):
	data=request.data
	print(data)
	if data['type']=='csv':
		CSV_obj=CSVData.objects.all()
		df_a=pd.read_csv('df_'+CSV_obj[0].File_Name+'.csv')
		df_b=pd.read_csv('df_'+CSV_obj[1].File_Name+'.csv')
		df_c=Transform_join(df_a, df_b, data['primary'], data['join_type'])
		df_d=Transform_sort(df_c,data['sort_col'],data['sort_type'])
		out=df_d.to_html()
		return Response({'output':out})
	else:
		df_a=pd.read_csv('table1.csv')
		df_b=pd.read_csv('table2.csv')
		df_c=Transform_join(df_a, df_b, data['primary'], date['join_type'])
		df_d=Transform_sort(df_c,data['sort_col'],data['sort_type'])
		out=df_d.to_html()
		return Response({'output':out})

def downloadCSV(request):
	fl_path = 'out2.csv'
	filename = 'out2.csv'
	fl = open(fl_path, 'r')
	mime_type, _ = mimetypes.guess_type(fl_path)
	response = HttpResponse(fl, content_type=mime_type)
	response['Content-Disposition'] = "attachment; filename=%s" % filename
	return response