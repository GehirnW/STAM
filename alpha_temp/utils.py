# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 10:14:23 2018

@author: admin
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
import pymysql
import time
from functools import wraps
import os

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
 
  
def winsorize(ts, method, alpha, nsigma):
    """
    recognize extreme value and replace these with up_value or down_value
    
    Params:
        ts: 
            pd.Series, cross section factor
        method:
            'quantitles':
                data under alpha/2 percentile or above (1 - alpha/2) 
                percentile as extreme values
            'mv':
                data deviate the mean beyond nsigma * std as extreme values
                this method may need several times
            'mad':
                use Median Absolute Deviation(MAD) instead of mean
                md = median(ts)
                MAD = median(|ts - md|)
                use 1.483 * MAD instead of std
                this method is more robust than 'mv'
            'boxplot':
                IOR = Q3 - Q1
                data beyong [Q1 - 3 * IQR, Q3 + 3 * IQR] as abnormal values
                boxplot is not sensitive with extreme values
                when tha data is positive skew and right fat tailed, too much 
                data will divide into extreme values
            'boxplot_skew_adj':
                md = median(ts)
                mc = median(((x_i - md) - (md - x_j)) / (x_i - x_j))
                where x_i > md and x_j < md
                L = ... and U = ...
        [optional]:
            alpha: valid for method = 'quantitles'
            nsigma: vallid for method = 'mv' and 'mad'
    Return:
        ts,pd.Series                
    """

    if method == 'quantitles':
        d = ts.quantile(alpha / 2.0)
        u = ts.quantile(1 - alpha / 2.0)
    elif method == 'mv':
        sigma = ts.std() 
        d = ts.mean() - sigma * nsigma
        u = ts.mean() + sigma * nsigma
    elif method == 'mad':
        md = ts.median()
        MAD = (ts -  md).abs().median() * 1.483
        d = md - MAD * nsigma
        u = md + MAD * nsigma
    elif method == 'boxplot':
        Q1 = ts.quantile(0.25)
        Q3 = ts.quantile(0.75)
        IQR = Q3 - Q1
        d = Q1 - 3 * IQR
        u = Q3 + 3 * IQR
    elif method == 'boxplot_skew_adj':
        md = ts.median()
        x_u, x_d = ts[ts > md], ts[ts < md]
        x_u = x_u.reset_index(drop = True)
        x_d = x_d.reset_index(drop = True)
        h = np.zeros((len(x_u),len(x_d)))
        for i in range(len(x_u)):
            for j in range(len(x_d)):
                h[i,j] = (x_u.iloc[i] + x_d.iloc[j] - 2 * md)/ \
                            (x_u.iloc[i] - x_d.iloc[j])
        mc = np.median(h.flatten())
        Q1 = ts.quantile(0.25)
        Q3 = ts.quantile(0.75)
        IQR = Q3 - Q1
        if mc >= 0:
            d = Q1 - 1.5 * np.exp(-3.5 * mc) * IQR
            u = Q1 + 1.5 * np.exp(4 * mc) * IQR
        else:
            d = Q1 - 1.5 * np.exp(-4 * mc) * IQR
            u = Q1 + 1.5 * np.exp(3.5 * mc) * IQR
    else:
        raise ValueError('No method called: ', method)
    ts[ts > u] = u
    ts[ts < d] = d       
    return ts
        

def standardize(ts,cap,method):
    """
    use cap_weighted mean to standardize the factor
    
    Params:
        ts:
            pd.Series, cross section factor data
        cap:
            pd.Series, cross section cap data, the secID is matched one by one
            available for cap_weighted
        method:
            'cap_weighted' or 'average'
    Return:
        ts:
            pd.Series    
    """
    nan_label = np.where(np.isnan(ts))[0]
    ts[nan_label] = 0
    if method == 'cap_weighted':
        mean = np.average(ts, weights = cap)
    else:
        mean = np.average(ts)
    ts = (ts - mean) / ts.std()
    ts[nan_label] = np.nan
    return ts
@timer
def alpha_preprocess(df):
    """
    firstly,winsorize the factor(mad method, 3)
    secondly, standardize the factor
    Params:
        df: raw factor data,multi-index,['date','ID']
    """
    df1 = df.unstack()
    df_mod = pd.DataFrame([])
    for i in range(np.size(df1,0)):
        ts = df1.iloc[i,:]
        ts_mod = ts.dropna()
        ts_win = winsorize(ts_mod, 'mad', None, 3)
        ts_stand = standardize(ts_win,None,'average')
        ts_stand1 = pd.DataFrame(ts_stand).T
        ts_stand2 = ts_stand1.stack()
        df_mod = pd.concat([df_mod,ts_stand2], axis = 0)
        print(i)
    return df_mod
    
