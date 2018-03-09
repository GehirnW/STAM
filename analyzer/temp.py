# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 16:36:02 2018

@author: admin
"""

import pandas as pd
from datetime import datetime
import numpy as np
import pymysql
from sqlalchemy import create_engine
host = 'magiquant.mysql.rds.aliyuncs.com'
port = '3306'
database = 'quant'
user = 'haoamc'
passwd = 'voucher.seem.user'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(user,passwd,host,port,database)
#config = {
#        'host': 'magiquant.mysql.rds.aliyuncs.com',
#        'port': 3306,
#        'user':'haoamc',
#        'passwd':'voucher.seem.user',
#        'db': 'quant'
#        }
#query = "SELECT * FROM barra_style_factors WHERE trade_date >='%s' AND trade_date <= '%s';"%('20121022','20121024')
#conn = pymysql.connect(**config)
#cursor = conn.cursor()
#cursor.execute(query)
#data = pd.DataFrame(list(cursor.fetchall()))
#data.columns = ['trade_date','stock_id','Beta','Momentum','Size','EY','RV','Growth',\
#                    'BP','Leverage','Liquidity']
#data.to_csv('..\\analyzer\\barra_temp3.csv')                    



##################### transfer date format ###########################
#data1 = pd.read_csv('..\\analyzer\\barra_temp1.csv', index_col = 0)
#data2 = pd.read_csv('..\\analyzer\\barra_temp2.csv',index_col = 0)
#data3 = pd.read_csv('..\\analyzer\\barra_temp3.csv',index_col = 0)
#data = pd.concat([data1,data2,data3], axis = 0)
#data['trade_date'] = [datetime.strptime(str(data.iloc[i,0]),"%Y%m%d").strftime('%Y-%m-%d') \
#     for i in range(np.size(data,0))]
#data.to_csv('..\\analyzer\\barra_temp_aft.csv')

#####################upload barra_aft to sql(barra_style_factors_mod)###############
engine = create_engine(DB_URI,echo = True)
data = pd.read_csv('..\\analyzer\\barra_temp_aft.csv',index_col = 0)
data = data.round(5)
data = data.drop_duplicates()
data.to_sql(name = 'barra_style_factors_mod',con = engine, if_exists = 'append',index = False,chunksize = 1000)

#################################################################################################
###############up load style.csv to sql(barra_style_factors_stand)########################
#engine = create_engine(DB_URI,echo = True)
#data = pd.read_csv('..\\analyzer\\style_temp.csv')
#data = data.round(5)
#data = data.drop_duplicates()
#data.columns = ['stock_id','Beta','Momentum','Size','EY','RV','Growth',\
#                    'BP','Leverage','Liquidity','trade_date']
#cols = list(data)
#cols.insert(0,cols.pop(cols.index('trade_date')))
#data = data.ix[:,cols]
#data.to_sql(name = 'barra_style_factors_stand',con = engine, if_exists = 'append',index = False,chunksize = 1000)

#########################alpha test##########################
#df = pd.DataFrame([])
#for i in range(1,11):        
#    if i != 4:
#        filename = '..\\alpha\\data\\'  + str(i) + '.csv'
#        df1 = pd.read_csv(filename)
#        alpha_name = 'alpha' + str(i)
#        df1.columns = ['date','ID',alpha_name]
#        df1 = df1.set_index(['date','ID'],drop = True)
#        if i == 1:
#            df = pd.concat([df,df1],axis = 1, join = 'outer')
#        else:
#            df = pd.concat([df,df1], axis = 1, join  = 'inner')
#df.to_csv('C:\\Python\\shortTermAlpha\\STAM\\alpha\\data\\alpha_temp.csv')
#        
        