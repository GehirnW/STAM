#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 16:02:22 2018

@author: joyce
"""

import pandas as pd 
import numpy as np
import pymysql
from sklearn import linear_model
import time
from functools import wraps
config = {
        'host': 'magiquant.mysql.rds.aliyuncs.com',
        'port': 3306,
        'user':'haoamc',
        'passwd':'voucher.seem.user',
        'db': 'quant'
        }
def timer(function):
  @wraps(function)
  def function_timer(*args, **kwargs):
      t0 = time.time()
      result = function(*args, **kwargs)
      t1 = time.time()
      print ("Total time running %s: %s seconds" %(function.__name__, str(round((t1-t0), 2))))
      return result
  return function_timer
  
@timer  
def get_stockdata_from_sql(mode,begin,end,name):
    """
    get stock market data from sql,include: [Open,High,Low,Close,Pctchg,Vol,
    Amount,total_shares,free_float_shares,Vwap]
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        if mode == 0:
            query = "SELECT stock_id,%s FROM stock_market_data WHERE trade_date='%s';"%(name,begin)
        else:
            query = "SELECT trade_date,stock_id,%s FROM stock_market_data WHERE trade_date >='%s' \
                                        AND trade_date <= '%s';"%(name,begin,end)
        cursor.execute(query)
        date = pd.DataFrame(list(cursor.fetchall()))
        if mode == 0:
            date.columns =['ID','name']
        else:
            date.columns =['date','ID','name']
        date = date.set_index('ID')
        date.columns = ['date',name]
        date = date.set_index([date['date'],date.index],drop = True)
        del date['date']
        return date
    finally:
        if conn:
            conn.close() 
@timer 
def get_indexdata_from_sql(mode,begin,end,name,index):
    """
    get stock market data from sql,include: [open,high,low,close,pctchg]
    """    
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        if mode == 0:
            query = "SELECT stock_id,%s FROM index_market_data WHERE trade_date='%s' AND stock_id ='%s';"%(name,begin,index)
        else:
            query = "SELECT trade_date,stock_id,%s FROM index_market_data WHERE trade_date >='%s' \
                                        AND trade_date <= '%s' AND stock_id ='%s';"%(name,begin,end,index)
        cursor.execute(query)
        date = pd.DataFrame(list(cursor.fetchall()))
        if mode == 0:
            date.columns =['ID','name']
        else:
            date.columns =['date','ID','name']
        date = date.set_index('ID')
        date.columns = ['date',name]
        date = date.set_index([date['date'],date.index],drop = True)
        del date['date']
        return date
    finally:
        if conn:
            conn.close()     
    
@timer           
def get_tradedate(begin, end):
    """ 
    get tradedate between begin date and end date
    Params:
        begin:
            str,eg: '1999-01-01'
        end:
            str,eg: '2017-12-31'
    Return:
        pd.DataFrame
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT calendar_date FROM trade_calendar WHERE is_trade_day= 1 AND \
            calendar_date>='" + begin + "' AND calendar_date<='" + end + "';"
        cursor.execute(query)
        date = pd.DataFrame(list(cursor.fetchall()))
        return date
    finally:
        if conn:
            conn.close()
            
def get_fama(begin,end,name,index):
    """
    get fama factor from sql 
    Params:
        begin:
            str,eg:"1990-01-01"
        end:
            str:eg:"2017-12-31"
        index:
            str, index id ,eg :'000300.SH'
        name:
            the name of fama factors ['SMB','HML','MKT']
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT trade_date,%s FROM fama_factor WHERE \
                    stock_id = '%s' AND trade_date >= '%s' AND trade_date <= '%s';"\
                    %(name,index,begin,end)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        data.columns = ['date',name]
        return data
    finally:
        if conn:
            conn.close()
        
        
            
@timer
def Corr(df,num):
    """
    Params:
        data:
            pd.DataFrame,multi-index = ['date','id']
        num:
            int
    Return:
        pd.DataFrame,multi-index = ['date','id']
    """
    df.columns  = ['r1','r2']
    df1 = df['r1']
    df2 = df['r2']
    df1_unstack = df1.unstack()
    df2_unstack = df2.unstack()
    corr = df1_unstack.rolling(num).corr(df2_unstack)
    corr = corr.stack()
    corr = pd.DataFrame(corr)
    corr.columns = ['corr']
    return corr

