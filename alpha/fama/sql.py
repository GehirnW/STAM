# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 13:04:18 2018

@author: admin
"""

from sqlalchemy import create_engine
import pandas as pd
import numpy as np
#config = {
#        'host': 'magiquant.mysql.rds.aliyuncs.com',
#        'port': 3306,
#        'user':'haoamc',
#        'passwd':'voucher.seem.user',
#        'db': 'quant'
#        }
host = 'magiquant.mysql.rds.aliyuncs.com'
port = '3306'
database = 'quant'
user = 'haoamc'
passwd = 'voucher.seem.user'
charset = 'utf8'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(user,passwd,host,port,database)

#engine = create_engine(DB_URI,echo = True)
##data0 = pd.read_csv('..//..//analyzer//barra_aft.csv', index_col = 0)
##data0.columns = ['trade_date','stock_id','Beta','Momentum','Size','EY','RV','Growth',\
##                            'BP','Leverage','Liquidity']
##data1 = pd.read_csv('..//..//analyzer//barra_aft2.csv',index_col = 0)
##data2 = pd.read_csv('..//..//analyzer//barra_aft3.csv',index_col = 0)
##data = pd.concat([data0,data1,data2], axis = 0)
#style1 = pd.read_csv('..//..//analyzer//ret1.csv',index_col = 0)
#style2 = pd.read_csv('..//..//analyzer//ret2.csv',index_col = 0)
#data = pd.concat([style1,style2], axis = 0)
#data['stock_id'] = data.index.tolist()
#data = data.drop_duplicates()
#data = data.round(5)
#data.columns = ['ret','trade_date','stock_id']
##data.columns = ['stock_id','Beta','Momentum','Size','EY','RV','Growth',\
##                            'BP','Leverage','Liquidity','trade_date']
#data.to_sql(name = 'pure_ret',con = engine, if_exists = 'replace',index = False,chunksize = 1000)

##########################################################################################
################upload barra_stand########################################################
#engine = create_engine(DB_URI,echo = True)
#data0 = pd.read_csv('..//..//analyzer//barra_aft.csv', index_col = 0)
#data0.columns = ['trade_date','stock_id','Beta','Momentum','Size','EY','RV','Growth',\
#                            'BP','Leverage','Liquidity']
#data1 = pd.read_csv('..//..//analyzer//barra_aft2.csv',index_col = 0)
#data2 = pd.read_csv('..//..//analyzer//barra_aft3.csv',index_col = 0)
#data = pd.concat([data0,data1,data2], axis = 0)
#data = data.drop_duplicates()
#data = data.round(5)
#data.columns = ['stock_id','Beta','Momentum','Size','EY','RV','Growth',\
#                            'BP','Leverage','Liquidity','trade_date']
#data.to_sql(name = 'barra_style_factors_stand',con = engine, if_exists = 'replace',index = False,chunksize = 1000)
########################################################################################
################ upload pure_ret######################################################
engine = create_engine(DB_URI,echo = True)
data = pd.read_csv('..//..//analyzer//ret_all.csv')
data = data.round(5)
data.columns = ['stock_id','ret','trade_date','timelog','indus']
cols = list(data)
cols.insert(0,cols.pop(cols.index('trade_date')))
data = data.ix[:,cols]
data.to_sql(name = 'pure_ret',con = engine, if_exists = 'replace',index = False,chunksize = 1000)

#################################################################################################
######################upload alpha_raw#################################
#engine = create_engine(DB_URI,echo = True)
#data = pd.read_csv('..//data//alpha_temp.csv')
#data = data.drop_duplicates()
##data = data.round(10)
#data = pd.DataFrame(np.nan_to_num(data))
#data.columns = ['trade_date','stock_id','alpha1','alpha2','alpha3','alpha5','alpha6','alpha7','alpha8','alpha9','alpha10']
#
#
##data = pd.DataFrame(np.nan_to_num(data))
#pd.io.sql.to_sql(data,name = 'alpha_raw',con = engine, if_exists = 'replace',index = False,chunksize = 1000)