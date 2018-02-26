# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 10:34:55 2018

@author: admin
"""
"""
in order to get the fama factor of each index
the dataset can be construct as followed:
    [date,index,beta,SMB,HML]
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
def get_factor_from_sql(mode,begin,end):
    """
    get factor from sql: TotalValue, PB
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        if mode == 0:
            query = "SELECT stock_id,TotalValue,PB FROM stock_alpha_factors WHERE\
                    trade_date = '%s';"%(begin)
        else:
            query = "SELECT trade_date,stock_id,TotalValue,PB FROM stock_alpha_factors WHERE \
                trade_date >= '%s' AND trade_date <= '%s'; "%(begin,end)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        data.columns = ['ID','TotalValue','PB']
        return data
    finally:
        if conn:
            conn.close()

@timer
def get_index_component(date,index_id):
    """
    get the component of index on a certain day
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT stock_id FROM index_constitution WHERE\
                trade_date = '%s' AND index_id = '%s';"%(date,index_id)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        data.columns = ['stock_id']
        return data
    finally:
        if conn:
            conn.close()
            
@timer
def extract_part_from_all(secID, df, name):
    '''
    从包含secID的dataframe中提取给定secID的数据
    param secID: list of str
    param df: dataframe,其中某一列为包含上述secID的更大范围的secID
    param name: str,df中secID的列名 u'name'格式
    '''
    label = [df[df[name].str.contains(secID[i])].index.tolist() for i in range(len(secID))]
    label_list = list(np.array(label).flatten())
    df_part = df.iloc[label_list, :]
    df_return = df_part.reset_index(drop=True)
    return df_return

@timer
def get_month(date):
    """
    date: datetime
    """
    month = np.zeros((len(date),1))
    for i in range(len(date)):
        month[i,0] = date.iloc[i,0].month
    return pd.DataFrame(month)
    
@timer    
def get_month_date(begin,end):
    """
    get monthly trade date
    Attention:
        the end can not be the last day of month
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT calendar_date FROM trade_calendar WHERE is_trade_day = 1 \
                AND calendar_date >='%s' AND calendar_date <='%s';"%(begin,end)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        data.columns = ['date']

        date = pd.DataFrame(pd.to_datetime(data['date']))
        date.columns = ['date']
        date['month'] = get_month(pd.DataFrame(date['date']))
        temp = pd.DataFrame(date['month'])
        temp_shift = temp.shift(-1)
        date['label'] = temp_shift - temp
        month_date = pd.DataFrame(date['date'][date['label'] == 1])
        month_date = month_date.reset_index(drop = True)
        return month_date
    finally:
        if conn:
            conn.close()

def get_stock_ret(date):
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT stock_id,PctChg FROM stock_market_data WHERE trade_date = '%s';"%(date)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        data.columns = ['ID','ret']
        return data
    finally:
        if conn:
            conn.close()


            

class fama(object):
    def __init__(self,date,index_id):
        self.date = date
        self.index_id = index_id
        self.factor = get_factor_from_sql(0,self.date,None)
        index_component = get_index_component(self.date,self.index_id)
        self.index_component = index_component['stock_id'].tolist()
        self.stock_ret = get_stock_ret(self.date)
    
    @timer
    def SMB_HML(self):
        df = self.factor.copy()
        data = extract_part_from_all(self.index_component, df, 'ID')
        size_mid = np.percentile(data['TotalValue'],50)
        data['S'] = 0
        data['S'] [data['TotalValue'] < size_mid] = 1
        data['B'] = 0
        data['B'][data['TotalValue'] >= size_mid] = 1 
        data['BP'] = 1/data['PB']
        bp_30 = np.percentile(data['BP'],30)
        bp_70 = np.percentile(data['BP'],70)
        data['L'] = 0
        data['L'][data['BP'] < bp_30] = 1
        data['M'] = 1
        data['M'][data['BP'] < bp_30] = 0
        data['M'][data['BP'] >= bp_70] = 0
        data['H'] = 0
        data['H'][data['BP'] >= bp_70] = 1
        data['SL'] = data['S'] * data['L']
        data['SM'] = data['S'] * data['M']
        data['SH'] = data['S'] * data['H']
        data['BL'] = data['B'] * data['L']
        data['BM'] = data['B'] * data['M']
        data['BH'] = data['B'] * data['H']
        
        data = data.set_index(data['ID'])
        """
        Attention!!stock_market_data 中不包含退市股票
        """
        secID = list(set(self.index_component).intersection(set(self.stock_ret['ID'])))
        ret = extract_part_from_all(secID,self.stock_ret,'ID')
        
        ret = ret.set_index(ret['ID'])
        del ret['ID']
        data_all = pd.concat([data,ret], axis = 1)
        
        smb = (np.mean(data_all['ret'][data_all['SL'] == 1]) \
               + np.mean(data_all['ret'][data_all['SM'] == 1]) \
                + np.mean(data_all['ret'][data_all['SH'] == 1]))/3 - \
               (np.mean(data_all['ret'][data_all['BL'] == 1]) \
                + np.mean(data_all['ret'][data_all['BM'] == 1]) \
                + np.mean(data_all['ret'][data_all['BH'] == 1]))/3
                   
        hml = 0.5 * (np.mean(data_all['ret'][data_all['SH'] == 1]) \
                     + np.mean(data_all['ret'][data_all['BH'] ==1 ]))  \
                     - (np.mean(data_all['ret'][data_all['SL'] == 1]) \
                        + np.mean(data_all['ret'][data_all['BL'] ==1 ])) * 0.5
        return smb,hml

        
        
        
if __name__ == '__main__':
    date = get_month_date('2005-01-01','2018-01-02')
    index_list = ['000300.SH','000905.SH']
    result = pd.DataFrame([])
    for i in range(len(index_list)):
        for j in range(len(date)):
            FF = fama(date.iloc[j,0],index_list[i])
            [smb_temp,hml_temp] = FF.SMB_HML()
            temp = pd.DataFrame([date.iloc[j,0],index_list[i],smb_temp,hml_temp]).T
            result = pd.concat([result,temp], axis = 0)
    result.columns = ['date','index','SMB','HML']
    result = result.reset_index(drop = True)
    
#    FF = fama('2015-01-30','000300.SH')
#    [smb,hml] = FF.SMB_HML()
#    date = get_month_date('2015-01-01','2016-01-01')
#    factor = get_factor_from_sql(0,'2015-01-30',None)
#    a1 = get_index_component('2015-01-30','000300.SH')
            
        