@timer    
def Cov(df,num):
    """
    Params:
        data:
            pd.DataFrame,multi-index = ['date','id']
        num:
            int
    Return:
        pd.DataFrame,multi-index = ['date','id']
    """
    df.columns  = ['r1','r2']
    df1 = df['r1']
    df2 = df['r2']
    df1_unstack = df1.unstack()
    df2_unstack = df2.unstack()
    corr = df1_unstack.rolling(num).cov(df2_unstack)
    corr = corr.stack()
    corr = pd.DataFrame(corr)
    corr.columns = ['cov']
    return corr
    
@timer
def Delta(df,num):
    """
    Params:
        df:
            pd.DataFrame,multi-index = ['date','ID'],columns = ['alpha']
        num:
            int
    Return:
        pd.DataFrame,multi-inde = ['date','ID']
    """
    df_unstack = df.unstack()
    df_temp = df_unstack.shift(num)
    df_temp1 = df_unstack - df_temp
    df_final = df_temp1.stack()
    return df_final

@timer    
def Delay(df,num):
    """
    Params:
        df:
            pd.DataFrame,multi-index = ['date','ID'],columns = ['alpha']
        num:
            int
    Return:
        pd.DataFrame,multi-index = ['date','ID']
    """
    df_unstack = df.unstack()
    df_temp = df_unstack.shift(num)
    df_final = df_temp.stack()
    return df_final

@timer
def Rank(df):
    """
    Params:
        df: pd.DataFrame,multi-index = ['date','ID'],columns = ['alpha']
    Return:
        pd.DataFrame，multi-index = ['date','ID'],columns = ['alpha']
    """
    df = df.swaplevel(0,1)
    df_mod = df.unstack()
    df_rank = df_mod.rank(axis = 1)
    df_final_temp = df_rank.stack()
    # 内外层索引进行交换
    df_final = df_final_temp.swaplevel(0,1)
    return df_final

@timer
def Cross_max(df1,df2):
    """
    Params:
        df1: 
            pd.DataFrame,multi-index = ['date','ID']
        df2:
            pd.DataFrame,multi-index = ['date','ID']

    """
    df = pd.concat([df1,df2],axis =1 ,join = 'inner')
    df_max = np.max(df,axis = 1)
    return df_max    

@timer    
def Cross_min(df1,df2):
    """
    Params:
        df1: 
            pd.DataFrame,multi-index = ['date','ID']
        df2:
            pd.DataFrame,multi-index = ['date','ID']

    """
    df = pd.concat([df1,df2],axis =1 ,join = 'inner')
    df_min = np.min(df,axis = 1)
    return df_min  

@timer
def Sum(df,num):
    """
    Params:
        df:
            pd.DataFrame,multi-index = ['date','ID']
    Returns:
        df: 
            pd.DataFrame,multi-index = ['date','ID']
        
    """
    df_unstack = df.unstack(level = 'ID')
    df_temp = df_unstack.rolling(num).sum()
    df_final = df_temp.stack()
    return df_final

@timer
def Mean(df,num):
    """
    Params:
        df:
            pd.DataFrame,multi-index = ['date','ID']
    Returns:
        df: 
            pd.DataFrame,multi-index = ['date','ID']
        
    """
    df_unstack = df.unstack()
    df_temp = df_unstack.rolling(num).mean() 
    df_final = df_temp.stack()
    return df_final  
@timer
def STD(df,num):
    """
    Params:
        df:
            pd.DataFrame,multi-index = ['date','ID']
    Returns:
        df: 
            pd.DataFrame,multi-index = ['date','ID']
        
    """
    df_unstack = df.unstack()
    df_temp = df_unstack.rolling(num).std() 
    df_final = df_temp.stack()
    return df_final      

