from django.shortcuts import render, redirect
from django.views.decorators.csrf import *
from app.models import *
import pandas as pd
from app.myutil import *
from django.http import HttpResponse
from app.main import *
import mimetypes

def index(request):
	#return HttpResponse(performjoin())
	dic={'data':CSVData.objects.all(),
		'fields':getFields()}
	return render(request,'index.html',dic)

@csrf_exempt
def saveCSV(request):
	if request.method=='POST':
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
import csv
@csrf_exempt
def gen_df(request):
	if request.method=='POST':
		fields=getFields()
		primary=[]
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


		dic={'data':CSVData.objects.all(),
			'fields':getFields(),
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