def style_stand(df,cap):
    for i in range(np.size(df,1)):
        df.iloc[:,i] = standardize(df.iloc[:,i],cap)
    return df

def orthogonal(df,indus,style):
    """
    orthogonal
    factors which gets rid of the effect of industry and style factors
    
    """
    
def get_industry_matrix(industries):
    """
    get the industry dummy matrix
    Param:
        industries: 
            pd.Series,index = secID,value = 行业名称
    Return:
        df:
            pd.DataFrame,industry dummy matrix
    """
    sec_ids = industries.index.tolist()
    nb_sec_ids = len(sec_ids)
    unique_industry = industries.unique()
    nb_unique_industry = len(unique_industry)
    matrix = np.zeros([nb_sec_ids,nb_unique_industry])
    for i in range(nb_sec_ids):
        col_index = np.where(unique_industry == industries[i])[0]
        matrix[i,col_index] = 1.0 
    df = pd.DataFrame(matrix)
    df.index = sec_ids
    return df 

    
def get_resi_factor(factor,indus,style):
    """
    compute the pure factor values which gets rid of the effect of industries and style factor
    ------------------------
    Param:
        factor:
            pd.DataFrame,multi-index, index = ['date','secID'] 
        indus:
            pd.DataFrame, industry dummy matirx, index = secID
        style:
            pd.DataFrame,columns = [style factor], index = secID
    Return:
        pure factor
    """
    cap = pd.DataFrame(style['Size'])
    Y = factor.unstack()
    X_temp = pd.concat([indus,style], axis = 1)
#    X = sm.add_constant(X_temp)
    wls_model = sm.WLS(Y,X_temp,weights = cap)
    results = wls_model.fit()
    factor_resi = results.resid
    return factor_resi

def get_pure_return(ret,indus,style):
    """
    compute the ret which gets rid of indus effects and style effects
    -------------
    Param:
        ret:
            index = 'secID', ret of secID
        indus:
            pd.DataFrame, industry dummy matrix, index = secID
        style:
            pd.DataFrame,columns = [style factor], index = secID

    Return:
        
    
    """
#    cap = pd.DataFrame(style['Size'])
    Y = ret
    X_temp = pd.concat([indus,style], axis = 1)
#    X = sm.add_constant(X_temp)
    wls_model = sm.WLS(Y,X_temp)
    results = wls_model.fit()
    ret_resi = results.resid
    return ret_resi


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

 


class Connector:
    def __init__(self):
#        if db == 'quant':
        self.config = {
                        'host': 'magiquant.mysql.rds.aliyuncs.com',
                        'port': 3306,
                        'user':'haoamc',
                        'passwd':'voucher.seem.user',
                        'db': 'quant'
                        }
                        
        self.conn = pymysql.connect(**self.config)
        self.cursor = self.conn.cursor()
    
    def __del__(self):
        self.conn.close()
    
    def get_tradedate(self,begin,end):
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
        query = "SELECT calendar_date FROM trade_calendar WHERE is_trade_day= 1 AND \
                calendar_date >= '%s' AND calendar_date <= '%s';"%(begin,end)
        self.cursor.execute(query)
        data = pd.DataFrame(list(self.cursor.fetchall()))
        data.columns = ['date']
#        data = pd.DataFrame(pd.to_datetime(data['date']))
        return data
        
    def get_style_factor_from_sql(self,mode,begin,end,table_name):
        """
        get barra style factor from sql,including Beta, Momentum,Size,EY,RV,Growth,\
        BP,Leverage,Liquidity
        ----------------------------------
        Params:
            begin:
                str,eg: '1999-01-01'
            end:
                str,eg: '2017-12-31'
        Return:
            pd.DataFrame,multi-index        
        """
        if mode == 0 :
            query = "SELECT * FROM %s WHERE trade_date = '%s';"%(table_name,begin)
        else:
            query = "SELECT * FROM barra_style_factors_mod WHERE trade_date >= '%s' AND\
            trade_date <= '%s';"%(begin,end)
        self.cursor.execute(query)
        data = pd.DataFrame(list(self.cursor.fetchall()))
        data.columns = ['date','secID','Beta','Momentum','Size','EY','RV','Growth',\
                            'BP','Leverage','Liquidity']
        