@timer
def TsRank(df,num):
    """
    Params:
        df:
            pd.DataFrame,multi-index = ['date','ID']
        num:
            int
    Returns:
        df: 
            pd.DataFrame,multi-index = ['date','ID']    
    """
    df = df.swaplevel(0,1)
    df_unstack = df.unstack()
    date = df_unstack.index.tolist()
    ts_rank = pd.DataFrame([])
    for i in range(num,len(date)):
        df = df_unstack.iloc[i-num:i,:]
        df_rank = df.rank(axis = 0)
        ts_rank_temp = pd.DataFrame(df_rank.iloc[num-1,:]).T
        ts_rank = pd.concat([ts_rank,ts_rank_temp],axis = 0)
    ts_rank = ts_rank.stack()
    ts_rank = ts_rank.swaplevel(0,1)
    return ts_rank

@timer     
def TsMax(df,num):
    """
    Params:
        df:
            pd.DataFrame,multi-index = ['date','ID']
        num:
            int
    Returns:
        df: 
            pd.DataFrame,multi-index = ['date','ID']    
    """
    df_unstack = df.unstack()
    df_temp = df_unstack.rolling(num).max() 
    df_final = df_temp.stack()
    return df_final 
    
@timer    
def TsMin(df,num):
    """
    Params:
        df:
            pd.DataFrame,multi-index = ['date','ID']
        num:
            int
    Returns:
        df: 
            pd.DataFrame,multi-index = ['date','ID']    
    """
    df_unstack = df.unstack()
    df_temp = df_unstack.rolling(num).min() 
    df_final = df_temp.stack()
    return df_final   
    
@timer        
def DecayLinear(df,num):
    """
    Params:
        df:
            pd.DataFrame,multi-index = ['date','ID']
        num:
            int
    Returns:
        df: 
            pd.DataFrame,multi-index = ['date','ID']    
    """
    df_unstack = df.unstack()
    df2 = df.swaplevel(0,1)
    df_unstack2 = df2.unstack()
    secID = df_unstack2.index.tolist()
    array = np.arange(num,0,-1)
    w = pd.DataFrame(array/array.sum())
    date = df_unstack.index.tolist()
    df_wma = pd.DataFrame([])
    for i in range(num,len(date)):
        df_temp = df_unstack.iloc[i-num:i,:]
        df_temp1 = np.multiply(df_temp,w) 
        df_wma_temp = pd.DataFrame(df_temp1.sum(axis = 0))
        df_wma_temp['date'] = date[i]
        df_wma_temp['secID'] = secID
        df_wma_tep = df_wma_temp.set_index([df_wma_temp['date'],df_wma_temp['secID']],drop = True)
        del df_wma_tep['date'],df_wma_tep['secID']
        df_wma = pd.concat([df_wma,df_wma_tep],axis = 0)
    return pd.DataFrame(df_wma)
    
@timer
def SUMIF(mode,condi,num,temp1,temp2):
    """
    Params:
        mode = 0 or 1, if mode = 0, represent >; 1: >=
        temp1 = pd.DataFrame,multi-index = ['date','ID']
        temp2 = pd.DataFrame,multi-index = ['date','ID']
        num = int
    Return:
        pd.DataFrame
    """
    data = pd.concat([condi,temp1,temp2], axis = 1, join  = 'inner')
    data.columns = ['condi','temp1','temp2']
    if mode == 0:
        data['condi'][data['temp1'] <= data['temp2']] = 0
    else:
        data['condi'][data['temp1'] > data['temp2']] =0
    result_unstack = data['condi'].unstack()
    result = result_unstack.rolling(num,min_periods = num).sum()
    result_stack = result.stack()
    return pd.DataFrame(result_stack)
    
@timer   
def Count(mode,temp1,temp2,num):
    """
    Params:
        mode = 0 or 1, if mode = 0, represent >; 1: >=
        temp1 = pd.DataFrame,multi-index = ['date','ID']
        temp2 = pd.DataFrame,multi-index = ['date','ID']
        num = int
    Return:
        pd.DataFrame
    """
    data = pd.concat([temp1,temp2],axis = 1,join = 'inner')
    data.columns = ['c1','c2']
    data['result'] = 0
    if mode == 0:
        data['result'][data['c1'] > data['c2']] = 1
    else:
        data['result'][data['c1'] >= data['c2']] = 1
    result_unstack = data['result'].unstack()
    result = result_unstack.rolling(num,min_periods = num).sum()
    result_stack = result.stack()
    return pd.DataFrame(result_stack)
