from django.db import models
from django.conf import settings

class CSVData(models.Model):
	File_ID=models.CharField(max_length=10, primary_key=True)
	File_Name=models.CharField(max_length=15)
	File_Src=models.FileField(upload_to="csvfiles/")
	class Meta:
		db_table="CSVData"

class DBData(models.Model):
	Host=models.CharField(max_length=100)
	Username=models.CharField(max_length=100)
	Password=models.CharField(max_length=100)
	Database=models.CharField(max_length=100)
	class Meta:
		db_table="DBData"