#        data['date'] = pd.to_datetime(data['date'])
#        data = data.set_index('ID')
#        data = data.set_index([data['date'], data.index],drop = True)
        del data['date']
        data = data.set_index('secID')
        return data
    
    def get_indus(self,date):
        """
        get all industry information
        ------------------------
        Params:
            date:str, eg:"2010-01-01"
        Returns:
            pd.Series,index = secID,columns = ['sectorID']
        """
        query = "SELECT stock_id,industry_sw FROM stock_sector WHERE trade_date = '%s';"%(date)
        self.cursor.execute(query)
        data = pd.DataFrame(list(self.cursor.fetchall()))
        data.columns = ['secID','sectorID']
        data = data.set_index('secID')
        return data
    
    def get_ret(self,date):
        """
        get all stocks' daily ret
        ----------------------
        Params:
            date: str,eg: '2010-01-01'
        Return:
            
        """
        query = "SELECT stock_id, PctChg FROM stock_market_data WHERE trade_date = '%s';"%(date)
        self.cursor.execute(query)
        data = pd.DataFrame(list(self.cursor.fetchall()))
        data.columns = ['secID','ret']
        data = data.set_index('secID')
        return data
    
    def get_cap(self,date):
        """
        get all stocks' daily cap
        ------------------------
        Params:
            date:str,eg:"2010-01-01"
        Return:
            pd.DataFrame,columns = ['secID','TotalValue']
            
        """
        query = "SELECT stock_id,TotalValue FROM stock_alpha_factors WHERE trade_date = '%s';"%(date)
        self.cursor.execute(query)
        data = pd.DataFrame(list(self.cursor.fetchall()))
        data.columns = ['secID','cap']
        data = data.set_index('secID')
        return data
        

    def get_ret_daily(self,date,stocklist):
        """
        get the daily ret of certain stocklist
        """
        ret_all = self.get_ret(date)
        ret = extract_part_from_all(stocklist,ret_all,'secID')
        ret = ret.set_index('secID')
        return ret
    
    def get_cap_daily(self,date,stocklist):
        """
        get the daily cap of certain stocklist
        Params:
            date:
                str, eg:"2010-01-01"
            stocklist:
                list of str
        Return:
            pd.DataFrame
        """
        cap_all = self.get_cap(date)
        cap = extract_part_from_all(stocklist,cap_all,'secID')
        cap = cap.set_index('secID')
        return cap
    
        
    def get_alpha(self,date,factor_name):
         """
         get the alpha factor from sql
         """
         query =  "SELECT stock_id,%s FROM alpha_raw WHERE trade_date = '%s';"%(factor_name,date)
         self.cursor.execute(query)
         data = pd.DataFrame(list(self.cursor.fetchall()))
         data.columns = ['secID',factor_name]
         return data

        

if __name__ == '__main__':
    #############################################################
    file = '..//alpha_temp//data'
    file_save = '..//alpha_temp//data_mod'
    filelist = os.listdir(file)
#    for i in range(3,len(filelist)):
    # 3，7，15，17，22
    for i in range(len(filelist)):
        filename = file + '/' + filelist[i]
        alpha = pd.read_csv(filename)
#        alpha.columns = ['date','ID','alpha73']
        alpha = alpha.set_index(['date','ID'])
        alpha = alpha_preprocess(alpha)
        file_save_name = file_save + '/' + filelist[i]
        alpha.to_csv(file_save_name)
        print(i)
    
#    #################### get standard style factor and pure ret################
#    #####################upload only end 2017-08-09################################
#    connector = Connector()
#    trade_date = connector.get_tradedate('2017-08-11','2017-08-12') 
#    style = pd.DataFrame([])
#    ret_resi_all = pd.DataFrame([])
#    for i in range(len(trade_date)):       
#        date = trade_date.iloc[i,0]
#        ret = connector.get_ret(date)
#        indus = connector.get_indus(date)
#        style_factor = connector.get_style_factor_from_sql(0,date,None,'barra_style_factors_mod')
#        cap = connector.get_cap(date)
#        data_all = pd.concat([ret,indus,style_factor,cap], axis = 1, join  = 'inner')
#        
#        industry_matrix = get_industry_matrix(data_all['sectorID'])
#        style_factor_stand = style_stand(pd.DataFrame(data_all.iloc[:,2:11]),data_all['cap'])
#        
##        ret_resi = get_pure_return(pd.DataFrame(data_all['ret']),industry_matrix,style_factor_stand)
#        
#        style_factor_stand['date'] = date
#        style = pd.concat([style,style_factor_stand], axis = 0)
##        ret_resi_temp = pd.DataFrame(ret_resi)
##        ret_resi_temp.columns = ['ret']
##        ret_resi_temp['date'] = date
##        ret_resi_all = pd.concat([ret_resi_all,ret_resi_temp], axis = 0)
#        print(i)
#    style.to_csv('..\\analyzer\\style_temp.csv')
##    ret_resi_all.to_csv('..\\analyzer\\ret3.csv')
        

    
                

    
    
    
    