@timer    
def SMA(df,num1,num2):
    df_unstack = df.unstack()
    if num2 == 1:
        sma_temp = df_unstack.ewm(com = num1,ignore_na = True, min_periods = num1).mean() 
    else:
        sma_temp = df_unstack.ewm(span = num1,ignore_na = True, min_periods = num1).mean()
    sma =  sma_temp.stack()
    return sma
@timer  
def DTM(df_open,df_high):
    df_open_delay = Delay(df_open,1)
    data = pd.concat([df_open,df_high,df_open_delay],axis = 1, join = 'inner')
    data.columns = ['open','high','open_delay']
    diff = pd.DataFrame(data['high'] - data['open'])
    open_delta= pd.DataFrame(data['open'] - data['open_delay'])
    data1 = pd.concat([diff,open_delta],axis = 1, join = 'inner')
    temp = pd.DataFrame(np.max(data1,axis = 1))
    temp.columns = ['temp']
    data_temp = pd.concat([data,temp],axis = 1, join  = 'inner')
    data_temp['alpha'] = data_temp['temp']
    data_temp['alpha'][data_temp['open'] <= data_temp['open_delay']] = 0
    return pd.DataFrame(data_temp['alpha'])

@timer  
def DBM(df_open,df_low):
    df_open_delay = Delay(df_open,1)
    data = pd.concat([df_open,df_low,df_open_delay],axis = 1, join = 'inner')
    data.columns = ['open','low','open_delay']
    diff = pd.DataFrame(data['open'] - data['low'])
    open_delta= pd.DataFrame(data['open'] - data['open_delay'])
    data1 = pd.concat([diff,open_delta],axis = 1, join = 'inner')
    temp = pd.DataFrame(np.max(data1,axis = 1))
    temp.columns = ['temp']
    data_temp = pd.concat([data,temp],axis = 1, join  = 'inner')
    data_temp['alpha'] = data_temp['temp']
    data_temp['alpha'][data_temp['open'] >= data_temp['open_delay']] = 0
    return pd.DataFrame(data_temp['alpha'])
    
@timer      
def Lowday(df,num):
    """
    Params:
        df = pd.DataFrame,mulit-index = ['date','ID']
        num:int
    """
    df_unstack = df.unstack()
    date = df_unstack.index.tolist()
    lowday = pd.DataFrame([])
    for i in range(num,len(date)):
        df_temp = df_unstack.iloc[i-num:i,:]
        df_rank = df_temp.rank(axis = 0, method = 'max')
        df_rank = df_rank.reset_index(drop = True)
        ts_temp = num - np.argmax(df_rank.values, axis = 0)
        
        ts_rank_temp = pd.DataFrame(ts_temp).T
        ts_rank_temp.columns  = pd.DataFrame(df_temp.columns.tolist()).iloc[:,1]
        lowday = pd.concat([lowday,ts_rank_temp],axis = 0)
    lowday['date'] = date[num:]
    lowday = lowday.set_index('date')
    lowday = pd.DataFrame(lowday.stack())
    return lowday
@timer  
def Highday(df,num):
    """
    Params:
        df = pd.DataFrame,mulit-index = ['date','ID']
        num:int
    """
    df_unstack = df.unstack()
    date = df_unstack.index.tolist()
    highday = pd.DataFrame([])
    for i in range(num,len(date)):
        df_temp = df_unstack.iloc[i-num:i,:]
        df_rank = df_temp.rank(axis = 0, method = 'max')
        df_rank = df_rank.reset_index(drop = True)
        ts_temp = num - np.argmax(df_rank.values, axis = 0)
        ts_rank_temp = pd.DataFrame(ts_temp).T
        ts_rank_temp.columns  = pd.DataFrame(df_temp.columns.tolist()).iloc[:,1]
        highday = pd.concat([highday,ts_rank_temp],axis = 0)
    highday['date'] = date[num:]
    highday = highday.set_index('date')
    highday = pd.DataFrame(highday.stack())
    return highday   
@timer 
def HD(high):
    high_delay = Delay(high,1)
    data = pd.concat([high,high_delay],axis = 1, join = 'inner')
    data.columns = ['high','high_delay']
    temp = data['high'] - data['high_delay']
    return pd.DataFrame(temp)
