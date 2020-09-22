import pandas as pd

#df_a= pd.read_csv(r'''C:\Users\dell\Desktop\akhil\customers.csv''')
#df_b= pd.read_csv(r'''C:\Users\dell\Desktop\akhil\orders.csv''')
#column_name='CustomerID'
#join_type='inner'
#sorting_type_value = 0

def Transform_join(df_a,df_b,column_name,join_type):
	df_c=pd.merge(df_a, df_b,on=column_name,how=join_type)
	df_c.to_csv('out1.csv', index=True)
	#print df_c
	return df_c

def Transform_sort(df,column_name,sorting_type_value):
	df_d=df.sort_values(by=column_name, ascending=sorting_type_value)
	df_d.to_csv('out2.csv', index=True)
	#print df
	return df_d

#df_c = Transform_join(df_a,df_b,column_name,join_type)
#df_d = Transform_sort(df_c,column_name,sorting_type_value)
