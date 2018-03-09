# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 10:00:11 2018

@author: admin
"""

import pandas as pd
from utils import Connector,get_pure_return,get_industry_matrix
#from sqlalchemy import create_engine
#host = 'magiquant.mysql.rds.aliyuncs.com'
#port = '3306'
#database = 'quant'
#user = 'haoamc'
#passwd = 'voucher.seem.user'
#DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(user,passwd,host,port,database)

'''
cumpute the pure ret which gets rid of the style and industry effect
R(t+d) = f_indus * X_indus + f_style * X_style + R_resi
R_resi can be used to compute the factor ret
upload table to sql whose structure is as followed:
    trade_date| stock_id | ret | timelog| indus
    2010-10-01|000001.SH |0.05 | 1      | SW
Attention:
    the trade_date is the date of factor not the ret
    eg, timelog = 1, trade_date = '2009-01-05', which means the date of style-factors is '2009-01-05'
        while the date of ret is '2009-01-06'
'''

connector = Connector()
trade_date = connector.get_tradedate('2009-01-05','2017-12-31')
ret_resi_all = pd.DataFrame([])
timelog = [1,2,3,4,5]
for k in range(len(timelog)):
    log = timelog[k]
    for i in range(len(trade_date) - log):
        date = trade_date.iloc[i,0]
        date_ret = trade_date.iloc[i + log,0]
        ret = connector.get_ret(date_ret)
        indus = connector.get_indus(date)
        style_factor = connector.get_style_factor_from_sql(0,date,None,'barra_style_factors_stand')
        data_all = pd.concat([ret,indus,style_factor], axis = 1, join = 'inner')
        
        industry_matrix = get_industry_matrix(data_all['sectorID'])
        
        ret_resi = get_pure_return(pd.DataFrame(data_all['ret']),industry_matrix,pd.DataFrame(data_all.iloc[:,2:]))
        ret_resi_temp = pd.DataFrame(ret_resi)
        ret_resi_temp.columns = ['ret']
        ret_resi_temp['date'] = date
        ret_resi_temp['timelog'] = log
        ret_resi_all = pd.concat([ret_resi_all,ret_resi_temp],axis = 0)
        print(i)
#    ret_resi_all['timelog'] = log
ret_resi_all['indus'] = 'SW'
ret_resi_all.to_csv('..\\analyzer\\ret_all.csv')    

#'''
#upload to sql(pure_ret)
#'''
#engine = create_engine(DB_URI,echo = True)



#"""
#compute the pure alpha factor which gets rids of the effects of industry and style factors
#before orthogonal, the factor should be winsorized and then be standardized
#X = beta_indus * X_indus + beta_style * X_style + X_resi
#X_resi can be combined with R_resi to compute the factor ret
#upload table to sql whose structure is as followed:
#    trade_date | stock_id | alpha1 |alpha2| ....| indus
#
#"""
#connector = Connector()
#trade_date = connector.get_tradedate('2009-01-05','2017-12-31')
#for i in range(len(trade_date)):
#    date = trade_date.iloc[i,0]
#    
#
#
#"""
#compute the factor ret
#R_resi = X_resi * f
#upload table to sql whose structure is as followed:
#    trade_date | stock_id | timelog | alpha1 | alpha2 | ... | indus
#    
#"""
#
#
#
#"""
#compute the IC of factors
#    IC = corr(pure_ret, pure_factor)
#    quasi_Rank_IC = corr(pure_ret,Rank(pure_factor))
#    Rank_IC = corr(Rank(pure_ret),Rank(pure_factor))
#upload table to sql whose structure is as followed:
#    trade_date | stock_id | timelog | alpha1 | alpha2 | .... | indus
#"""