@timer 
def LD(low):
    low_delay = Delay(low,1)
    data = pd.concat([low,low_delay],axis = 1, join = 'inner')
    data.columns = ['low','low_delay']
    temp = data['low_delay'] - data['low']
    return pd.DataFrame(temp)
@timer 
def RegBeta(mode,df1,df2,num):
    df1_unstack = df1.unstack()
    if mode == 1:
        df2_unstack = df2.unstack()
    date = df1_unstack.index.tolist()
    beta = pd.DataFrame([])
    for i in range(num,len(date)):
        df_temp_A = df1_unstack.iloc[i-num:i,:]
        if mode == 1:
            df_temp_B = df2_unstack.iloc[i-num:i,:]
            df_temp_B = df_temp_B.dropna()
            df = pd.concat([df_temp_B,df_temp_A],axis = 1, join  = 'inner')
            df_temp_B = pd.DataFrame(df.iloc[:,0])
            df_temp_A = pd.DataFrame(df.iloc[:,1:])
        beta_temp = pd.DataFrame(np.zeros((1,np.size(df1_unstack,1))))
        for k in range(np.size(df1_unstack,1)):
            Y = pd.DataFrame(df_temp_A.iloc[:,k])
            if mode != 1:
                Y = Y.dropna()
                if len(Y) < num/2:
                    beta_temp.iloc[0,k] = np.nan
                else:
                    X = pd.DataFrame(np.linspace(1,len(Y),len(Y)))
                    regr = linear_model.LinearRegression()
                    regr.fit(X,Y)
                    beta_temp.iloc[0,k] = regr.coef_[0,0]
            else:
                X = pd.DataFrame(df_temp_B.iloc[:,0])
                xy = X.copy()
                xy['y'] = Y
                xy.columns = ['x','y']
                xy_temp = xy.dropna()
                if np.size(xy_temp,0) < 10:
                    beta_temp.iloc[0,k] = np.nan
                else:
                    regr = linear_model.LinearRegression()
                    regr.fit(pd.DataFrame(xy_temp['x']),pd.DataFrame(xy_temp['y']))
                    beta_temp.iloc[0,k] = regr.coef_[0,0] 
            print(k)         
        beta = pd.concat([beta,beta_temp],axis = 0)
    if mode == 1:
        beta.columns  = pd.DataFrame(df1_unstack.columns.tolist()).iloc[:,0]
    else:
        beta.columns  = pd.DataFrame(df1_unstack.columns.tolist()).iloc[:,1]
    beta['date'] = date[num:]
    beta = beta.set_index('date')
    beta_stack = pd.DataFrame(beta.stack())
    return pd.DataFrame(beta_stack)
@timer 
def RegResi(mode,df1,df2,num):
    df1_unstack = df1.unstack()
    if mode == 1:
        df2_unstack = df2.unstack()
    date = df1_unstack.index.tolist()
    beta = pd.DataFrame([])
    for i in range(num,len(date)):
        df_temp_A = df1_unstack.iloc[i-num:i,:]
        if mode == 1:
            df_temp_B = df2_unstack.iloc[i-num:i,:]
        beta_temp = pd.DataFrame(np.zeros((1,np.size(df1_unstack,1))))
        for k in range(np.size(df1_unstack,1)):
            Y = pd.DataFrame(df_temp_A.iloc[:,0])
            Y = Y.dropna()
            if len(Y) < num/2:
                beta_temp.iloc[0,k] = np.nan
            else:
                if mode == 1:
                    X = df_temp_B.iloc[:,k]
                else:
                    X = pd.DataFrame(np.linspace(1,len(Y),len(Y)))
                regr = linear_model.LinearRegression()
                regr.fit(X,Y)
            beta_temp.iloc[0,k] = regr.intercept_[0]       
        beta = pd.concat([beta,beta_temp],axis = 0)
    beta.columns  = pd.DataFrame(df1_unstack.columns.tolist()).iloc[:,1]
    beta['date'] = date[num:]
    beta = beta.set_index('date')
    beta_stack = pd.DataFrame(beta.stack())
    return pd.DataFrame(beta_stack)
           
            
