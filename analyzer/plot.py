# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 12:28:24 2018

@author: admin
"""

import pandas as pd
import numpy as np
import pymysql
import statsmodels.api as sm
from datetime import datetime
config = {
        'host': 'magiquant.mysql.rds.aliyuncs.com',
        'port': 3306,
        'user':'haoamc',
        'passwd':'voucher.seem.user',
        'db': 'quant'
        }
        
def get_month_tradedate(begin,end):
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT calendar_date FROM trade_calendar WHERE is_month_end = 1 \
            AND calendar_date >= '%s' AND calendar_date <= '%s';"%(begin,end)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        return data
    finally:
        if conn:
            conn.close()
def get_weekly_tradedate(begin,end):
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT calendar_date FROM trade_calendar WHERE is_week_end = 1 \
            AND calendar_date >= '%s' AND calendar_date <= '%s';"%(begin,end)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        return data
    finally:
        if conn:
            conn.close()           
def get_tradedate(begin,end):
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT calendar_date FROM trade_calendar WHERE is_trade_day = 1 \
            AND calendar_date >= '%s' AND calendar_date <= '%s';"%(begin,end)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        return data
    finally:
        if conn:
            conn.close()

def get_barra_factor_from_sql(date):
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT * FROM barra_style_factors_stand WHERE trade_date = '%s';"%(date)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        data.columns = ['date','secID','Beta','Momentum','Size','EY','RV','Growth',\
                            'BP','Leverage','Liquidity']
        del data['date']
        data = data.set_index('secID')
        return data
    finally:
        if conn:
            conn.close()

def get_ret(date):
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT stock_id,PctChg FROM stock_market_data WHERE trade_date = '%s';"%(date)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        data.columns = ['secID','ret']
        data = data.set_index('secID')
        return data
    finally:
        if conn:
            conn.close()

def get_cap(date):
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT stock_id,TotalValue FROM stock_alpha_factors WHERE trade_date = '%s';"%(date)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        data.columns = ['secID','cap']
        data = data.set_index('secID')
        return data
    finally:
        if conn:
            conn.close()

def get_index_composition(date,index_name):
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT stock_id,weight FROM index_constitution WHERE \
                trade_date = '%s' AND index_id = '%s';"%(date,index_name)
        cursor.execute(query)
        data = pd.DataFrame(list(cursor.fetchall()))
        data.columns = ['secID','weight']
        data = data.set_index('secID')
        return data
    finally:
        if conn:
            conn.close()

def get_factor_ret(date,date_lag):
    """
    compute the style factor ret
    """
    ret = get_ret(date_lag)
    cap = get_cap(date)
    style_factor = get_barra_factor_from_sql(date)
    data_all = pd.concat([ret,cap,style_factor],axis = 1,join = 'inner')
    X = pd.DataFrame(data_all.iloc[:,2:])
    X = sm.add_constant(X)
    wls_model = sm.WLS(pd.DataFrame(data_all['ret']),X,\
                       weights = pd.DataFrame(data_all['cap']))
    results = wls_model.fit()
    factor_ret = results.params[1:]
    return factor_ret

def extract_part_from_all(secID, df, name):
    '''
    从包含secID的dataframe中提取给定secID的数据
    param secID: list of str
    param df: dataframe,其中某一列为包含上述secID的更大范围的secID
    param name: str,df中secID的列名 u'name'格式
    '''
    df = df.reset_index(drop = True)
    label = [df[df[name].str.contains(secID[i])].index.tolist() for i in range(len(secID))]
    label_list = list(np.array(label).flatten())
    df_part = df.iloc[label_list, :]
    df_return = df_part.reset_index(drop=True)
    return df_return    



class barra_monitor(object):
    def __init__(self,begin,end,timelog):
        self.begin = begin
        self.end = end
        self.trade_date = get_tradedate(self.begin,self.end)
#        self.trade_month_date = get_month_tradedate(self.begin,self.end)
        self.weekly_date = get_weekly_tradedate(self.begin,self.end)
        self.timelog = timelog
        
    def factor_ret(self):
        """
        compute the style factor's ret, use WLS regression
        
        """
        factor_ret_all = pd.DataFrame([])
        for i in range(len(self.trade_date) - self.timelog):
            date =  self.trade_date.iloc[i,0]
            date_lag = self.trade_date.iloc[i + self.timelog,0]
            factor_ret = get_factor_ret(date,date_lag)
            factor_ret_all = pd.concat([factor_ret_all,pd.DataFrame(factor_ret).T],axis = 0)
            print(i)
        cumulative_factor_ret = factor_ret_all.cumsum(axis = 0)
        factor_ret_all.index = self.trade_date.iloc[:len(self.trade_date) - self.timelog,0]
        cumulative_factor_ret.index = self.trade_date.iloc[:len(self.trade_date) -self.timelog,0]
        return factor_ret_all,cumulative_factor_ret
    
    def factor_exposure(self):
        """
        compute the hs300 and zz500 weekly exposure on style factors
        """
        exp_hs_all = pd.DataFrame([])
        exp_zz_all = pd.DataFrame([])
        for i in range(len(self.weekly_date)):
            date = self.weekly_date.iloc[i,0]
            factor = get_barra_factor_from_sql(date)
            factor['secID'] = factor.index.tolist()
            stocklist = factor.index.tolist()
            
            hs300 = get_index_composition(date,'000300.SH')
            zz500 = get_index_composition(date,'000905.SH')
            hs300['secID'] = hs300.index.tolist()
            zz500['secID'] = zz500.index.tolist()
            
            stocklist_hs300 = list(set(hs300.index.tolist()).intersection(set(stocklist)))
            stocklist_zz500 = list(set(zz500.index.tolist()).intersection(set(stocklist)))
            stocklist_hs300.sort()
            stocklist_zz500.sort()
            
            factor_hs = extract_part_from_all(stocklist_hs300,factor,'secID')
            factor_zz = extract_part_from_all(stocklist_zz500,factor,'secID')
            hs_weight = extract_part_from_all(stocklist_hs300,hs300,'secID')
            zz_weight = extract_part_from_all(stocklist_zz500,zz500,'secID')
            del factor_hs['secID'],factor_zz['secID'],hs_weight['secID'],zz_weight['secID']
        
           
            exp_hs = pd.DataFrame(np.dot(hs_weight.T,factor_hs))
            exp_zz = pd.DataFrame(np.dot(zz_weight.T,factor_zz))
            
            
            exp_hs_all = pd.concat([exp_hs_all,exp_hs], axis = 0)
            exp_zz_all = pd.concat([exp_zz_all,exp_zz], axis = 0) 
            print(i)
        exp_hs_all.columns = ['Beta','Momentum','Size','EY','RV','Growth',\
                            'BP','Leverage','Liquidity']
        exp_zz_all.columns = ['Beta','Momentum','Size','EY','RV','Growth',\
                                    'BP','Leverage','Liquidity']
        exp_hs_all.index = self.weekly_date.iloc[:,0]
        exp_zz_all.index = self.weekly_date.iloc[:,0]
        return exp_hs_all,exp_zz_all
    
if __name__ == '__main__':
    Barra_monitor = barra_monitor('2017-05-01','2017-06-31',1)
    [factor_ret, cum_factor_ret] = Barra_monitor.factor_ret()
    [exp_hs300,exp_zz500] = Barra_monitor.factor_exposure()
    

    
    
    