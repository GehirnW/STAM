#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 15:39:02 2018

@author: joyce
"""

import pandas as pd
import numpy as np
from numpy.matlib import repmat
from stats import get_stockdata_from_sql,get_tradedate,Corr,Delta,Rank,Cross_max,\
Cross_min,Delay,Sum,Mean,STD,TsRank,TsMax,TsMin,DecayLinear,Count,SMA,Cov,DTM,DBM,\
Highday,Lowday,HD,LD,RegBeta,RegResi,SUMIF,get_indexdata_from_sql,timer


class stAlpha(object):
    def __init__(self,begin,end):
        self.begin = begin
        self.end = end
        self.close = get_stockdata_from_sql(1,self.begin,self.end,'Close')
        self.open = get_stockdata_from_sql(1,self.begin,self.end,'Open')
        self.high = get_stockdata_from_sql(1,self.begin,self.end,'High')
        self.low = get_stockdata_from_sql(1,self.begin,self.end,'Low')
        self.volume = get_stockdata_from_sql(1,self.begin,self.end,'Vol')
        self.amt = get_stockdata_from_sql(1,self.begin,self.end,'Amount')
        self.vwap = get_stockdata_from_sql(1,self.begin,self.end,'Vwap')
        self.ret = get_stockdata_from_sql(1,begin,end,'Pctchg')
        self.close_index = get_indexdata_from_sql(1,begin,end,'close','000001.SH')
        self.open_index = get_indexdata_from_sql(1,begin,end,'open','000001.SH')
    @timer
    def alpha1(self):
        volume = self.volume
        ln_volume = np.log(volume)
        ln_volume_delta = Delta(ln_volume,1)
        
        close = self.close
        Open = self.open
    
        price_temp = pd.concat([close,Open],axis = 1,join = 'outer')
        price_temp['ret'] = (price_temp['Close'] - price_temp['Open'])/price_temp['Open']
        del price_temp['Close'],price_temp['Open']
        
        r_ln_volume_delta = Rank(ln_volume_delta)
        r_ret = Rank(price_temp)
        rank = pd.concat([r_ln_volume_delta,r_ret],axis = 1,join = 'inner')
        rank.columns = ['r1','r2']
        corr = Corr(rank,6)
        alpha = corr
        alpha.columns = ['alpha1']
        return alpha
        
    @timer    
    def alpha2(self):
        close = self.close
        low = self.low
        high = self.high
        temp = pd.concat([close,low,high],axis = 1,join = 'outer')
        temp['alpha'] = (2 * temp['Close'] - temp['Low'] - temp['High']) \
            / (temp['High'] - temp['Low']) 
        del temp['Close'],temp['Low'],temp['High']
        alpha = -1 * Delta(temp,1)
        alpha.columns = ['alpha2']
        return alpha
        
    @timer    
    def alpha3(self):
        close = self.close
        low = self.low
        high = self.high
        temp = pd.concat([close,low,high],axis = 1,join = 'outer')
        close_delay = Delay(pd.DataFrame(temp['Close']),1)
        close_delay.columns = ['close_delay']
        temp = pd.concat([temp,close_delay],axis = 1,join = 'inner')
        temp['min'] = Cross_max(pd.DataFrame(temp['close_delay']),pd.DataFrame(temp['Low']))
        temp['max'] = Cross_min(pd.DataFrame(temp['close_delay']),pd.DataFrame(temp['High']))
        temp['alpha_temp'] = 0
        temp['alpha_temp'][temp['Close'] > temp['close_delay']] = temp['Close'] - temp['min']
        temp['alpha_temp'][temp['Close'] < temp['close_delay']] = temp['Close'] - temp['max']
        alpha = Sum(pd.DataFrame(temp['alpha_temp']),6)
        alpha.columns = ['alpha3']
        return alpha
        
    @timer
    def alpha4(self):
        close = self.close
        volume = self.volume
        close_mean_2 = Mean(close,2)
        close_mean_8 = Mean(close,8)
        close_std = STD(close,8)
        volume_mean_20 = Mean(volume,20)
        data = pd.concat([close_mean_2,close_mean_8,close_std,volume_mean_20,volume],axis = 1,join = 'inner')
        data.columns = ['close_mean_2','close_mean_8','close_std','volume_mean_20','volume']
        data['alpha'] = -1
        data['alpha'][data['close_mean_2'] < data['close_mean_8'] - data['close_std']] = 1
        data['alpha'][data['volume']/data['volume_mean_20'] >= 1] = 1
        alpha = pd.DataFrame(data['alpha'])
        alpha.columns = ['alpha4']
        return alpha
        
    @timer
    def alpha5(self):
        volume = self.volume
        high = self.high
        r1 = TsRank(volume,5)
        r2 = TsRank(high,5)
        rank = pd.concat([r1,r2],axis = 1,join = 'inner')
        rank.columns = ['r1','r2']
        corr = Corr(rank,5)
        alpha = -1 * TsMax(corr,5)
        alpha.columns = ['alpha5']
        return alpha
        
    @timer    
    def alpha6(self):
        Open = self.open
        high = self.high
        df = pd.concat([Open,high],axis = 1,join = 'inner')
        df['price'] = df['Open'] * 0.85 + df['High'] * 0.15
        df_delta = Delta(pd.DataFrame(df['price']),1)
        alpha = Rank(np.sign(df_delta))
        alpha.columns = ['alpha6']
        return alpha
        
    @timer
    def alpha7(self):
        close = self.close
        vwap = self.vwap
        volume = self.volume
        volume_delta = Delta(volume,3)
        data = pd.concat([close,vwap],axis = 1,join = 'inner')
        data['diff'] = data['Vwap'] - data['Close']
        r1 = Rank(TsMax(pd.DataFrame(data['diff']),3))
        r2 = Rank(TsMin(pd.DataFrame(data['diff']),3))
        r3 = Rank(volume_delta)
        rank = pd.concat([r1,r2,r3],axis = 1,join = 'inner')
        rank.columns = ['r1','r2','r3']
        alpha = (rank['r1'] + rank['r2'])* rank['r3']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha7']
        return alpha
        
    @timer
    def alpha8(self):
        high = self.high
        low = self.low
        vwap = self.vwap
        data = pd.concat([high,low,vwap],axis = 1,join = 'inner')
        data_price = (data['High'] + data['Low'])/2 * 0.2 + data['Vwap'] * 0.2
        data_price_delta = Delta(pd.DataFrame(data_price),4) * -1
        alpha = Rank(data_price_delta)
        alpha.columns = ['alpha8']
        return alpha
        
    @timer
    def alpha9(self):
        high = self.high
        low = self.low
        volume = self.volume
        data = pd.concat([high,low,volume],axis = 1,join = 'inner')
        data['price']= (data['High'] + data['Low'])/2 
        data['price_delay'] = Delay(pd.DataFrame(data['price']),1)
        alpha_temp = (data['price'] - data['price_delay']) * (data['High'] - data['Low'])/data['Vol']
        alpha_temp_unstack = alpha_temp.unstack(level = 'ID')
        alpha = alpha_temp_unstack.ewm(span = 7, ignore_na = True, min_periods = 7).mean()
        alpha_final = alpha.stack()
        alpha = pd.DataFrame(alpha_final)
        alpha.columns = ['alpha9']
        return alpha
    
    @timer
    def alpha10(self):
        ret = self.ret
        close = self.close
        ret_std =  STD(pd.DataFrame(ret),20)
        ret_std.columns = ['ret_std']
        data = pd.concat([ret,close,ret_std],axis = 1, join = 'inner')
        temp1 = pd.DataFrame(data['ret_std'][data['Pctchg'] < 0])
        temp2 = pd.DataFrame(data['Close'][data['Pctchg'] >= 0])
        temp1.columns = ['temp']
        temp2.columns = ['temp']
        temp = pd.concat([temp1,temp2],axis = 0,join = 'outer')
        temp_order = pd.concat([data,temp],axis = 1)
        temp_square = pd.DataFrame(np.power(temp_order['temp'],2))
        alpha_temp = TsMax(temp_square,5)
        alpha = Rank(alpha_temp)
        alpha.columns = ['alpha10']
        return alpha
    
    @timer
    def alpha11(self):
        high = self.high
        low = self.low
        close = self.close
        volume = self.volume
        data = pd.concat([high,low,close,volume],axis = 1,join = 'inner')
        data_temp = (data['Close'] - data['Low']) -(data['High'] - data['Close'])\
                    /(data['High'] - data['Low']) * data['Vol']
        alpha = Sum(pd.DataFrame(data_temp),6)
        alpha.columns = ['alpha11']
        return alpha
    
    @timer    
    def alpha12(self):
        Open = self.open
        vwap = self.vwap 
        close = self.close
        data = pd.concat([Open,vwap,close],axis = 1, join = 'inner')
        data['p1'] = data['Open'] - Mean(data['Open'],10)
        data['p2'] = data['Close'] - data['Vwap']
        r1 = Rank(pd.DataFrame(data['p1']))
        r2 = Rank(pd.DataFrame(np.abs(data['p2'])))
        rank = pd.concat([r1,r2],axis = 1,join = 'inner')
        rank.columns = ['r1','r2']
        alpha = rank['r1'] - rank['r2']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha12']
        return alpha
    
    @timer    
    def alpha13(self):
        high = self.high
        low = self.low
        vwap = self.vwap 
        data = pd.concat([high,low,vwap],axis = 1,join = 'inner')
        alpha = (data['High'] + data['Low'])/2 - data['Vwap']
        alpha  = pd.DataFrame(alpha)
        alpha.columns = ['alpha13']
        return alpha
    
    @timer
    def alpha14(self):
        close = self.close
        close_delay = Delay(close,5)
        close_delay.columns = ['close_delay']
        data = pd.concat([close,close_delay],axis = 1, join = 'inner')
        alpha = data['Close'] - data['close_delay']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha14']
        return alpha
    
    @timer
    def alpha15(self):
        Open = self.open
        close = self.close
        close_delay = Delay(close,1)
        close_delay.columns = ['close_delay']
        data = pd.concat([Open,close_delay],axis = 1,join = 'inner')
        alpha = data['Open']/data['close_delay'] - 1
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha15']
        return alpha
    
    @timer
    def alpha16(self):
        vwap = self.vwap
        volume = self.volume
        data = pd.concat([vwap,volume],axis = 1, join = 'inner')
        r1 = Rank(pd.DataFrame(data['Vol']))
        r2 = Rank(pd.DataFrame(data['Vwap']))
        rank = pd.concat([r1,r2],axis = 1, join = 'inner')
        rank.columns  = ['r1','r2']
        corr = Corr(rank,5)
        alpha = -1 * TsMax(Rank(corr),5)
        alpha.columns = ['alpha16']
        return alpha
    
    @timer
    def alpha17(self):
        vwap = self.vwap
        close = self.close
        data = pd.concat([vwap,close],axis = 1, join = 'inner')
        data['vwap_max15'] = TsMax(data['Vwap'],15)
        data['close_delta5'] = Delta(data['Close'],5)
        temp = np.power(data['vwap_max15'],data['close_delta5'])
        alpha = Rank(pd.DataFrame(temp))
        alpha.columns = ['alpha17']
        return alpha
    
    @timer    
    def alpha18(self):
        """
        this one is similar with alpha14
        """
        close = self.close
        close_delay = Delay(close,5)
        close_delay.columns = ['close_delay']
        data = pd.concat([close,close_delay],axis = 1, join = 'inner')
        alpha = data['Close']/data['close_delay']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha18']
        return alpha
    
    @timer
    def alpha19(self):
        close = self.close
        close_delay = Delay(close,5)
        close_delay.columns = ['close_delay']
        data = pd.concat([close,close_delay],axis = 1, join = 'inner')
        data['temp1'] = (data['Close'] - data['close_delay'])/data['close_delay']
        data['temp2'] = (data['Close'] - data['close_delay'])/data['Close']
        temp1 = pd.DataFrame(data['temp1'][data['Close'] < data['close_delay']])
        temp2 = pd.DataFrame(data['temp2'][data['Close'] >= data['close_delay']])
        temp1.columns = ['temp']
        temp2.columns = ['temp']
        temp = pd.concat([temp1,temp2],axis = 0)
        data = pd.concat([data,temp],axis = 1,join = 'outer')
        alpha = pd.DataFrame(data['temp'])
        alpha.columns = ['alpha19']
        return alpha
    
    @timer
    def alpha20(self):
        close = self.close
        close_delay = Delay(close,6)
        close_delay.columns = ['close_delay']
        data = pd.concat([close,close_delay],axis = 1, join = 'inner')
        alpha = (data['Close'] - data['close_delay'])/data['close_delay'] 
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha20']
        return alpha
    
    @timer
    def alpha21(self):
        close = self.close
        close_mean = Mean(close,6)
        alpha = RegBeta(0,close_mean,None,6)
        alpha.columns = ['alpha21']
        return alpha
    
    @timer
    def alpha22(self):
        close = self.close
        close_mean = Mean(close,6)
        data = pd.concat([close,close_mean],axis = 1,join = 'inner')
        data.columns = ['close','close_mean']
        temp = pd.DataFrame((data['close'] - data['close_mean'])/data['close_mean'])
        temp_delay = Delay(temp,3)
        data_temp = pd.concat([temp,temp_delay],axis = 1,join = 'inner')
        data_temp.columns = ['temp','temp_delay']
        temp2 = pd.DataFrame(data_temp['temp'] - data_temp['temp_delay'])
        alpha = SMA(temp2,12,1)
        alpha.columns = ['alpha22']
        return alpha
         
    @timer    
    def alpha23(self):
        close = self.close
        close_std = STD(close,20)
        close_delay = Delay(close,1)
        data = pd.concat([close,close_std,close_delay],axis = 1, join = 'inner')
        data.columns = ['Close','close_std','close_delay']
        data['temp'] = data['close_std']
        data['temp'][data['Close'] <= data['close_delay']] = 0
        temp = pd.DataFrame(data['temp'])
        sma1 = SMA(temp,20,1)
        sma2 = SMA(pd.DataFrame(data['close_std']),20,1)
        sma = pd.concat([sma1,sma2],axis = 1, join = 'inner')
        sma.columns = ['sma1','sma2']
        alpha = pd.DataFrame(sma['sma1']/sma['sma2'])
        alpha.columns = ['alpha23']
        return alpha
    
    @timer    
    def alpha24(self):  
        close = self.close
        close_delay = Delay(close,5)
        close_delay.columns = ['close_delay']
        data = pd.concat([close,close_delay],axis=1 ,join = 'inner' )
        temp = data['Close'] - data['close_delay']
        temp = pd.DataFrame(temp)
        alpha = SMA(temp,5,1)
        alpha.columns = ['alpha24']
        return alpha
    
    @timer
    def alpha25(self): 
        close = self.close
        close_delta = Delta(close,7)
        ret = self.ret
        r1 = Rank(close_delta)
        r3 = Rank(Sum(ret,250))
        volume = self.volume
        volume_mean = Mean(pd.DataFrame(volume['Vol']),20)
        volume_mean.columns = ['volume_mean']
        data = pd.concat([volume,volume_mean],axis = 1,join = 'inner')
        temp0 = pd.DataFrame(data['Vol']/data['volume_mean'])
        temp = DecayLinear(temp0,9)
        r2 = Rank(temp)
        rank = pd.concat([r1,r2,r3],axis = 1, join = 'inner')
        rank.columns  = ['r1','r2','r3']
        alpha = pd.DataFrame(-1 * rank['r1'] * (1 - rank['r2']) * rank['r3'])
        alpha.columns = ['alpha25']
        return alpha
        
    @timer    
    def alpha26(self):
        close = self.close
        vwap = self.vwap
        close_mean7 = Mean(close,7)
        close_mean7.columns = ['close_mean7']
        close_delay5 = Delay(close,5)
        close_delay5.columns = ['close_delay5']
        data = pd.concat([vwap,close_delay5],axis = 1,join = 'inner')
        corr = Corr(data,230)
        corr.columns = ['corr']
        data_temp = pd.concat([corr,close_mean7,close],axis = 1,join = 'inner')
        alpha = data_temp['close_mean7'] - data_temp['Close'] + data_temp['corr']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha26']
        return alpha
    
    @timer
    def alpha27(self):
        """
        uncompleted
        """
        close = self.close
        close_delay3 = Delay(close,3)
        close_delay6 = Delay(close,6)
        data = pd.concat([close,close_delay3,close_delay6],axis = 1,join = 'inner')
        data.columns = ['close','close_delay3','close_delay6']
        temp1 = pd.DataFrame((data['close'] - data['close_delay3'])/data['close_delay3'] * 100)
        temp2 = pd.DataFrame((data['close'] - data['close_delay6'])/data['close_delay6'] * 100)
        data_temp = pd.concat([temp1,temp2],axis = 1,join = 'inner')
        data_temp.columns = ['temp1','temp2']
        temp = pd.DataFrame(data_temp['temp1'] + data_temp['temp2'])
        alpha = DecayLinear(temp,12)
        alpha.columns = ['alpha27']
        return alpha
        
    @timer    
    def alpha28(self):
        close = self.close
        low = self.low
        high = self.high
        low_min = TsMin(low,9)
        high_max = TsMax(high,9)
        data = pd.concat([close,low_min,high_max],axis = 1,join = 'inner')
        data.columns = ['Close','low_min','high_max']
        temp1 = pd.DataFrame((data['Close'] - data['low_min']) /(data['high_max'] - data['low_min']))
        sma1 = SMA(temp1,3,1)
        sma2 = SMA(sma1,3,1)
        sma = pd.concat([sma1,sma2],axis = 1, join = 'inner')
        sma.columns = ['sma1','sma2']
        alpha = pd.DataFrame(sma['sma1'] * 2 - sma['sma2'] * 3)
        alpha.columns = ['alpha28']
        return alpha
    
    @timer    
    def alpha29(self):
        close = self.close
        volume = self.volume
        close_delay = Delay(close,6)
        close_delay.columns = ['close_delay']
        data = pd.concat([close,close_delay,volume],axis = 1, join = 'inner')
        alpha = (data['Close'] - data['close_delay'])/data['close_delay'] * data['Vol']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha29']
        return alpha
    
    #def alpha30(begin,end):
    @timer
    def alpha31(self):
        close = self.close
        close_delay = Delay(close,12)
        close_delay.columns  = ['close_delay']
        data = pd.concat([close,close_delay],axis = 1, join = 'inner')
        alpha = (data['Close'] - data['close_delay'])/data['close_delay']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha31']
        return alpha
    
    @timer    
    def alpha32(self):
        volume = self.volume
        high = self.high
        r1 = Rank(volume)
        r2 = Rank(high)
        rank = pd.concat([r1,r2],axis = 1,join = 'inner')
        corr = Corr(rank,3)
        r = Rank(corr)
        alpha = -1 * Sum(r,3)
        alpha.columns = ['alpha32']
        return alpha
    
    @timer
    def alpha33(self):
        low = self.low
        volume = self.volume
        ret = self.ret
        low_min = TsMin(low,5)
        low_min_delay = Delay(low_min,5)
        data1 = pd.concat([low_min,low_min_delay],axis = 1,join = 'inner')
        data1.columns  = ['low_min','low_min_delay']
        ret_sum240 = Sum(ret,240)
        ret_sum20 = Sum(ret,20)
        ret_temp = pd.concat([ret_sum240,ret_sum20],axis = 1, join = 'inner')
        ret_temp.columns  = ['ret240','ret20']
        temp1 = pd.DataFrame(data1['low_min_delay'] - data1['low_min'])
        temp2 = pd.DataFrame((ret_temp['ret240'] - ret_temp['ret20'])/220)
        r_temp2 = Rank(temp2)
        r_volume = TsRank(volume,5)
        temp = pd.concat([temp1,r_temp2,r_volume],axis = 1,join = 'inner')
        temp.columns = ['temp1','r_temp2','r_volume']
        alpha = temp['temp1'] * temp['r_temp2'] * temp['r_volume']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha33']
        return alpha
    
    @timer   
    def alpha34(self):
        close = self.close
        close_mean = Mean(close,12)
        close_mean.columns = ['close_mean']
        data = pd.concat([close,close_mean],axis = 1, join = 'inner')
        alpha = pd.DataFrame(data['close_mean']/data['Close'])
        alpha.columns = ['alpha34']
        return alpha
    
    @timer
    def alpha35(self):
        volume = self.volume
        Open = self.open
        open_delay = Delay(Open,1)
        open_delay.columns  = ['open_delay']
        open_linear = DecayLinear(Open,17)
        open_linear.columns = ['open_linear']
        open_delay_temp = DecayLinear(open_delay,15)
        r1 = Rank(open_delay_temp)
        data = pd.concat([Open,open_linear],axis = 1,join = 'inner')
        Open_temp = data['Open'] * 0.65 + 0.35 * data['open_linear']
        rank = pd.concat([volume,Open_temp],axis = 1, join  = 'inner')
        rank.columns  = ['r1','r2']
        corr = Corr(rank,7)
        r2 = Rank(-1 * corr)
        r = pd.concat([r1,r2],axis = 1,join = 'inner')
        r.columns = ['r1','r2']
        alpha = Cross_min(pd.DataFrame(r['r1']),pd.DataFrame(r['r2']))
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha35']
        return alpha
    
    @timer    
    def alpha36(self):
        volume = self.volume
        vwap = self.vwap
        r1 = Rank(volume)
        r2 = Rank(vwap)
        rank = pd.concat([r1,r2],axis = 1,join = 'inner')
        corr = Corr(rank,6)
        temp = Sum(corr,2)
        alpha = Rank(temp)
        alpha.columns = ['alpha36']
        return alpha
    
    @timer
    def alpha37(self):
        Open = self.open
        ret = self.ret
        open_sum = Sum(Open,5)
        ret_sum = Sum(ret,5)
        data = pd.concat([open_sum,ret_sum],axis = 1,join = 'inner')
        data.columns  = ['open_sum','ret_sum']
        temp = data['open_sum'] * data['ret_sum']
        temp_delay = Delay(temp,10)
        data_temp = pd.concat([temp,temp_delay],axis = 1,join  = 'inner')
        data_temp.columns = ['temp','temp_delay']
        alpha = -1 * Rank(pd.DataFrame(data_temp['temp'] - data_temp['temp_delay']))
        alpha.columns = ['alpha37']
        return alpha
    
    @timer
    def alpha38(self):
        high = self.high
        high_mean = Mean(high,20)
        high_delta = Delta(high,2)
        data =  pd.concat([high,high_mean,high_delta],axis = 1,join = 'inner')
        data.columns  = ['high','high_mean','high_delta']
        data['alpha'] = -1 * data['high_delta']
        data['alpha'][data['high_mean'] >= data['high']] = 0
        alpha = pd.DataFrame(data['alpha'])
        alpha.columns = ['alpha38']
        return alpha
    
    @timer
    def alpha39(self):
        close = self.close
        Open = self.open
        vwap = self.vwap
        volume = self.volume
        close_delta2 = Delta(close,2)
        close_delta2_decay = DecayLinear(close_delta2,8)
        r1 = Rank(close_delta2_decay)
        price_temp = pd.concat([vwap,Open],axis = 1,join = 'inner')
        price = pd.DataFrame(price_temp['Vwap'] * 0.3 + price_temp['Open'] * 0.7)
        volume_mean = Mean(volume,180)
        volume_mean_sum = Sum(volume_mean,37)
        rank = pd.concat([price,volume_mean_sum],axis = 1,join = 'inner')
        corr = Corr(rank,14)
        corr_decay = DecayLinear(corr,12)
        r2 = Rank(corr_decay)
        r = pd.concat([r1,r2],axis = 1,join  = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r2'] - r['r1'])
        alpha.columns = ['alpha39']
        return alpha
    
    @timer
    def alpha40(self):
        close = self.close
        volume = self.volume
        close_delay = Delay(close,1)
        data = pd.concat([close,volume,close_delay],axis = 1, join = 'inner')
        data.columns  = ['close','volume','close_delay']
        data['temp1'] = data['volume']
        data['temp2'] = data['volume']
        data['temp1'][data['close'] <= data['close_delay']] = 0
        data['temp2'][data['close'] > data['close_delay']] = 0
        s1 = Sum(pd.DataFrame(data['temp1']),26)
        s2 = Sum(pd.DataFrame(data['temp2']),26)
        s = pd.concat([s1,s2], axis = 1, join = 'inner')
        s.columns = ['s1','s2']
        alpha = pd.DataFrame(s['s1']/s['s2'] * 100)
        alpha.columns = ['alpha40']
        return alpha
         
    @timer    
    def alpha41(self):
        vwap = self.vwap
        vwap_delta = Delta(vwap,3)
        vwap_delta_max = TsMax(vwap_delta,5)
        alpha = -1 * Rank(vwap_delta_max)
        alpha.columns = ['alpha41']
        return alpha
    
    @timer    
    def alpha42(self):
        high = self.high
        volume = self.volume
        high_std = STD(high,10)
        r1 = Rank(high_std)
        data = pd.concat([high,volume],axis = 1,join  = 'inner')
        corr = Corr(data,10)
        r = pd.concat([r1,corr],axis = 1,join = 'inner')
        r.columns = ['r1','corr']
        alpha = pd.DataFrame(-1 * r['r1'] * r['corr'])
        alpha.columns = ['alpha42']
        return alpha
    
    @timer    
    def alpha43(self):
        close = self.close
        volume = self.volume
        close_delay = Delay(close,1)
        close_delay.columns = ['close_delay']
        data = pd.concat([close,close_delay,volume],axis = 1,join = 'inner')
        data['sign'] = 1
        data['sign'][data['Close'] < data['close_delay']] = -1
        temp = pd.DataFrame(data['Vol'] * data['sign'])
        alpha = Sum(temp,6)
        alpha.columns = ['alpha43']
        return alpha
    
    @timer    
    def alpha44(self):
        volume = self.volume
        vwap = self.vwap
        low = self.low
        volume_mean = Mean(volume,10)
        rank = pd.concat([low,volume_mean],axis = 1,join  = 'inner')
        corr = Corr(rank,7)
        corr_decay =  DecayLinear(corr,6)
        r1 = TsRank(corr_decay,4)
        vwap_delta = Delta(vwap,3)
        vwap_delta_decay = DecayLinear(vwap_delta,10)
        r2 = TsRank(vwap_delta_decay,15)
        r = pd.concat([r1,r2],axis = 1,join  = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1'] + r['r2'])
        alpha.columns = ['alpha44']
        return alpha
    
    @timer
    def alpha45(self):
        volume = self.volume
        vwap = self.vwap
        close = self.close   
        Open = self.open
        price = pd.concat([close,Open],axis = 1,join  = 'inner')
        price['price'] = price['Close'] * 0.6 + price['Open'] * 0.4 
        price_delta = Delta(pd.DataFrame(price['price']),1)
        r1 = Rank(price_delta)
        volume_mean = Mean(volume,150)
        data = pd.concat([vwap,volume_mean],axis = 1,join  = 'inner')
        corr = Corr(data,15)
        r2 = Rank(corr)
        r = pd.concat([r1,r2],axis = 1,join  = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1'] + r['r2'])
        alpha.columns = ['alpha45']
        return alpha
    
    @timer
    def alpha46(self):
        close = self.close
        close_mean3 = Mean(close,3)
        close_mean6 = Mean(close,6)
        close_mean12 = Mean(close,12)
        close_mean24 = Mean(close,24)
        data =  pd.concat([close,close_mean3,close_mean6,close_mean12,close_mean24],axis = 1,join  = 'inner')
        data.columns = ['c','c3','c6','c12','c24']
        alpha  = (data['c3'] + data['c6'] + data['c12'] + data['c24'])/(4 * data['c'])
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha46']
        return alpha
    
    @timer
    def alpha47(self):  
        close = self.close
        low = self.low
        high = self.high
        high_max = TsMax(high,6)
        low_min = TsMin(low,6)
        data = pd.concat([high_max,low_min,close],axis = 1,join = 'inner')
        data.columns = ['high_max','low_min','close']
        temp = pd.DataFrame((data['high_max'] - data['close'])/(data['high_max'] - \
                            data['low_min']) * 100)
        alpha = SMA(temp,9,1)
        alpha.columns = ['alpha47']
        return alpha
    
    @timer
    def alpha48(self):
        close = self.close
        volume = self.volume
        temp1 = Delta(close,1)
        temp1_delay1 = Delay(temp1,1)
        temp1_delay2 = Delay(temp1,2)
        data = pd.concat([temp1,temp1_delay1,temp1_delay2],axis = 1,join = 'inner')
        data.columns = ['temp1','temp1_delay1','temp1_delay2']
        temp2 = pd.DataFrame(np.sign(data['temp1']) + np.sign(data['temp1_delay1']) \
                             + np.sign(data['temp1_delay2']))
        volume_sum5 = Sum(volume,5)
        volume_sum20 = Sum(volume,20)
        data_temp = pd.concat([temp2,volume_sum5,volume_sum20],axis = 1,join = 'inner')
        data_temp.columns = ['temp2','volume_sum5','volume_sum20']
        temp3 = pd.DataFrame(data_temp['temp2'] * data_temp['volume_sum5']/\
                             data_temp['volume_sum20'])
        alpha = -1 * Rank(temp3)
        alpha.columns = ['alpha48']
        return alpha
    
    @timer    
    def alpha49(self):
        low = self.low
        high = self.high
        data = pd.concat([low,high],axis = 1,join  = 'inner')
        price_sum = pd.DataFrame(data['Low'] + data['High'])
        price_sum_delay = Delay(price_sum,1)
        price = pd.concat([price_sum,price_sum_delay],axis = 1,join = 'inner')
        price.columns = ['sum','sum_delay']
        price['temp'] = 0
        price['temp'][price['sum'] < price['sum_delay']] = 1
        alpha = Sum(pd.DataFrame(price['temp']),12)
        alpha.columns = ['alpha49']
        return alpha
    
    @timer    
    def alpha50(self):
        low = self.low
        high = self.high
        data = pd.concat([low,high],axis = 1,join  = 'inner')
        price_sum = pd.DataFrame(data['Low'] + data['High'])
        price_sum_delay = Delay(price_sum,1)
        price = pd.concat([price_sum,price_sum_delay],axis = 1,join = 'inner')
        price.columns = ['sum','sum_delay']
        price['temp'] = 1
        price['temp'][price['sum'] <= price['sum_delay']] = -1
        alpha = Sum(pd.DataFrame(price['temp']),12)
        alpha.columns = ['alpha50']
        return alpha   
    
    @timer    
    def alpha51(self):
        low = self.low
        high = self.high
        data = pd.concat([low,high],axis = 1,join  = 'inner')
        price_sum = pd.DataFrame(data['Low'] + data['High'])
        price_sum_delay = Delay(price_sum,1)
        price = pd.concat([price_sum,price_sum_delay],axis = 1,join = 'inner')
        price.columns = ['sum','sum_delay']
        price['temp'] = 1
        price['temp'][price['sum'] <= price['sum_delay']] = 0
        alpha = Sum(pd.DataFrame(price['temp']),12)
        alpha.columns = ['alpha51']
        return alpha    
    
    @timer    
    def alpha52(self):
        low = self.low
        high = self.high
        close = self.close
        data = pd.concat([low,high,close],axis = 1,join = 'inner')
        data['sum_delay'] = Delay(pd.DataFrame((data['High'] + data['Low'] + data['Close'])/3),1)
        temp1 = pd.DataFrame(data['High'] - data['sum_delay'])
        temp1.columns = ['high_diff']
        temp2 = pd.DataFrame(data['sum_delay'] - data['Low'])
        temp2.columns = ['low_diff']
        temp1['max'] = temp1['high_diff']
        temp1['max'][temp1['high_diff'] < 0 ] = 0
        temp2['max'] = temp2['low_diff']
        temp2['max'][temp2['low_diff'] < 0 ] = 0
        temp1_sum = Sum(pd.DataFrame(temp1['max']),26)
        temp2_sum = Sum(pd.DataFrame(temp2['max']),26)
        alpha_temp = pd.concat([temp1_sum,temp2_sum],axis = 1,join  = 'inner')
        alpha_temp.columns = ['s1','s2']
        alpha  = pd.DataFrame(alpha_temp['s1']/alpha_temp['s2'] * 100)
        alpha.columns = ['alpha52']
        return alpha
    
    @timer
    def alpha53(self):
        close = self.close
        close_delay = Delay(close,1)
        count = Count(0,close,close_delay,12)
        alpha = count/12.0 * 100
        alpha.columns = ['alpha53']
        return alpha
    
    @timer
    def alpha54(self):
        Open = self.open
        close = self.close
        data = pd.concat([Open,close], axis = 1, join = 'inner')
        data.columns = ['close','open']
        temp = pd.DataFrame(data['close'] - data['open'])
        temp_abs = pd.DataFrame(np.abs(temp))
        df = pd.concat([temp,temp_abs], axis = 1, join= 'inner')
        df.columns = ['temp','abs']
        std = STD(pd.DataFrame(df['temp'] + df['abs']),10)
        corr = Corr(data,10)
        data1 = pd.concat([corr,std],axis = 1, join = 'inner')
        data1.columns = ['corr','std']
        alpha = Rank(pd.DataFrame(data1['corr'] + data1['std'])) * -1
        alpha.columns = ['alpha54']
        return alpha
    
    @timer    
    def alpha55(self):
        Open = self.open
        close = self.close
        low = self.low
        high = self.high
        close_delay = Delay(close,1)
        open_delay = Delay(Open,1)
        low_delay = Delay(low,1)
        data = pd.concat([Open,close,low,high,close_delay,open_delay,low_delay], axis =1 ,join = 'inner')
        data.columns= ['open','close','low','high','close_delay','open_delay','low_delay']
        temp1 = pd.DataFrame((data['close'] - data['close_delay'] + (data['close'] - data['open'])/2\
                + data['close_delay'] - data['open_delay'])/ np.abs(data['high'] - data['close_delay']))
        temp2 = pd.DataFrame(np.abs(data['high'] - data['close_delay']) + np.abs(data['low'] - data['close_delay'])/2 \
                + np.abs(data['close_delay'] - data['open_delay'])/4)
        temp3 = pd.DataFrame(np.abs(data['low'] - data['close_delay']) + np.abs(data['high'] - data['close_delay'])/2 \
                + np.abs(data['close_delay'] - data['open_delay'])/4)
        
        abs1 = pd.DataFrame(np.abs(data['high'] - data['close_delay']))
        abs2 = pd.DataFrame(np.abs(data['low'] - data['close_delay']))
        abs3 = pd.DataFrame(np.abs(data['high'] - data['low_delay']))
        data1 = pd.concat([abs1,abs2,abs3], axis = 1, join  = 'inner')
        data1.columns = ['abs1','abs2','abs3']
        
        data_temp = pd.concat([abs1,abs2],axis = 1, join  = 'inner')
        data_temp_max = pd.DataFrame(np.max(data_temp,axis = 1))
        data_temp_max.columns = ['max']
        data_temp1 = pd.concat([data,data_temp_max], axis = 1, join  = 'inner')
        temp4 = pd.DataFrame((np.abs(data_temp1['high'] - data_temp1['low_delay']) + \
            np.abs(data_temp1['close_delay'] - data_temp1['open_delay'])) *\
                 data_temp1['max'])
        data1['judge1'] = 0
        data1['judge2'] = 0
        data1['judge3'] = 0
        data1['judge4'] = 0
        data1['judge1'][data1['abs1'] > data1['abs2']] = 1
        data1['judge2'][data1['abs1'] > data1['abs3']] = 1
        data1['judge3'][data1['abs2'] > data1['abs3']] = 1
        data1['judge3'][data1['abs3'] > data1['abs1']] = 1
        judge_1 = pd.DataFrame(data1['judge1'] * data1['judge2'])
        judge_2 = pd.DataFrame(data1['judge3'] * data1['judge4'])
        data2 = pd.concat([temp1,temp2,temp3,temp4,judge_1,judge_2], axis = 1, join  = 'inner')
        data2.columns = ['t1','t2','t3','t4','j1','j2']
        data2['j3']  = 1
        data2['j4'] = data2['j3'] - data2['j1'] - data2['j2']
        data2['t5'] = data2['t2'] * data2['j1'] + data2['t3'] * data2['j2'] + \
                data2['t4'] * data2['j4']
        tep = pd.DataFrame(16 * data2['t5']/data2['t1'])
        alpha = Sum(tep,20)
        alpha.columns = ['alpha55']
        return alpha
    @timer    
    def alpha56(self):
        low = self.low
        high = self.high
        volume = self.volume
        Open = self.open
        open_min = TsMin(Open,12)
        data1 = pd.concat([Open,open_min], axis = 1, join  = 'inner')
        data1.columns  = ['open','open_min']
        r1 = Rank(pd.DataFrame(data1['open'] - data1['open_min']))
        volume_mean = Mean(volume,40)
        volume_mean_sum= Sum(volume_mean,19)
        data2 = pd.concat([high,low],axis = 1, join  = 'inner')
        temp = pd.DataFrame((data2['High'] + data2['Low'])/2)
        rank = pd.concat([temp,volume_mean_sum],axis = 1 , join = 'inner')
        rank.columns = ['temp','volume_mean_sum']
        corr = Corr(rank,13)
        r2 = Rank(corr)
        r = pd.concat([r1,r2],axis = 1, join = 'inner')
        r.columns = ['r1','r2']
        r['alpha'] = 0
        r['alpha'][r['r1'] >= r['r2']] = 1
        alpha = pd.DataFrame(r['alpha'])    
        alpha.columns = ['alpha56']
        return alpha
    
    @timer    
    def alpha57(self):
        low = self.low
        high = self.high
        close = self.close
        low_min = TsMin(low,9)
        high_max = TsMax(high,9)
        data = pd.concat([close,low_min,high_max],axis = 1,join = 'inner')
        data.columns = ['close','low_min','high_max']
        temp = pd.DataFrame((data['close'] - data['low_min'])/(data['high_max'] \
                            - data['low_min']) * 100)
        alpha = SMA(temp,3,1)
        alpha.columns = ['alpha57']
        return alpha
    
    @timer
    def alpha58(self):    
        close = self.close
        close_delay = Delay(close,1)
        count = Count(0,close,close_delay,20)
        alpha = count/20.0 * 100
        alpha.columns = ['alpha58']
        return alpha   
    
    @timer
    def alpha59(self):
        low = self.low
        high = self.high
        close = self.close
        close_delay = Delay(close,1)
        max_temp = pd.concat([high,close_delay],axis = 1,join = 'inner')
        min_temp = pd.concat([low,close_delay],axis = 1,join  = 'inner')
        
        max_temp1 = pd.DataFrame(np.max(max_temp,axis = 1))
        min_temp1 = pd.DataFrame(np.min(min_temp,axis = 1))
        data = pd.concat([close,close_delay,max_temp1,min_temp1],axis = 1,join = 'inner')
        data.columns = ['close','close_delay','max','min']
        data['max'][data['close'] > data['close_delay']] = 0
        data['min'][data['close'] <= data['close_delay']] = 0
        alpha = pd.DataFrame(data['max'] + data['min'])
        alpha.columns = ['alpha59']
        return alpha
    
    @timer
    def alpha60(self):
        low = self.low
        high = self.high
        close = self.close
        volume = self.volume
        data = pd.concat([low,high,close,volume],axis = 1,join = 'inner')
        temp = pd.DataFrame((2 * data['Close'] - data['Low'] - data['High'])/(data['Low'] + \
               data['High']) * data['Vol'])
        alpha = Sum(temp,20)
        alpha.columns = ['alpha60']
        return alpha
    
    @timer    
    def alpha61(self):
        low = self.low
        volume = self.volume
        vwap = self.vwap
        vwap_delta = Delta(vwap,1)
        vwap_delta_decay = DecayLinear(vwap_delta,12)
        r1 = Rank(vwap_delta_decay)
        volume_mean = Mean(volume,80)
        data = pd.concat([low,volume_mean],axis = 1,join = 'inner')
        corr = Corr(data,8)
        corr_decay = DecayLinear(corr,17)
        r2 = Rank(corr_decay)
        r = pd.concat([r1,r2],axis = 1,join = 'inner')
        alpha = pd.DataFrame(np.max(r,axis = 1) * -1)
        alpha.columns = ['alpha61']
        return alpha
    
    @timer    
    def alpha62(self):
        high = self.high
        volume = self.volume
        volume_r = Rank(volume)
        data = pd.concat([high,volume_r],axis = 1,join = 'inner')
        alpha = -1 * Corr(data,5)
        alpha.columns = ['alpha62']
        return alpha
    
    @timer
    def alpha63(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay],axis = 1,join = 'inner')
        data.columns = ['close','close_delay']
        data['max'] = data['close'] - data['close_delay']
        data['max'][data['max'] < 0] = 0
        data['abs'] = np.abs(data['close'] - data['close_delay'])
        sma1 = SMA(pd.DataFrame(data['max']),6,1)
        sma2 = SMA(pd.DataFrame(data['abs']),6,1)
        sma = pd.concat([sma1,sma2],axis = 1,join = 'inner')
        sma.columns  = ['sma1','sma2']
        alpha = pd.DataFrame(sma['sma1']/sma['sma2'] * 100)
        alpha.columns = ['alpha63']
        return alpha
    
    @timer
    def alpha64(self):
        vwap = self.vwap
        volume = self.volume
        close = self.close
        vwap_r = Rank(vwap)
        volume_r = Rank(volume)
        data1 = pd.concat([vwap_r,volume_r],axis = 1,join = 'inner')
        corr1 = Corr(data1,4)
        corr1_decay = DecayLinear(corr1,4)
        r1 = Rank(corr1_decay)
        close_mean = Mean(close,60)
        close_r = Rank(close)
        close_mean_r = Rank(close_mean)
        data2 = pd.concat([close_r,close_mean_r],axis = 1,join = 'inner')
        corr2 = Corr(data2,4)
        corr2_max = TsMax(corr2,13)
        corr2_max_decay = DecayLinear(corr2_max,14)
        r2 = Rank(corr2_max_decay)
        r = pd.concat([r1,r2],axis = 1,join = 'inner')
        alpha = pd.DataFrame(np.max(r,axis = 1) *-1)
        alpha.columns = ['alpha64']
        return alpha
    
    @timer
    def alpha65(self):
        close = self.close
        close_mean = Mean(close,6)
        data = pd.concat([close,close_mean],axis = 1, join = 'inner')
        data.columns = ['close','close_mean']
        alpha = pd.DataFrame(data['close_mean']/data['close'])
        alpha.columns = ['alpha65']
        return alpha
    
    @timer    
    def alpha66(self):
        close = self.close
        close_mean = Mean(close,6)
        data = pd.concat([close,close_mean],axis = 1, join = 'inner')
        data.columns = ['close','close_mean']
        alpha = (data['close'] - data['close_mean'])/data['close_mean'] * 100
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha66']
        return alpha
    
    @timer    
    def alpha67(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay],axis = 1,join = 'inner')
        data.columns = ['close','close_delay']
        data['max'] = data['close'] - data['close_delay']
        data['max'][data['max'] < 0] = 0
        data['abs'] = np.abs(data['close'] - data['close_delay'])
        sma1 = SMA(pd.DataFrame(data['max']),24,1)
        sma2 = SMA(pd.DataFrame(data['abs']),24,1)
        sma = pd.concat([sma1,sma2],axis = 1,join = 'inner')
        sma.columns  = ['sma1','sma2']
        alpha = pd.DataFrame(sma['sma1']/sma['sma2'] * 100)
        alpha.columns = ['alpha67']
        return alpha 
    
    @timer
    def alpha68(self):
        high = self.high
        volume = self.volume
        low = self.low
        data = pd.concat([high,low,volume],axis = 1,join = 'inner')
        data['sum']= (data['High'] + data['Low'])/2
        data['sum_delta'] = Delta(pd.DataFrame(data['sum']),1)
        temp = data['sum_delta'] * (data['High'] - data['Low'])/data['Vol']
        alpha = SMA(pd.DataFrame(temp),15,2)
        alpha.columns = ['alpha68']
        return alpha
    
    @timer
    def alpha69(self):
        high = self.high
        low = self.low
        Open = self.open
        dtm = DTM(Open,high)
        dbm = DBM(Open,low)
        dtm_sum = Sum(dtm,20)
        dbm_sum = Sum(dbm,20)
        data = pd.concat([dtm_sum,dbm_sum],axis = 1, join = 'inner')
        data.columns = ['dtm','dbm']
        data['temp1'] = (data['dtm'] - data['dbm'])/data['dtm']
        data['temp2'] = (data['dtm'] - data['dbm'])/data['dbm']
        data['temp1'][data['dtm'] <= data['dbm']] = 0
        data['temp2'][data['dtm'] >= data['dbm']] = 0
        alpha = pd.DataFrame(data['temp1'] + data['temp2'])
        alpha.columns = ['alpha69']
        return alpha
        
    @timer    
    def alpha70(self):
        amount = self.amt
        alpha= STD(amount,6)
        alpha.columns = ['alpha70']
        return alpha
    
    @timer
    def alpha71(self):
        close = self.close
        close_mean = Mean(close,24)
        data = pd.concat([close,close_mean],axis = 1, join = 'inner')
        data.columns = ['close','close_mean']
        alpha = (data['close'] - data['close_mean'])/data['close_mean'] * 100
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha71']
        return alpha    
    @timer    
    def alpha72(self):
        low = self.low
        high = self.high
        close = self.close
        low_min = TsMin(low,6)
        high_max = TsMax(high,6)
        data = pd.concat([close,low_min,high_max],axis = 1,join = 'inner')
        data.columns = ['close','low_min','high_max']    
        temp = (data['high_max'] - data['close'])/(data['high_max'] - data['low_min']) * 100
        alpha = SMA(pd.DataFrame(temp),15,1)
        alpha.columns = ['alpha72']
        return alpha
    
    @timer
    def alpha73(self):
        vwap = self.vwap
        volume = self.volume
        close = self.close
        data1 = pd.concat([close,volume],axis = 1,join  = 'inner')
        corr1 = Corr(data1,10)
        corr1_decay = DecayLinear(DecayLinear(corr1,16),4)
        r1 = TsRank(corr1_decay,5)
        volume_mean = Mean(volume,30)
        data2 = pd.concat([vwap,volume_mean],axis = 1,join = 'inner')
        corr2 = Corr(data2,4)
        corr2_decay = DecayLinear(corr2,3)
        r2 = Rank(corr2_decay)
        r = pd.concat([r1,r2],axis = 1,join ='inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r2'] - r['r1'])
        alpha.columns= ['alpha73']
        return alpha
    
    @timer
    def alpha74(self):
        vwap = self.vwap
        volume = self.volume
        low = self.low
        volume_mean = Mean(volume,40)
        volume_mean_sum = Sum(volume_mean,20)
        data1 = pd.concat([low,vwap],axis = 1,join = 'inner')
        data_sum = Sum(pd.DataFrame(data1['Low'] * 0.35 + data1['Vwap'] * 0.65),20)
        data = pd.concat([volume_mean_sum,data_sum],axis = 1,join = 'inner')
        corr = Corr(data,7)
        r1 = Rank(corr)
        vwap_r = Rank(vwap)
        volume_r = Rank(volume)
        data_temp = pd.concat([vwap_r,volume_r],axis = 1,join = 'inner')
        corr2 = Corr(data_temp,6)
        r2 = Rank(corr2)
        r = pd.concat([r1,r2],axis = 1,join = 'inner')
        r.columns = ['r1','r2']
        alpha  = pd.DataFrame(r['r1'] + r['r2'])
        alpha.columns = ['alpha74']
        return alpha
    
    @timer    
    def alpha75(self):
        close = self.close
        Open = self.open
        close_index = self.close_index
        open_index = self.open_index
        data1 = pd.concat([close,Open], axis = 1, join = 'inner')
        data1.columns = ['close','open']
        data1['temp'] = 1
        data1['temp'][data1['close'] <= data1['open']] = 0
        data2 = pd.concat([close_index,open_index], axis = 1, join = 'inner')
        data2.columns = ['close','open']
        data2['tep'] = 1
        data2['tep'][data2['close'] > data2['open']] = 0
        temp = data1['temp'].unstack()    
        tep = data2['tep'].unstack()
        tep1 = repmat(tep,1,np.size(temp,1))
        data3 = temp * tep1
        temp_result = data3.rolling(50,min_periods = 50).sum()
        tep_result = tep.rolling(50,min_periods = 50).sum()
        tep2_result = np.matlib.repmat(tep_result,1,np.size(temp,1))
        result = temp_result/tep2_result
        alpha = pd.DataFrame(result.stack())
        alpha.columns = ['alpha75']
        return alpha     
        
    @timer    
    def alpha76(self):
        volume = self.volume
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([volume,close,close_delay],axis = 1,join = 'inner')
        data.columns = ['volume','close','close_delay']
        temp = pd.DataFrame(np.abs((data['close']/data['close_delay'] -1 )/data['volume']))
        temp_std = STD(temp,20)
        temp_mean = Mean(temp,20)
        data_temp = pd.concat([temp_std,temp_mean],axis = 1,join = 'inner')
        data_temp.columns = ['std','mean']
        alpha = pd.DataFrame(data_temp['std']/data_temp['mean'])
        alpha.columns = ['alpha76']
        return alpha
    
    @timer
    def alpha77(self):
        vwap = self.vwap
        volume = self.volume
        low = self.low
        high = self.high
        data = pd.concat([high,low,vwap],axis = 1,join  = 'inner')
        temp = pd.DataFrame((data['High'] + data['Low'])/2 - data['Vwap'])
        temp_decay = DecayLinear(temp,20)
        r1 = Rank(temp_decay)
        temp1 = pd.DataFrame((data['High'] + data['Low'])/2)
        volume_mean = Mean(volume,40)
        data2 = pd.concat([temp1,volume_mean],axis = 1,join = 'inner')
        corr = Corr(data2,3)
        corr_decay = DecayLinear(corr,6)
        r2 = Rank(corr_decay)
        r = pd.concat([r1,r2],axis = 1,join = 'inner')
        alpha = pd.DataFrame(np.min(r,axis = 1))
        alpha.columns = ['alpha77']
        return alpha
    
    @timer
    def alpha78(self):
        low = self.low
        high = self.high
        close = self.close
        data = pd.concat([low,high,close],axis = 1,join = 'inner')
        temp = pd.DataFrame((data['Low'] + data['High'] + data['Close'])/3)
        temp.columns = ['temp']
        temp_mean = Mean(temp,12)
        temp_mean.columns = ['temp_mean']
        temp2 = pd.concat([temp,temp_mean],axis = 1,join = 'inner')
        tmp = pd.DataFrame(temp2['temp'] - temp2['temp_mean'])
        data1 = pd.concat([close,temp_mean],axis = 1,join = 'inner')
        temp_abs = pd.DataFrame(np.abs(data1['Close'] - data1['temp_mean']))
        temp_abs_mean = Mean(temp_abs,12)
        df = pd.concat([tmp,temp_abs_mean],axis = 1,join = 'inner')
        df.columns = ['df1','df2']
        alpha = pd.DataFrame(df['df1']/(df['df2'] * 0.015))
        alpha.columns = ['alpha78']
        return alpha
        
    @timer    
    def alpha79(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay],axis = 1,join = 'inner')
        data.columns = ['close','close_delay']
        data['max'] = data['close'] - data['close_delay']
        data['max'][data['max'] < 0] = 0
        data['abs'] = np.abs(data['close'] - data['close_delay'])
        sma1 = SMA(pd.DataFrame(data['max']),12,1)
        sma2 = SMA(pd.DataFrame(data['abs']),12,1)
        sma = pd.concat([sma1,sma2],axis = 1,join = 'inner')
        sma.columns  = ['sma1','sma2']
        alpha = pd.DataFrame(sma['sma1']/sma['sma2'] * 100)
        alpha.columns = ['alpha79']
        return alpha     
        
    @timer 
    def alpha80(self):
        volume = self.volume
        volume_delay = Delay(volume,5)
        volume_delay.columns = ['volume_delay']
        data = pd.concat([volume,volume_delay],axis = 1,join  = 'inner')
        alpha = (data['Vol'] - data['volume_delay'])/data['volume_delay']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha80']
        return alpha
    
    @timer
    def alpha81(self):
        volume = self.volume
        alpha = SMA(volume,21,2)
        alpha.columns = ['alpha81']
        return alpha
    
    @timer
    def alpha82(self):
        low = self.low
        high = self.high
        close = self.close
        low_min = TsMin(low,6)
        high_max = TsMax(high,6)
        data = pd.concat([close,low_min,high_max],axis = 1,join = 'inner')
        data.columns = ['close','low_min','high_max']    
        temp = (data['high_max'] - data['close'])/(data['high_max'] - data['low_min']) * 100
        alpha = SMA(pd.DataFrame(temp),20,1)
        alpha.columns = ['alpha82']
        return alpha  
    
    @timer
    def alpha83(self):
        high = self.high
        volume = self.volume
        high_r = Rank(high)
        volume_r = Rank(volume)
        data = pd.concat([high_r,volume_r],axis = 1,join = 'inner')
        corr = Corr(data,5)
        alpha = -1 * Rank(corr)
        alpha.columns = ['alpha83']
        return alpha
    
    @timer
    def alpha84(self):
        close = self.close
        volume = self.volume
        close_delay = Delay(close,1)
        close_delay.columns = ['close_delay']
        data = pd.concat([close,close_delay,volume],axis = 1,join = 'inner')
        data['sign'] = 1
        data['sign'][data['Close'] < data['close_delay']] = -1
        data['sign'][data['Close'] == data['close_delay']] = 0
        temp = pd.DataFrame(data['Vol'] * data['sign'])
        alpha = Sum(temp,20)
        alpha.columns = ['alpha84']
        return alpha  
    
    @timer
    def alpha85(self):
        close = self.close
        volume = self.volume
        volume_mean = Mean(volume,20)
        close_delta = Delta(close,7)
        data1 = pd.concat([volume,volume_mean],axis = 1,join = 'inner')
        data1.columns = ['volume','volume_mean']
        temp1 = pd.DataFrame(data1['volume']/data1['volume_mean'])
        r1 = TsRank(temp1,20)
        r2 = TsRank(-1 * close_delta,8)
        r = pd.concat([r1,r2],axis = 1,join = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1'] * r['r2'])
        alpha.columns = ['alpha85']
        return alpha
    
    @timer    
    def alpha86(self):
        close = self.close
        close_delay20 = Delay(close,20)
        close_delay10 = Delay(close,20)
        data = pd.concat([close,close_delay20,close_delay10],axis = 1,join = 'inner')
        data.columns = ['close','close_delay20','close_delay10']
        temp = pd.DataFrame((data['close_delay20'] - data['close_delay10'])/10 - \
                    (data['close_delay10'] - data['close'])/10)
        close_delta = Delta(close,1) * -1
        data_temp = pd.concat([close_delta,temp],axis = 1,join = 'inner')
        data_temp.columns = ['close_delta','temp']
        data_temp['close_delta'][data_temp['temp'] > 0.25]= -1
        data_temp['close_delta'][data_temp['temp'] < 0]= 1 
        alpha  = pd.DataFrame(data_temp['close_delta'])
        alpha.columns = ['alpha86']
        return alpha
    
    @timer
    def alpha87(self):
        vwap =  self.vwap
        high = self.high    
        low = self.low  
        Open = self.open
        vwap_delta = Delta(vwap,4)
        vwap_delta_decay = DecayLinear(vwap_delta,7)
        r1 = Rank(vwap_delta_decay)
        data = pd.concat([low,high,vwap,Open], axis = 1, join  = 'inner')
        temp = pd.DataFrame((data['Low'] * 0.1 + data['High'] * 0.9 - data['Vwap'])/\
                (data['Open'] - 0.5 * (data['Low'] + data['High'])))
        temp_decay = DecayLinear(temp,11)
        r2 = TsRank(temp_decay,7)
        r = pd.concat([r1,r2], axis = 1,join  = 'inner')
        r.columns  = ['r1','r2']
        alpha = pd.DataFrame(-1 * (r['r1'] + r['r2']))
        alpha.columns = ['alpha87']
        return alpha
        
    @timer    
    def alpha88(self):
        close = self.close
        close_delay = Delay(close,20)
        data  = pd.concat([close,close_delay],axis = 1,join  = 'inner')
        data.columns = ['close','close_delta']
        alpha = (data['close'] - data['close_delta'])/data['close_delta'] * 100
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha88']
        return alpha
    
    @timer    
    def alpha89(self):
        close = self.close
        sma1 = SMA(close,13,2)
        sma2 = SMA(close,27,2)
        sma = pd.concat([sma1,sma2],axis = 1, join  = 'inner')
        sma.columns = ['sma1','sma2']
        temp = pd.DataFrame(sma['sma1'] - sma['sma2'])
        sma3 = SMA(temp,10,2)
        data = pd.concat([temp,sma3],axis = 1, join  = 'inner')
        data.columns  = ['temp','sma']
        alpha =  pd.DataFrame(2 *(data['temp'] - data['sma']))
        alpha.columns = ['alpha89']
        return alpha
    
    @timer     
    def alpha90(self):
        volume = self.volume
        vwap =  self.vwap
        r1 = Rank(volume)
        r2 = Rank(vwap)
        rank = pd.concat([r1,r2], axis = 1, join = 'inner')
        corr = Corr(rank,5)
        alpha = -1 * Rank(corr)
        alpha.columns = ['alpha90']
        return alpha
    
    @timer
    def alpha91(self):
        close = self.close
        volume = self.volume
        low = self.low
        close_max = TsMax(close,5)
        data1 = pd.concat([close,close_max], axis = 1,join  = 'inner')
        data1.columns = ['close','close_max']
        r1 = Rank(pd.DataFrame(data1['close'] - data1['close_max']))
        volume_mean = Mean(volume,40)
        data2 = pd.concat([volume_mean,low], axis = 1, join  = 'inner')
        corr = Corr(data2,5)
        r2 = Rank(corr)
        r = pd.concat([r1,r2],axis = 1, join = 'inner')
        r.columns  = ['r1','r2']
        alpha = pd.DataFrame(r['r1'] * r['r2'] * -1)
        alpha.columns = ['alpha91']
        return alpha
    
    @timer    
    def alpha92(self):
        volume = self.volume
        vwap =  self.vwap 
        close = self.close
        data = pd.concat([close,vwap],axis = 1, join  = 'inner')
        data['price'] = data['Close'] * 0.35 + data['Vwap'] * 0.65
        price_delta = Delta(pd.DataFrame(data['price']),2)
        price_delta_decay = DecayLinear(price_delta,3)
        r1 = Rank(price_delta_decay)
        volume_mean = Mean(volume,180)
        rank = pd.concat([volume_mean,close],axis = 1,join  = 'inner')
        corr = Corr(rank,13)
        temp = pd.DataFrame(np.abs(corr))
        temp_decay = DecayLinear(temp,5)
        r2 = TsRank(temp_decay,15)
        r = pd.concat([r1,r2],axis = 1, join  = 'inner')
        alpha = pd.DataFrame(-1 * np.max(r, axis = 1))
        alpha.columns = ['alpha92']
        return alpha
                    
    @timer
    def alpha93(self):
        low = self.low
        Open = self.open
        open_delay = Delay(Open,1)
        data = pd.concat([low,Open,open_delay],axis = 1,join = 'inner')
        data.columns = ['low','open','open_delay']
        temp1 = pd.DataFrame(data['open'] -  data['low'])
        temp2 = pd.DataFrame(data['open'] - data['open_delay'])
        data_temp = pd.concat([temp1,temp2],axis = 1 ,join = 'inner')
        temp_max = pd.DataFrame(np.max(data_temp,axis = 1))
        temp_max.columns = ['max']
        data2 = pd.concat([data,temp_max],axis = 1,join  = 'inner')
        data2['temp'] = data2['max']
        data2['temp'][data2['open'] >= data2['open_delay']] = 0
        alpha = Sum(pd.DataFrame(data2['temp']),20)
        alpha.columns = ['alpha93']
        return alpha
    
    @timer
    def alpha94(self):
        close = self.close
        volume = self.volume
        close_delay = Delay(close,1)
        close_delay.columns = ['close_delay']
        data = pd.concat([close,close_delay,volume],axis = 1,join = 'inner')
        data['sign'] = 1
        data['sign'][data['Close'] < data['close_delay']] = -1
        data['sign'][data['Close'] == data['close_delay']] = 0
        temp = pd.DataFrame(data['Vol'] * data['sign'])
        alpha = Sum(temp,30)
        alpha.columns = ['alpha94']
        return alpha     
    
    @timer
    def alpha95(self):
        amt = self.amt
        alpha = STD(amt,20)
        alpha.columns = ['alpha95']
        return alpha
    
    @timer
    def alpha96(self):
        low = self.low
        high = self.high
        close = self.close
        low_min = TsMin(low,9)
        high_max = TsMax(high,9)
        data = pd.concat([close,low_min,high_max],axis = 1,join = 'inner')
        data.columns = ['close','low_min','high_max']    
        temp = ( data['close'] - data['low_min'])/(data['high_max'] - data['low_min']) * 100
        alpha_temp = SMA(pd.DataFrame(temp),3,1)
        alpha = SMA(alpha_temp,3,1)
        alpha.columns = ['alpha96']
        return alpha 
    
    @timer    
    def alpha97(self):
        volume = self.volume
        alpha = STD(volume,10)
        alpha.columns = ['alpha97']
        return alpha
    
    @timer
    def alpha98(self):
        close = self.close
        close_mean = Mean(close,100)
        close_mean_delta = Delta(close_mean,100)
        close_delay = Delay(close,100)
        data = pd.concat([close_mean_delta,close_delay],axis = 1,join = 'inner')
        data.columns = ['delta','delay']
        temp = pd.DataFrame(data['delta']/ data['delay'])
        close_delta = Delta(close,3)
        close_min = TsMin(close,100)
        data_temp = pd.concat([close,close_delta,close_min,temp],axis = 1,join = 'inner')
        data_temp.columns = ['close','close_delta','close_min','temp']
        data_temp['diff'] = (data_temp['close'] - data_temp['close_min']) * -1
        data_temp['diff'][data_temp['temp'] < 0.05] = 0
        data_temp['close_delta'] = data_temp['close_delta'] * -1
        data_temp['close_delta'][data_temp['temp'] >= 0.05]= 0
        alpha = pd.DataFrame(data_temp['close_delta'] + data_temp['diff'])
        alpha.columns = ['alpha98']
        return alpha
    
    @timer
    def alpha99(self):
        close = self.close
        volume = self.volume
        r1 = Rank(close)
        r2 = Rank(volume)
        r = pd.concat([r1,r2],axis = 1,join  = 'inner')
        cov = Cov(r,5)
        alpha = -1 * Rank(cov)
        alpha.columns = ['alpha99']
        return alpha
        
    @timer    
    def alpha100(self):
        volume = self.volume
        alpha = STD(volume,20)
        alpha.columns = ['alpha100']
        return alpha
    
    @timer
    def alpha101(self):
        close = self.close
        volume = self.volume
        high = self.high
        vwap =  self.vwap
        volume_mean = Mean(volume,30)
        volume_mean_sum = Sum(volume_mean,37)
        data1 = pd.concat([close,volume_mean_sum], axis = 1, join = 'inner')
        corr1 = Corr(data1,15)
        r1 = Rank(corr1)
        data2 = pd.concat([high,vwap],axis = 1, join = 'inner')
        temp = pd.DataFrame(data2['High'] * 0.1 + data2['Vwap'] * 0.9)
        temp_r = Rank(temp)
        volume_r = Rank(volume)
        data3 = pd.concat([temp_r,volume_r], axis = 1, join = 'inner')
        corr2 = Corr(data3,11)
        r2 = Rank(corr2)
        r = pd.concat([r1,r2], axis = 1, join = 'inner')
        r.columns  = ['r1','r2']
        r['alpha'] = 0
        r['alpha'][r['r1'] < r['r2']] = -1
        alpha = pd.DataFrame(r['alpha'])
        alpha.columns = ['alpha101']
        return alpha
     
    @timer    
    def alpha102(self): 
        volume = self.volume
        temp = Delta(volume,1)
        temp.columns = ['temp']
        temp['max'] = temp['temp']
        temp['max'][temp['temp'] < 0 ] = 0
        temp['abs'] = np.abs(temp['temp'])
        sma1 = SMA(pd.DataFrame(temp['max']),6,1)
        sma2 = SMA(pd.DataFrame(temp['abs']),6,1)
        sma = pd.concat([sma1,sma2], axis = 1 ,join ='inner')
        sma.columns = ['sma1','sma2']
        alpha = pd.DataFrame(sma['sma1']/ sma['sma2'] * 100)
        alpha.columns = ['alpha102']
        return alpha
    
    @timer
    def alpha103(self):
        low = self.low
        lowday = Lowday(low,20)
        alpha = (20 - lowday)/20.0 * 100
        alpha.columns = ['alpha103']
        return alpha
    
    @timer    
    def alpha104(self):
        close = self.close
        volume = self.volume
        high = self.high
        data = pd.concat([high,volume], axis = 1, join  = 'inner')
        corr = Corr(data,5)
        corr_delta = Delta(corr,5)
        close_std = STD(close,20)
        r1 =  Rank(close_std)
        temp = pd.concat([corr_delta,r1], axis = 1, join  = 'inner')
        temp.columns = ['delta','r']
        alpha = pd.DataFrame(-1 * temp['delta'] * temp['r'])
        alpha.columns = ['alpha104']
        return alpha
    
    @timer
    def alpha105(self):
        volume = self.volume
        Open = self.open
        volume_r = Rank(volume)
        open_r = Rank(Open)
        rank = pd.concat([volume_r,open_r],axis = 1, join  = 'inner')
        alpha = -1 * Corr(rank,10)
        alpha.columns = ['alpha105']
        return alpha
    
    @timer    
    def alpha106(self):
        close = self.close
        close_delay = Delay(close,20)
        data = pd.concat([close,close_delay], axis = 1, join = 'inner')
        data.columns = ['close','close_delay']
        alpha = pd.DataFrame(data['close'] -  data['close_delay'])
        alpha.columns = ['alpha106']
        return alpha
    
    @timer
    def alpha107(self):
        Open = self.open
        high = self.high
        close = self.close
        low = self.low
        high_delay = Delay(high,1)
        close_delay = Delay(close,1)
        low_delay = Delay(low,1)
        data = pd.concat([high_delay,close_delay,low_delay,Open], axis = 1, join  = 'inner')
        data.columns  = ['high_delay','close_delay','low_delay','open']
        r1 = Rank(pd.DataFrame(data['open'] - data['high_delay']))
        r2 = Rank(pd.DataFrame(data['open'] - data['close_delay']))
        r3 = Rank(pd.DataFrame(data['open'] - data['low_delay']))
        alpha = -1 * r1 * r2 * r3
        alpha.columns = ['alpha107']
        return alpha
    
    @timer    
    def alpha108(self):
        high = self.high
        volume = self.volume
        vwap =  self.vwap
        high_min = TsMin(high,2)
        data1 = pd.concat([high,high_min], axis = 1, join  = 'inner')
        data1.columns = ['high','high_min']
        r1 = Rank(pd.DataFrame(data1['high'] -  data1['high_min']))
        volume_mean = Mean(volume,120)
        rank = pd.concat([vwap,volume_mean],axis = 1, join  = 'inner')
        corr = Corr(rank,6)
        r2 = Rank(corr)
        r = pd.concat([r1,r2], axis = 1, join  = 'inner')
        r.columns  = ['r1','r2']
        alpha = r['r1'] * r['r2'] * -1
        alpha.columns = ['alpha108']
        return alpha
    
    @timer    
    def alpha109(self):
        high = self.high
        low = self.low
        data = pd.concat([high,low],axis = 1, join  = 'inner')
        temp = SMA(pd.DataFrame(data['High'] - data['Low']),10,2)
        sma = SMA(temp,10,2)
        sma_temp = pd.concat([temp,sma],axis = 1, join  = 'inner')
        sma_temp.columns  = ['temp','sma']
        alpha = pd.DataFrame(sma_temp['temp']/sma_temp['sma'])
        alpha.columns = ['alpha109']
        return alpha
    
    @timer
    def alpha110(self):
        high = self.high
        low = self.low    
        close = self.close
        close_delay = Delay(close,1)
        close_delay.columns = ['close_delay']
        data = pd.concat([high,low,close_delay], axis = 1, join  = 'inner')
        data['max1'] =  data['High'] - data['close_delay']
        data['max2'] = data['close_delay'] - data['Low']
        data['max1'][data['max1'] < 0] = 0
        data['max2'][data['max2'] < 0] = 0
        s1 = Sum(pd.DataFrame(data['max1']),20)
        s2 = Sum(pd.DataFrame(data['max2']),20)
        s = pd.concat([s1,s2], axis = 1 , join  = 'inner')
        s.columns = ['s1','s2']
        alpha = pd.DataFrame(s['s1']/s['s2'])
        alpha.columns = ['alpha110']
        return alpha
    
    @timer
    def alpha111(self):
        high = self.high
        low = self.low   
        close = self.close
        volume = self.volume
        data = pd.concat([high,low,close,volume], axis = 1, join  = 'inner')
        temp = pd.DataFrame(data['Vol'] * (2 * data['Close'] - data['Low'] - data['High'])\
                    /(data['High'] - data['Low']))
        sma1 = SMA(temp,11,2)
        sma2 = SMA(temp,4,2)
        sma = pd.concat([sma1, sma2], axis = 1, join  = 'inner')
        sma.columns = ['sma1','sma2']
        alpha = pd.DataFrame(sma['sma1'] - sma['sma2'])
        alpha.columns = ['alpha111']
        return alpha
    
    @timer
    def alpha112(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close, close_delay], axis = 1, join  = 'inner')
        data.columns  = ['close','close_delay']
        data['temp'] = 1
        data['temp'][data['close'] > data['close_delay']] =  0
        alpha = Sum(pd.DataFrame(data['temp']),12)
        alpha.columns = ['alpha112']
        return alpha
    
    @timer
    def alpha113(self):
        close = self.close
        volume = self.volume
        close_delay = Delay(close,5)
        close_delay_mean = Mean(close_delay,20)
        data1 = pd.concat([close,volume],axis = 1, join  = 'inner')
        corr = Corr(data1,2)
        r1 = Rank(close_delay_mean)
        data2 = pd.concat([r1,corr], axis = 1, join  = 'inner')
        data2.columns = ['r1','corr']
        r1 = pd.DataFrame(data2['r1'] * data2['corr'])
        close_sum5 = Sum(close,5)
        close_sum20 = Sum(close,20)
        data3 = pd.concat([close_sum5,close_sum20],axis = 1, join  = 'inner')
        corr2 = Corr(data3,2)
        r2 = Rank(corr2)
        r = pd.concat([r1,r2], axis = 1, join  = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1'] * r['r2'] * -1)
        alpha.columns = ['alpha113']
        return alpha
    @timer
    def alpha114(self):
        close = self.close
        high = self.high
        low = self.low
        volume = self.volume
        vwap = self.vwap
        close_mean = Mean(close,5)
        data = pd.concat([high,low,close_mean], axis = 1, join = 'inner')
        data.columns = ['high','low','close_mean']
        temp = pd.DataFrame(data['high'] - data['low'] / data['close_mean'])
        temp_delay = Delay(temp,2)
        r1 = TsRank(temp_delay,5)
        temp1 = pd.concat([temp,vwap,close], axis = 1, join = 'inner')
        temp1.columns = ['temp','vwap','close']
        tep = pd.DataFrame(temp1['temp']/(temp1['vwap'] - temp1['close']))
        r2 = TsRank(volume,5)
        data2 = pd.concat([r2,tep], axis = 1, join  = 'inner')
        data2.columns = ['r2','tep']
        tep1 = pd.DataFrame(data2['r2']/data2['tep'])
        r3 = TsRank(tep1,5)
        r = pd.concat([r1,r3],axis = 1, join  = 'inner')
        r.columns = ['r1','r3']
        alpha = pd.DataFrame(r['r1'] + r['r3'])
        alpha.columns = ['alpha114']
        return alpha
        
    @timer    
    def alpha115(self):
        high = self.high
        low = self.low   
        volume = self.volume
        volume_mean = Mean(volume,30)
        price = pd.concat([high,low], axis = 1, join  = 'inner')
        price.columns = ['high','low']
        price_temp = price['high'] * 0.9 + price['low'] * 0.1
        data  = pd.concat([price_temp,volume_mean],axis = 1, join  = 'inner')
        corr = Corr(data,10)
        r1 = Rank(corr)
        data2 = pd.concat([high,low], axis = 1, join = 'inner')
        temp = pd.DataFrame((data2['High'] + data2['Low'])/2)
        temp_r = TsRank(temp,4)
        volume_r = TsRank(volume,10)
        data3 = pd.concat([temp_r,volume_r], axis = 1, join  = 'inner')
        corr2 = Corr(data3,7)
        r2 = Rank(corr2)
        r = pd.concat([r1,r2], axis = 1, join  = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1'] * r['r2'])
        alpha.columns = ['alpha115']
        return alpha
    
    @timer
    def alpha116(self):
        close = self.close
        alpha = RegResi(0,close,None,20)
        alpha.columns = ['alpha116']
        return alpha
    
    @timer   
    def alpha117(self):
        high = self.high
        low = self.low 
        close = self.close
        volume = self.volume
        ret = self.ret
        r1 = TsRank(volume,32)
        data1 = pd.concat([close,high,low],axis = 1, join  = 'inner')
        r2 = TsRank(pd.DataFrame(data1['Close'] + data1['High'] - data1['Low']),16)
        r3 = TsRank(ret,32)
        r = pd.concat([r1,r2,r3], axis = 1, join  = 'inner')
        r.columns = ['r1','r2','r3']
        alpha = pd.DataFrame(r['r1'] * (1 - r['r2']) * (1 - r['r3']))
        alpha.columns = ['alpha117']
        return alpha
    
    @timer
    def alpha118(self):
        high = self.high
        low = self.low
        Open = self.open
        data = pd.concat([high,low,Open], axis = 1, join = 'inner')
        s1 = Sum(pd.DataFrame(data['High'] - data['Open']),20)
        s2 = Sum(pd.DataFrame(data['Open'] - data['Low']),20)
        s = pd.concat([s1,s2], axis = 1, join = 'inner')
        s.columns = ['s1','s2']
        alpha = pd.DataFrame(s['s1']/s['s2'] * 100)
        alpha.columns = ['alpha118']
        return alpha
    
    @timer
    def alpha119(self):
        Open = self.open
        volume = self.volume
        vwap = self.vwap
        volume_mean = Mean(volume,5)
        volume_mean_sum = Sum(volume_mean,26)
        data1 = pd.concat([vwap,volume_mean_sum],axis = 1, join = 'inner')
        corr1 = Corr(data1,5)
        corr1_decay = DecayLinear(corr1,7)
        r1 = Rank(corr1_decay)    
        open_r = Rank(Open)
        volume_mean2 = Mean(volume,15)
        volume_mean2_r = Rank(volume_mean2)
        data2 = pd.concat([open_r, volume_mean2_r], axis = 1, join  = 'inner')
        corr2 = Corr(data2,21)
        corr2_min = TsMin(corr2,9)
        corr2_min_r = TsRank(corr2_min,7)
        corr_min_r_decay = DecayLinear(corr2_min_r,8)
        r2 = Rank(corr_min_r_decay)
        r = pd.concat([r1,r2], axis = 1, join = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1'] - r['r2'])
        alpha.columns = ['alpha119']
        return alpha
    
    @timer    
    def alpha120(self):
        vwap = self.vwap
        close = self.close
        data = pd.concat([vwap,close], axis = 1, join  = 'inner')
        r1 = Rank(pd.DataFrame(data['Vwap'] - data['Close']))
        r2 = Rank(pd.DataFrame(data['Vwap'] + data['Close']))
        r = pd.concat([r1,r2],axis = 1, join = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1']/r['r2'])
        alpha.columns = ['alpha120']
        return alpha
    
    @timer
    def alpha121(self):
        vwap = self.vwap
        volume = self.volume
        vwap_r = TsRank(vwap,20)
        volume_mean = Mean(volume,60)
        volume_mean_r = TsRank(volume_mean,2)
        data = pd.concat([vwap_r,volume_mean_r], axis = 1, join = 'inner')
        corr=  Corr(data,18)
        temp = TsRank(corr,3)
        vwap_min = TsMin(vwap,12)
        data2 = pd.concat([vwap,vwap_min],axis = 1, join  = 'inner')
        data2.columns = ['vwap','vwap_min']
        rank = Rank(pd.DataFrame(data2['vwap'] - data2['vwap_min']))
        data3 = pd.concat([rank,temp],axis = 1, join  = 'inner')
        data3.columns = ['rank','temp']
        alpha = pd.DataFrame(np.power(data3['rank'],data3['temp']) * -1)
        alpha.columns = ['alpha121']
        return alpha
    
    @timer    
    def alpha122(self):
        close = self.close
        close_ln = pd.DataFrame(np.log(close))
        temp1 = SMA(close_ln,13,2)
        sma1 = SMA(temp1,13,2)
        sma2 = SMA(sma1,13,2)
        sma3 = SMA(sma2,13,2)
        sma3_delay = Delay(sma3,1)
        data = pd.concat([sma3,sma3_delay],axis = 1, join = 'inner')
        data.columns  = ['sma','sma_delay']
        alpha = pd.DataFrame(data['sma']/data['sma_delay'])
        alpha.columns = ['alpha122']
        return alpha
    
    @timer
    def alpha123(self):
        volume = self.volume
        high = self.high
        low = self.low
        data1 = pd.concat([high,low], axis = 1, join  = 'inner')
        s1 = Sum(pd.DataFrame((data1['High'] + data1['Low'])/2),20)
        volume_mean = Mean(volume,60)
        s2 = Sum(volume_mean,20)
        data2 = pd.concat([s1,s2], axis = 1, join  = 'inner')
        corr1 = Corr(data2,9)
        data3 = pd.concat([low,volume], axis = 1, join = 'inner')
        corr2 = Corr(data3,6)
        corr1_r = Rank(corr1)
        corr2_r = Rank(corr2)
        data = pd.concat([corr1_r,corr2_r], axis = 1, join  = 'inner')
        data.columns = ['r1','r2']
        data['alpha'] = -1
        data['alpha'][data['r1'] >= data['r2']] = 0
        alpha = pd.DataFrame(data['alpha'])
        alpha.columns = ['alpha123']
        return alpha
    
    @timer 
    def alpha124(self):
        close = self.close
        vwap = self.vwap
        close_max = TsMax(close,30)
        close_max_r = Rank(close_max)
        close_max_r_decay = DecayLinear(close_max_r,2)
        close_max_r_decay.columns = ['decay']
        data = pd.concat([close,vwap,close_max_r_decay], axis = 1, join  ='inner')
        alpha = pd.DataFrame((data['Close'] - data['Vwap'])/data['decay'])
        alpha.columns = ['alpha124']
        return alpha
    
    @timer    
    def alpha125(self):
        close = self.close
        vwap = self.vwap    
        volume = self.volume
        volume_mean = Mean(volume,80)
        data1 = pd.concat([vwap,volume_mean], axis = 1, join  = 'inner')
        corr1 = Corr(data1,17)
        data2 = pd.concat([close,vwap], axis = 1, join  = 'inner')
        temp2 = pd.DataFrame(0.5*(data2['Close'] + data2['Vwap']))
        temp2_delta = Delta(temp2,3)
        corr1_decay = DecayLinear(corr1,20)
        r1 = Rank(corr1_decay)
        temp2_delta_decay = DecayLinear(temp2_delta,16)
        r2 = Rank(temp2_delta_decay)
        r = pd.concat([r1,r2], axis = 1, join = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1']/r['r2'])
        alpha.columns = ['alpha125']
        return alpha
    
    @timer
    def alpha126(self):
        close = self.close
        high = self.high
        low = self.low
        data = pd.concat([close,high,low], axis = 1, join  = 'inner')
        alpha = pd.DataFrame((data['Close'] + data['High'] + data['Low'])/3)
        alpha.columns = ['alpha126']
        return alpha
    
    @timer
    def alpha127(self):
        close = self.close
        close_max = TsMax(close,12)
        data = pd.concat([close,close_max], axis = 1, join = 'inner')
        data.columns = ['close','close_max']
        alpha = pd.DataFrame((data['close'] -  data['close_max'])/data['close_max'])
        alpha.columns = ['alpha127']
        return alpha
    
    @timer    
    def alpha128(self):
        close = self.close
        high = self.high
        low = self.low
        volume = self.volume
        data = pd.concat([close,high,low,volume], axis = 1, join = 'inner')
        data['temp1'] = (data['Close'] + data['Low'] + data['High'])/3
        data['temp2'] = data['temp1'] * data['Vol']
        data['temp3'] = data['temp1'] * data['Vol']
        temp_delay = Delay(pd.DataFrame(data['temp1']),1)
        temp_delay.columns = ['temp_decay']
        data = pd.concat([data,temp_delay], axis = 1, join = 'inner')
        data['temp2'][data['temp1'] < data['temp_decay']] = 0
        data['temp3'][data['temp1'] > data['temp_decay']] = 0 
        s1 = Sum(pd.DataFrame(data['temp2']),14)
        s2 = Sum(pd.DataFrame(data['temp3']),14)
        s = pd.concat([s1,s2], axis = 1, join  = 'inner')
        s.columns = ['s1','s2']
        alpha = pd.DataFrame(100 - 100/(1+ s['s1']/s['s2']))
        alpha.columns = ['alpha128']
        return alpha
    
    @timer
    def alpha129(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay], axis = 1, join = 'inner')
        data.columns = ['close','close_delay']
        data['abs'] = np.abs(data['close'] - data['close_delay'])
        data['temp'] = data['abs']
        data['temp'][data['close'] < data['close_delay']] = 0
        alpha = Sum(pd.DataFrame(data['temp']),12)
        alpha.columns = ['alpha129']
        return alpha
    
    @timer
    def alpha130(self):
        close = self.close
        high = self.high
        low = self.low
        volume = self.volume
        volume_mean = Mean(volume,40)
        data1 = pd.concat([high,low],axis = 1, join  = 'inner')
        temp1 = pd.DataFrame((data1['High'] + data1['Low'])/2)
        rank1 = pd.concat([temp1,volume_mean], axis = 1, join  = 'inner')
        corr = Corr(rank1,9)
        close_r = Rank(close)
        volume_r = Rank(volume)
        data2 = pd.concat([close_r,volume_r],axis = 1, join  = 'inner')
        corr2 = Corr(data2,7)
        corr_decay = DecayLinear(corr,10)
        r1 = Rank(corr_decay)
        corr2_decay = DecayLinear(corr2,3)
        r2 = Rank(corr2_decay)
        r = pd.concat([r1,r2],axis = 1, join  = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1']/r['r2'])
        alpha.columns = ['alpha130']
        return alpha
    
    @timer
    def alpha131(self):
        close = self.close
        vwap = self.vwap
        volume = self.volume
        volume_mean = Mean(volume,50)
        data1 = pd.concat([close,volume_mean], axis = 1, join = 'inner')
        corr = Corr(data1,18)        
        vwap_delta = Delta(vwap,1)
        temp2 = TsRank(corr,18)
        data2 = pd.concat([vwap_delta,temp2],axis = 1, join  = 'inner')
        data2.columns = ['vwap_delta','temp2']
        temp3 = np.power(data2['vwap_delta'],data2['temp2'])
        alpha = Rank(pd.DataFrame(temp3))
        alpha.columns = ['alpha131']
        return alpha
    
    @timer    
    def alpha132(self):
        amt = self.amt
        alpha = Mean(amt,20)
        alpha.columns = ['alpha132']
        return alpha
    
    @timer
    def alpha133(self):
        low = self.low
        high = self.high
        highday = Highday(high,20)
        lowday = Lowday(low,20)
        data = pd.concat([highday,lowday],axis = 1, join  = 'inner')
        data.columns  = ['highday','lowday']
        alpha = (20 - data['highday']/20.0) * 100 - (20 - data['lowday']/20.0) * 100
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha133']
        return alpha
    
    @timer   
    def alpha134(self):
        close = self.close
        volume = self.volume
        close_delay = Delay(close,12)
        close_delay.columns = ['close_delay']
        data = pd.concat([close,volume,close_delay], axis = 1, join = 'inner')
        alpha = pd.DataFrame((data['Close'] - data['close_delay'])/data['close_delay'])
        alpha.columns  = ['alpha134']
        return alpha
    
    @timer    
    def alpha135(self):
        close = self.close
        close_delay = Delay(close,20)
        data = pd.concat([close,close_delay],axis = 1 , join  = 'inner')
        data.columns = ['close','close_delay']
        temp = pd.DataFrame(data['close']/data['close_delay'])
        temp_delay = Delay(temp,1)
        alpha = SMA(temp_delay,20,1)
        alpha.columns = ['alpha135']
        return alpha
    
    @timer
    def alpha136(self):
        volume = self.volume
        Open = self.open
        ret = self.ret
        ret_delta = Delta(ret,3)
        ret_delta_r = Rank(ret_delta)
        data = pd.concat([Open,volume],axis = 1, join  = 'inner')
        corr = Corr(data,10)
        data_temp = pd.concat([ret_delta_r,corr],axis = 1, join = 'inner')
        data_temp.columns = ['ret_delta','corr']
        alpha = pd.DataFrame(-1 * data_temp['ret_delta'] * data_temp['corr'])
        alpha.columns = ['alpha136']
        return alpha
    
    @timer
    def alpha137(self):
        Open = self.open
        close = self.close
        low = self.low
        high = self.high
        close_delay = Delay(close,1)
        open_delay = Delay(Open,1)
        low_delay = Delay(low,1)
        data = pd.concat([Open,close,low,high,close_delay,open_delay,low_delay], axis =1 ,join = 'inner')
        data.columns= ['open','close','low','high','close_delay','open_delay','low_delay']
        temp1 = pd.DataFrame((data['close'] - data['close_delay'] + (data['close'] - data['open'])/2\
                + data['close_delay'] - data['open_delay'])/ np.abs(data['high'] - data['close_delay']))
        temp2 = pd.DataFrame(np.abs(data['high'] - data['close_delay']) + np.abs(data['low'] - data['close_delay'])/2 \
                + np.abs(data['close_delay'] - data['open_delay'])/4)
        temp3 = pd.DataFrame(np.abs(data['low'] - data['close_delay']) + np.abs(data['high'] - data['close_delay'])/2 \
                + np.abs(data['close_delay'] - data['open_delay'])/4)
        
        abs1 = pd.DataFrame(np.abs(data['high'] - data['close_delay']))
        abs2 = pd.DataFrame(np.abs(data['low'] - data['close_delay']))
        abs3 = pd.DataFrame(np.abs(data['high'] - data['low_delay']))
        data1 = pd.concat([abs1,abs2,abs3], axis = 1, join  = 'inner')
        data1.columns = ['abs1','abs2','abs3']
        
        data_temp = pd.concat([abs1,abs2],axis = 1, join  = 'inner')
        data_temp_max = pd.DataFrame(np.max(data_temp,axis = 1))
        data_temp_max.columns = ['max']
        data_temp1 = pd.concat([data,data_temp_max], axis = 1, join  = 'inner')
        temp4 = pd.DataFrame((np.abs(data_temp1['high'] - data_temp1['low_delay']) + \
            np.abs(data_temp1['close_delay'] - data_temp1['open_delay'])) *\
                 data_temp1['max'])
        data1['judge1'] = 0
        data1['judge2'] = 0
        data1['judge3'] = 0
        data1['judge4'] = 0
        data1['judge1'][data1['abs1'] > data1['abs2']] = 1
        data1['judge2'][data1['abs1'] > data1['abs3']] = 1
        data1['judge3'][data1['abs2'] > data1['abs3']] = 1
        data1['judge3'][data1['abs3'] > data1['abs1']] = 1
        judge_1 = pd.DataFrame(data1['judge1'] * data1['judge2'])
        judge_2 = pd.DataFrame(data1['judge3'] * data1['judge4'])
        data2 = pd.concat([temp1,temp2,temp3,temp4,judge_1,judge_2], axis = 1, join  = 'inner')
        data2.columns = ['t1','t2','t3','t4','j1','j2']
        data2['j3']  = 1
        data2['j4'] = data2['j3'] - data2['j1'] - data2['j2']
        data2['t5'] = data2['t2'] * data2['j1'] + data2['t3'] * data2['j2'] + \
                data2['t4'] * data2['j4']
        alpha = pd.DataFrame(16 * data2['t5']/data2['t1'])
        alpha.columns = ['alpha137']
        return alpha    
    
    @timer    
    def alpha138(self):
        vwap = self.vwap  
        volume = self.volume
        low = self.low
        data1 = pd.concat([low,vwap], axis = 1, join = 'inner')
        temp1 = pd.DataFrame(data1['Low'] * 0.7 + data1['Vwap'] * 0.3)
        temp1_delta = Delta(temp1,3)
        temp1_delta_decay = DecayLinear(temp1_delta,20)
        r1 = Rank(temp1_delta_decay)
        low_r = TsRank(low,8)
        volume_mean = Mean(volume,60)
        volume_mean_r = TsRank(volume_mean,17)
        data2 = pd.concat([low_r,volume_mean_r],axis = 1, join  = 'inner')
        corr = Corr(data2,5)
        corr_r = TsRank(corr,19)
        corr_r_decay = DecayLinear(corr_r,16)
        r2 = TsRank(corr_r_decay,7)
        r = pd.concat([r1,r2], axis = 1, join = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1'] - r['r2'])
        alpha.columns = ['alpha138']
        return alpha
        
    @timer
    def alpha139(self):
        Open = self.open
        volume = self.volume
        data = pd.concat([Open,volume], axis = 1, join  = 'inner')
        alpha = -1 * Corr(data,10)
        alpha.columns = ['alpha139']
        return alpha
    
    @timer    
    def alpha140(self):
        Open = self.open
        volume = self.volume 
        high = self.high
        low = self.low
        close = self.close
        open_r = Rank(Open)
        low_r = Rank(low)
        high_r = Rank(high)
        close_r = Rank(close)
        data1 = pd.concat([open_r,low_r,high_r,close_r],axis = 1, join = 'inner')
        data1.columns = ['open_r','low_r','high_r','close_r']
        temp = pd.DataFrame(data1['open_r'] + data1['low_r'] - \
                            (data1['high_r'] + data1['close_r']))
        close_r_temp = TsRank(close,8)
        volume_mean = Mean(volume,70)
        volume_mean_r = TsRank(volume_mean,20)
        data2 = pd.concat([close_r_temp,volume_mean_r], axis = 1, join = 'inner')
        corr = Corr(data2,8)
        temp_decay = DecayLinear(temp,8)
        r1 = Rank(temp_decay)
        corr_decay = DecayLinear(corr,7)
        r2 = TsRank(corr_decay,3)
        r = pd.concat([r1,r2], axis = 1, join = 'inner')
        alpha = pd.DataFrame(np.min(r))
        alpha.columns = ['alpha140']
        return alpha
    
    @timer
    def alpha141(self):
        volume = self.volume    
        high = self.high
        volume_mean = Mean(volume,15)
        high_r = Rank(high)
        volume_mean_r = Rank(volume_mean)
        data = pd.concat([high_r,volume_mean_r], axis = 1, join  = 'inner')
        corr = Corr(data,9)
        alpha = -1 * Rank(corr)
        alpha.columns = ['alpha141']
        return alpha
    
    @timer
    def alpha142(self):
        close = self.close
        volume = self.volume
        close_r = TsRank(close,10)
        r1 = Rank(close_r)
        close_delta = Delta(close,1)
        close_delta_delta = Delta(close_delta,1)
        r2 = Rank(close_delta_delta)
        volume_mean = Mean(volume,20)
        data = pd.concat([volume,volume_mean], axis = 1, join  = 'inner')
        data.columns = ['v','v_m']
        temp = pd.DataFrame(data['v']/data['v_m'])
        temp_r = TsRank(temp,5)
        r3 = Rank(temp_r)
        r = pd.concat([r1,r2,r3],axis = 1, join  = 'inner')
        r.columns = ['r1','r2','r3']
        alpha = pd.DataFrame(- 1* r['r1'] * r['r2'] * r['r3'])
        alpha.columns= ['alpha142']
        return alpha
    
    @timer
    def alpha143(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay], axis = 1, join  = 'inner')
        data.columns = ['close','close_delay']
        temp = pd.DataFrame((data['close'] - data['close_delay'])/data['close_delay'])
        temp.columns= ['temp']
        data_temp = pd.concat([data,temp],axis = 1, join  = 'inner')
        data_temp['temp'][data_temp['close'] <= data_temp['close_delay']] = 1
        temp_unstack = data_temp['temp'].unstack()
        temp_unstack.iloc[0,:] = 1
        df = np.cumprod(temp_unstack,axis = 0)
        alpha = df.stack()
        alpha.columns = ['alpha143']
        return alpha
        
    @timer
    def alpha144(self):
        close = self.close
        amt = self.amt
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay,amt], axis = 1, join  = 'inner')
        data.columns = ['close','close_delay','amt']
        data['temp'] = np.abs(data['close']/data['close_delay'] - 1)/data['amt']
        data['sign'] = 1
        data['sign'][data['close'] >= data['close_delay']] = 0
        tep1 = Sum(pd.DataFrame(data['sign'] * data['temp']),20)
        tep2 =  Count(0,pd.DataFrame(data['close_delay']),pd.DataFrame(data['close']),20)
        data2 = pd.concat([tep1,tep2], axis = 1, join = 'inner')
        data2.columns = ['tep1','tep2']
        alpha = pd.DataFrame(data2['tep1']/data2['tep2'])
        alpha.columns = ['alpha144']
        return alpha
    
    @timer
    def alpha145(self):
        volume = self.volume
        volume_mean9 =  Mean(volume,9)
        volume_mean26 = Mean(volume,26)
        volume_mean12 = Mean(volume,12)
        data = pd.concat([volume_mean9,volume_mean26,volume_mean12], axis = 1, join = 'inner')
        data.columns = ['m9','m26','m12']
        alpha = pd.DataFrame((data['m9'] - data['m26'])/data['m12'] * 100)
        alpha.columns = ['alpha145']
        return alpha
    
    @timer
    def alpha146(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay],axis = 1, join  = 'inner')
        data.columns = ['close','close_delay']
        temp = pd.DataFrame((data['close'] -data['close_delay'])/data['close_delay'])
        sma1 = SMA(temp,61,2)
        data2 = pd.concat([temp,sma1], axis = 1, join  = 'inner')
        data2.columns = ['temp1','sma1']
        data2['temp2'] = data2['temp1'] - data2['sma1']
        temp2_mean = Mean(pd.DataFrame(data2['temp2']),20)
        sma2 = SMA(pd.DataFrame(data2['temp1'] - data2['temp2']),61,2)
        data_temp = pd.concat([temp2_mean,pd.DataFrame(data2['temp2']),sma2], axis = 1 , join = 'inner')
        data_temp.columns = ['temp2_mean','temp2','sma2']
        alpha = data_temp['temp2_mean'] * data_temp['temp2'] / data_temp['sma2']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha146']
        return alpha
    
    @timer
    def alpha147(self):
        close = self.close
        close_mean = Mean(close,12)
        alpha = RegBeta(0,close_mean,None,12)
        alpha.columns = ['alpha147']
        return alpha
    
    @timer
    def alpha148(self):
        Open = self.open
        volume = self.volume
        volume_mean = Mean(volume,60)
        volume_mean_s = Sum(volume_mean,9)
        data = pd.concat([Open,volume_mean_s],axis = 1, join  = 'inner')
        corr = Corr(data,6)
        r1 = Rank(corr)
        open_min = TsMin(Open,14)
        data2 = pd.concat([Open,open_min], axis = 1, join  = 'inner')
        data2.columns = ['open','open_min']
        r2 = Rank(pd.DataFrame(data2['open'] - data2['open_min']))
        r = pd.concat([r1,r2],axis = 1, join  = 'inner')
        r.columns  = ['r1','r2']
        r['alpha'] = -1
        r['alpha'][r['r1'] > r['r2']] = 0
        alpha = pd.DataFrame(r['alpha'])
        alpha.columns = ['alpha148']
        return alpha
    
    @timer
    def alpha149(self):
        close = self.close
        close_index = self.close_index
        close_delay = Delay(close,1)
        close_index_delay = Delay(close_index,1)
        data_index = pd.concat([close_index,close_index_delay], axis = 1, join = 'inner')
        data_index.columns = ['close','close_delay']
        data_index['delta'] = data_index['close']/data_index['close_delay'] - 1
        data_index['judge'] = 1
        data_index['judge'][data_index['close'] >= data_index['close_delay']] = 0
        data_index['delta'][data_index['judge'] == 0] = np.nan
    #    index_delta_unstack = index_delta_unstack.dropna()
        data = pd.concat([close,close_delay], axis = 1, join = 'inner')
        data.columns = ['close','close_delay']
        data['delta'] = data['close'] / data['close_delay'] - 1
        df1 = pd.DataFrame(data['delta'])
        df2 = pd.DataFrame(data_index['delta'])
        
        alpha = RegBeta(1,df1,df2,252)
        alpha.columns = ['alpha149']
        return alpha
        
    @timer
    def alpha150(self):
        high = self.high
        low = self.low
        close = self.close
        volume = self.volume
        data = pd.concat([high,low,close,volume], axis = 1, join  = 'inner')
        alpha = (data['Close'] + data['High'] + data['Low'])/3 * data['Vol']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha150']
        return alpha
    
    @timer
    def alpha151(self):
        close = self.close
        close_delay = Delay(close,20)
        data = pd.concat([close,close_delay], axis = 1, join  = 'inner')
        data.columns = ['close','close_delay']
        temp = pd.DataFrame(data['close'] - data['close_delay'])
        alpha = SMA(temp,20,1)
        alpha.columns = ['alpha151']
        return alpha
    
    @timer
    def alpha152(self):
        close = self.close
        close_delay = Delay(close,9)
        data = pd.concat([close,close_delay], axis = 1, join  = 'inner')
        data.columns = ['close','close_delay']  
        temp = pd.DataFrame(data['close']/data['close_delay'])
        temp_delay = Delay(temp,1)
        sma1 = SMA(temp_delay,9,1)
        sma1_delay = Delay(sma1,1)
        sma1_delay_mean1 = Mean(sma1_delay,12)
        sma1_delay_mean2 = Mean(sma1_delay,26)
        data_temp = pd.concat([sma1_delay_mean1,sma1_delay_mean2],axis = 1, join = 'inner')
        data_temp.columns = ['m1','m2']
        alpha = SMA(pd.DataFrame(data_temp['m1'] - data_temp['m2']),9,1)
        alpha.columns = ['alpha152']
        return alpha
    
    @timer    
    def alpha153(self):
        close = self.close
        close_mean3 = Mean(close,3)
        close_mean6 = Mean(close,6)
        close_mean12 = Mean(close,12)
        close_mean24 = Mean(close,24)
        data = pd.concat([close_mean3, close_mean6, close_mean12, close_mean24], axis = 1 ,join  ='inner')
        alpha = pd.DataFrame(np.mean(data, axis = 1))
        alpha.columns = ['alpha153']
        return alpha
    
    @timer
    def alpha154(self):
        volume = self.volume
        vwap = self.vwap
        volume_mean = Mean(volume,180)
        data = pd.concat([vwap,volume_mean], axis = 1, join = 'inner')
        corr = Corr(data,18)
        vwap_min = TsMin(vwap,16)
        data1 = pd.concat([vwap,vwap_min],axis = 1, join  = 'inner')
        data1.columns = ['vwap','vwap_min']
        temp = pd.DataFrame(data1['vwap'] - data1['vwap_min'])
        data_temp = pd.concat([corr,temp], axis = 1, join  = 'inner')
        data_temp.columns = ['corr','temp']
        data_temp['alpha'] = 1
        data_temp['alpha'][data_temp['corr'] >= data_temp['temp']] = 0
        alpha = pd.DataFrame(data_temp['alpha'])
        alpha.columns = ['alpha154']
        return alpha
    
    @timer    
    def alpha155(self):
        volume = self.volume
        sma1 = SMA(volume,13,2)
        sma2 = SMA(volume,26,2)
        sma = pd.concat([sma1, sma2], axis = 1, join  = 'inner')
        sma.columns = ['sma1','sma2']
        temp = pd.DataFrame(sma['sma1'] - sma['sma2'])
        sma3 = SMA(temp,10,2)
        data = pd.concat([temp,sma3], axis = 1 ,join = 'inner')
        data.columns = ['temp','sma']
        alpha = pd.DataFrame(data['temp'] - data['sma'])
        alpha.columns = ['alpha155']
        return alpha
    
    @timer    
    def alpha156(self):
        vwap = self.vwap
        Open = self.open
        low = self.low
        vwap_delta = Delta(vwap,5)
        vwap_delta_decay = DecayLinear(vwap_delta,3)
        r1 = Rank(vwap_delta_decay)
        data1 = pd.concat([Open,low],axis = 1, join = 'inner')
        temp = -1 * Delta(pd.DataFrame(data1['Open'] * 0.15 + data1['Low'] * 0.85),2)
        temp_decay = DecayLinear(temp,3)
        r2 = Rank(temp_decay)
        r = pd.concat([r1,r2],axis = 1, join = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(- 1 *np.max(r, axis = 1))
        alpha.columns = ['alpha156']
        return alpha
    
    @timer
    def alpha157(self):
        close = self.close
        ret = self.ret
        close_delta = Delta(close,5)
        close_delta_r = Rank(Rank(close_delta) * -1)
        r1 = TsMin(close_delta_r,2)
        ret_delay = Delay(-1 * ret,6)
        r2 = TsRank(ret_delay,5)
        r = pd.concat([r1,r2],axis = 1,join = 'inner')
        r.columns = ['r1','r2']
        temp = pd.DataFrame(r['r1'] + r['r2'])
        alpha = TsMin(temp,5)
        alpha.columns = ['alpha157']
        return alpha
        
    @timer
    def alpha158(self):
        high = self.high
        low = self.low
        close = self.close
        temp = SMA(close,15,2)
        temp.columns = ['temp']
        data = pd.concat([high,low,close,temp],axis = 1 , join  = 'inner')
        alpha =(data['High'] + data['Low'] - 2 * data['temp'] )/data['Close']
        alpha  = pd.DataFrame(alpha)
        alpha.columns = ['alpha158']
        return alpha
    
    @timer
    def alpha159(self):
        high = self.high
        low = self.low
        close = self.close   
        close_delay = Delay(close,1)
        data1 = pd.concat([low,close_delay],axis = 1, join = 'inner')
        data2 = pd.concat([high, close_delay], axis = 1, join  = 'inner')
        temp1 = pd.DataFrame(np.min(data1,axis = 1))
        temp2= pd.DataFrame(np.max(data2,axis = 1))
        temp = pd.concat([temp1,temp2], axis = 1 ,join = 'inner')
        temp.columns = ['temp1','temp2']
        temp1_sum6 = Sum(temp1,6)
        temp1_sum12 = Sum(temp1,12)
        temp1_sum24 = Sum(temp1,24)
        tep = pd.DataFrame(temp['temp2'] - temp['temp1'])
        s6 = Sum(tep,6)
        s12 = Sum(tep,12)
        s24 = Sum(tep,24)
        data3 = pd.concat([temp1_sum6,temp1_sum12,temp1_sum24,s6,s12,s24], axis = 1 ,join = 'inner')
        data3.columns = ['ts6','ts12','ts24','s6','s12','s24']
        temp3 = pd.DataFrame(data3['ts6']/data3['s6'] * 12 * 24 + data3['ts12']/data3['s12'] * 6 * 24 \
                    + data3['ts24']/data3['s24'] * 6 * 24)
        alpha = temp3 / (6*12 + 6*24 + 12*24) * 100
        alpha.columns = ['alpha159']
        return alpha
    
    @timer    
    def alpha160(self):
        close = self.close
        close_std = STD(close,20)
        close_delay = Delay(close,1)
        data = pd.concat([close,close_std,close_delay],axis = 1, join = 'inner')
        data.columns = ['close','close_std','close_delay']
        data['close_std'][data['close'] >= data['close_delay']] = 0
        alpha = SMA(pd.DataFrame(data['close_std']),20,1)
        alpha.columns = ['alpha160']
        return alpha
    
    @timer
    def alpha161(self):
        high = self.high
        low = self.low
        close = self.close
        close_delay = Delay(close,1)
        close_delay.columns = ['close_delay']
        data1 = pd.concat([high,low],axis = 1 , join = 'inner')
        diff = pd.DataFrame(data1['High'] - data1['Low'])
        data2 = pd.concat([close_delay,high], axis = 1, join ='inner')
        abs1 = pd.DataFrame(np.abs(data2['close_delay'] - data2['High']))
        data3 = pd.concat([diff,abs1], axis = 1, join = 'inner')
        temp1 = pd.DataFrame(np.max(data3,axis = 1))
        data4 = pd.concat([close_delay,low],axis = 1, join  = 'inner')
        temp2 = pd.DataFrame(np.abs(data4['close_delay'] -data4['Low']))
        data = pd.concat([temp1,temp2],axis =1 , join = 'inner')
        data.columns = ['temp1','temp2']
        temp = pd.DataFrame(np.max(data, axis = 1))
        alpha = Mean(temp,12)
        alpha.columns = ['alpha161']
        return alpha
    
    @timer    
    def alpha162(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay],axis = 1, join = 'inner')
        data.columns = ['close','close_delay']
        data['max']= data['close'] - data['close_delay']
        data['max'][data['max'] < 0] = 0
        data['abs'] = np.abs(data['close'] - data['close_delay'])
        temp1 = SMA(pd.DataFrame(data['max']),12,1)
        temp2 = SMA(pd.DataFrame(data['abs']),12,1)
        data1 = pd.concat([temp1,temp2], axis = 1, join = 'inner')
        data1.columns = ['temp1','temp2']
        tep = pd.DataFrame(data1['temp1']/data1['temp2'])
        temp3 = TsMin(tep,12)
        temp4 = TsMax(tep,12)
        data_temp = pd.concat([tep,temp3,temp4], axis = 1, join = 'inner')
        data_temp.columns = ['tep','temp3','temp4']
        alpha = (data_temp['tep'] - data_temp['temp3']/data_temp['temp4']) * 100
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha162']
        return alpha
    
    @timer
    def alpha163(self):
        low = self.low
        high = self.high
        volume = self.volume
        ret = self.ret
        vwap = self.vwap
        volume_mean = Mean(volume,20)
        data = pd.concat([high,low,vwap,ret,volume_mean],axis = 1, join = 'inner')
        data.columns = ['high','low','vwap','ret','volume_mean']
        temp = pd.DataFrame(-1 *data['ret'] * data['volume_mean'] *data['vwap'] * \
                        (data['high'] - data['low']))
        alpha = Rank(temp)
        alpha.columns = ['alpha163']
        return alpha
    
    @timer
    def alpha164(self):
        close = self.close
        high = self.high
        low = self.low
        close_delay = Delay(close,1)
        data = pd.concat([close,high,low,close_delay],axis = 1, join = 'inner')
        data.columns = ['close','high','low','close_delay']
        data['temp'] = 1/(data['close'] - data['close_delay'])
        data_min = TsMin(pd.DataFrame(data['temp']),12)
        data_min.columns = ['min']
        data2 = pd.concat([data,data_min],axis = 1, join = 'inner')
        data2['tep'] = data2['temp'] - data2['min']/(data2['high'] - data2['low'])
        data2['tep'][data['close'] <= data['close_delay']] = 0
        alpha = SMA(pd.DataFrame(data2['tep']) * 100,13,2)
        alpha.columns = ['alpha164']
        return alpha
    
    @timer
    def alpha165(self):
        close = self.close
        close_mean = Mean(close,48)
        data = pd.concat([close,close_mean],axis = 1, join = 'inner')
        data.columns = ['close','close_mean']
        temp = pd.DataFrame(data['close'] - data['close_mean'])
        temp_sum = Sum(temp,48)
        temp_sum_min = TsMin(temp_sum,48)
        temp_sum_max = TsMax(temp_sum,48)
        close_std = STD(close,48)
        data_temp = pd.concat([temp_sum_min,temp_sum_max,close_std], axis = 1, join = 'inner')
        data_temp.columns = ['min','max','std']
        alpha = (data_temp['max'] - data_temp['min'])/data_temp['std']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha165']
        return alpha
    
    @timer
    def alpha166(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay], axis = 1, join = 'inner')
        data.columns = ['close','close_delay']
        temp = pd.DataFrame(data['close']/data['close_delay'])
        temp_mean = Mean(temp,20)
        data1 = pd.concat([temp,temp_mean], axis = 1, join = 'inner')
        data1.columns = ['temp','temp_mean']
        temp2 = Sum(pd.DataFrame(data1['temp'] - data1['temp_mean']),20) * 20 * 19
        temp3 = Sum(temp,20) * 19 * 18
        data2 = pd.concat([temp2,temp3], axis = 1, join = 'inner')
        data2.columns = ['temp2','temp3']
        alpha = np.power(data2['temp2'],1.5)/np.power(data2['temp3'],1.5)
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha166']
        return alpha
    
    @timer    
    def alpha167(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay], axis = 1, join = 'inner')
        data.columns = ['close','close_delay']
        data['temp'] = data['close'] - data['close_delay']
        data['temp'][data['close'] <= data['close_delay']] = 0
        alpha = Sum(pd.DataFrame(data['temp']),12)
        alpha.columns = ['alpha167']
        return alpha
    
    @timer
    def alpha168(self):    
        volume = self.volume
        volume_mean = Mean(volume,20)
        data = pd.concat([volume,volume_mean], axis = 1, join = 'inner')
        data.columns = ['volume','volume_mean']
        alpha = data['volume']/data['volume_mean'] * -1
        alpha.columns = ['alpha168']
        return alpha
    
    @timer
    def alpha169(self):
        close = self.close
        close_delay = Delay(close,1)
        data = pd.concat([close,close_delay], axis = 1, join = 'inner')
        data.columns = ['close','close_delay']
        temp1 = pd.DataFrame(data['close'] - data['close_delay'])
        sma = SMA(temp1,9,1)
        temp2 = Delay(sma,1)
        temp2_mean12 = Mean(temp2,12)
        temp2_mean26 = Mean(temp2,26)
        data2 = pd.concat([temp2_mean12,temp2_mean26], axis = 1, join ='inner')
        data2.columns = ['mean1','mean2']
        alpha = SMA(pd.DataFrame(data2['mean1'] - data2['mean2']),10,1)
        alpha.columns = ['alpha169']
        return alpha
    
    @timer
    def alpha170(self):
        close = self.close
        high = self.high
        volume = self.volume
        vwap = self.vwap
        volume_mean = Mean(volume,20)
        data1 = pd.concat([high,close,volume,volume_mean], axis = 1, join = 'inner')
        data1.columns =['high','close','volume','volume_mean']
        temp1 = pd.DataFrame(data1['high']/data1['close'] *  data1['volume']/data1['volume_mean'])
        r1 = Rank(temp1)
        high_mean = Mean(high,5)
        vwap_delay = Delay(vwap,5)
        data2 = pd.concat([high,close,high_mean], axis = 1, join = 'inner')
        data2.columns = ['high','close','high_mean']
        temp2 = pd.DataFrame((data2['high'] - data2['close'])/data2['high_mean'])
        temp2_r = Rank(temp2)
        data3 = pd.concat([vwap,vwap_delay], axis = 1, join = 'inner')
        data3.columns = ['vwap','vwap_delay']
        temp3 = pd.DataFrame(data3['vwap'] - data3['vwap_delay'])
        temp3_r = Rank(temp3)
        rank = pd.concat([temp2_r,temp3_r], axis = 1, join = 'inner')
        rank.columns = ['r1','r2']
        r2 = pd.DataFrame(rank['r1'] - rank['r2'])
        data_temp = pd.concat([r1,r2],axis = 1, join  = 'inner')
        data_temp.columns = ['r1','r2']
        alpha = pd.DataFrame(data_temp['r1'] * data_temp['r2'])
        alpha.columns = ['alpha170']
        return alpha
    
    @timer
    def alpha171(self):
        high = self.high
        close = self.close
        low = self.low
        Open = self.open
        data = pd.concat([high,close,low,Open],axis = 1, join = 'inner')
        alpha = -1 * (data['Low'] - data['Close']) * np.power(data['Open'],5)/\
                ((data['Close'] - data['High']) * np.power(data['Close'],5))
        alpha.columns = ['alpha171']
        return alpha
    
    @timer
    def alpha172(self):
        high = self.high
        low = self.low
        hd = HD(high)
        ld = LD(low)
        data = pd.concat([hd,ld],axis = 1, join = 'inner')
        data.columns = ['hd','ld']
        data['temp'] = 0
        data['temp'][((data['hd'] > data['ld'])& (data['hd'] > 0)) | \
            ((data['ld'] > data['hd'])& (data['ld'] > 0))] = 1
        alpha = Mean(pd.DataFrame(data['temp']),6)
        alpha.columns = ['alpha172']
        return alpha
    
    @timer
    def alpha173(self):
        close = self.close
        close_ln = pd.DataFrame(np.log(close))
        temp1 = SMA(close,13,2)
        temp2 = SMA(close_ln,13,2)
        temp3 = SMA(temp1,13,2)
        temp4 = SMA(SMA(temp2,13,2),13,2)
        data = pd.concat([temp1,temp3,temp4], axis = 1, join  = 'inner')
        data.columns = ['t1','t2','t3']
        alpha = pd.DataFrame(3 * data['t1'] -  2 * data['t2'] + data['t3'])
        alpha.columns = ['alpha173']
        return alpha
    
    @timer
    def alpha174(self):
        close = self.close
        close_delay = Delay(close,1)
        close_std = STD(close,20)
        data = pd.concat([close,close_delay,close_std], axis = 1, join = 'inner')
        data.columns = ['close','close_delay','close_std']
        data['close_std'][data['close'] <= data['close_delay']] = 0
        alpha = SMA(pd.DataFrame(data['close_std']),12,1)
        alpha.columns = ['alpha174']
        return alpha    
    
    @timer    
    def alpha175(self):
        high = self.high   
        close = self.close
        low = self.low
        close_delay = Delay(close,1)
        data = pd.concat([high,close,low,close_delay],axis = 1, join  = 'inner')
        data.columns = ['high','close','low','close_delay']
        data_abs = pd.DataFrame(np.abs(data['close_delay'] - data['high']))
        h_l = pd.DataFrame(data['high'] - data['low'])
        data1 = pd.concat([data_abs,h_l], axis = 1, join = 'inner')
        temp1 = pd.DataFrame(np.max(data1,axis = 1))
        data_abs2 = pd.DataFrame(np.abs(data['close_delay'] - data['low']))
        data2 = pd.concat([temp1,data_abs2], axis = 1, join = 'inner')
        temp2 = pd.DataFrame(np.max(data2,axis = 1))
        data3 = pd.concat([temp1,temp2],axis = 1, join  = 'inner')
        max_temp = pd.DataFrame(np.max(data3,axis = 1))
        alpha = Mean(max_temp,6)
        alpha.columns = ['alpha175']
        return alpha
    
    @timer
    def alpha176(self):
        high = self.high   
        close = self.close
        low = self.low   
        volume = self.volume
        low_min = TsMin(low,12)
        high_max = TsMax(high,12)
        data1 = pd.concat([close,low_min,high_max],axis = 1, join = 'inner')
        data1.columns  = ['close','low_min','high_max']
        temp = pd.DataFrame((data1['close'] - data1['low_min'])\
                            /(data1['high_max'] - data1['low_min']))
        r1 = Rank(temp)
        r2 = Rank(volume)
        rank = pd.concat([r1,r2], axis = 1, join  = 'inner')
        alpha = Corr(rank,6)
        alpha.columns = ['alpha176']
        return alpha
    
    @timer
    def alpha177(self):
        high = self.high
        highday = Highday(high,20)
        alpha = pd.DataFrame((20 - highday)/20.0 * 100)
        alpha.columns = ['alpha177']
        return alpha
        
    @timer
    def alpha178(self):
        close = self.close
        close_delay = Delay(close,1)
        volume = self.volume
        data = pd.concat([close,close_delay,volume], axis = 1, join  = 'inner')
        data.columns = ['close','close_delay','volume']
        alpha = pd.DataFrame((data['close'] - data['close_delay'])\
                             /data['close_delay'] * data['volume'])
        alpha.columns = ['alpha178']
        return alpha
    
    @timer
    def alpha179(self):
        low = self.low    
        volume = self.volume
        vwap = self.vwap
        data1 = pd.concat([vwap,volume], axis = 1, join  = 'inner')
        corr = Corr(data1,4)
        r1 = Rank(corr)
        volume_mean = Mean(volume,50)
        volume_mean_r = Rank(volume_mean)
        row_r = Rank(low)
        data2 = pd.concat([row_r,volume_mean_r], axis = 1, join = 'inner')
        corr2 = Corr(data2,12)
        r2 = Rank(corr2)
        data = pd.concat([r1,r2], axis = 1, join  = 'inner')
        data.columns = ['r1','r2']
        alpha = pd.DataFrame(data['r1'] * data['r2'])
        alpha.columns = ['alpha179']
        return alpha
    
    @timer
    def alpha180(self):
        volume = self.volume
        close = self.close
        close_delta = Delta(close,7)
        volume_mean = Mean(volume,20)
        close_delta_abs = pd.DataFrame(np.abs(close_delta))
        r = TsRank(close_delta_abs,60)
        sign = pd.DataFrame(np.sign(close_delta))
        temp = pd.concat([r,sign],axis = 1, join  = 'inner')
        temp.columns  = ['r','sign']
        temp1 = temp['r'] * temp['sign']
        data = pd.concat([volume,volume_mean,temp1], axis = 1, join  = 'inner')
        data.columns  = ['volume','volume_mean','temp1']
        data['volume1'] = data['volume']
        data['temp1'][data['volume'] >= data['volume_mean']] = 0
        data['volume1'][data['volume'] < data['volume_mean']] = 0
        alpha = -1 * pd.DataFrame(data['volume1'] + data['temp1'])
        alpha.columns = ['alpha180']
        return alpha
    
    @timer    
    def alpha181(self):
        close = self.close
        close_index = self.close_index
        close_delay = Delay(close,1)
        data1 = pd.concat([close,close_delay],axis = 1, join  = 'inner')
        data1.columns = ['close','close_delay']
        temp = pd.DataFrame(data1['close']/data1['close_delay']) - 1
        temp_mean = Mean(temp,20)
        data_temp = pd.concat([temp,temp_mean], axis = 1, join  = 'inner')
        data_temp.columns = ['temp','temp_mean']
        temp1 = pd.DataFrame(data_temp['temp'] - data_temp['temp_mean'])
        
        close_index_mean = Mean(close_index,20)
        data2 = pd.concat([close_index,close_index_mean], axis = 1, join  = 'inner')
        data2.columns = ['close_index','close_index_mean']
        temp2 = pd.DataFrame(np.power(data2['close_index'] - data2['close_index_mean'],2))
        
        temp3 = pd.DataFrame(np.power(data2['close_index'] - data2['close_index_mean'],3))
        temp1_unstack = temp1.unstack()
        temp2_unstack = temp2.unstack()
        temp2_mod = pd.DataFrame(repmat(temp2_unstack,1,np.size(temp1_unstack,1)))
        temp3_unstack = temp3.unstack() 
        temp3_mod = pd.DataFrame(repmat(temp3_unstack,1,np.size(temp1_unstack,1)))
        temp1_result = temp1_unstack.rolling(20, min_periods = 20).sum()
        temp2_result = temp2_mod.rolling(20, min_periods = 20).sum()
        temp2_result.index = temp2_unstack.index.tolist()
        temp3_result = temp3_mod.rolling(20, min_periods = 20).sum()
        temp3_result.index = temp3_unstack.index.tolist()
        result = pd.concat([temp1_result,temp2_result,temp3_result], axis = 1, join  = 'inner')
        m = np.size(temp1_result,1)
        alpha_temp = pd.DataFrame((result.values[:,:m] - result.values[:,m:2*m])/result.values[:,2*m:])
        df1 = result.iloc[:,:m]
        alpha_temp.columns = df1.columns.tolist()
        alpha_temp.index = df1.index.tolist()
        alpha = pd.DataFrame(alpha_temp.stack())
        alpha.columns = ['alpha181']
        return alpha
    
    @timer    
    def alpha182(self):
        close = self.close
        Open = self.open
        close_index = self.close_index
        open_index = self.open_index
        data1 = pd.concat([close,Open], axis = 1, join = 'inner')
        data1['temp'] = 1
        data1['temp'][data1['Close'] <= data1['Open']] = 0
        data1['temp1'] = 1
        data1['temp1'][data1['Close'] > data1['Open']] = 0
        
        data2 = pd.concat([close_index,open_index], axis = 1, join = 'inner')
        data2['tep'] = 0
        data2['tep'][data2['close'] > data2['open']] = 1
        data2['tep1'] = 0
        data2['tep1'][data2['close'] < data2['open']] = 1
        temp = data1['temp'].unstack() 
        temp1 = data1['temp1'].unstack()
        tep = data2['tep'].unstack()
        tep1 = data2['tep1'].unstack()
        tep_rep = repmat(tep,1,np.size(temp,1))
        tep1_rep = repmat(tep1,1,np.size(temp,1))
        data3 = temp * tep_rep + temp1 * tep1_rep - temp * tep_rep * temp1 * tep1_rep
        result = data3.rolling(20,min_periods = 20).sum()
        alpha_temp = result/20.0
        alpha = pd.DataFrame(alpha_temp.stack())
        alpha.columns = ['alpha182']
        return alpha
    
    @timer    
    def alpha183(self):
        close = self.close
        close_mean = Mean(close,24)
        close_std = STD(close,24)
        data1 = pd.concat([close,close_mean], axis = 1, join = 'inner')
        data1.columns = ['close','close_mean']
        temp = pd.DataFrame(data1['close'] - data1['close_mean'])
        temp_max = TsMin(temp,24)
        temp_min = TsMin(temp,24)
        data2 = pd.concat([temp_max,temp_min,close_std],axis = 1, join = 'inner')
        data2.columns = ['max','min','std']
        alpha = pd.DataFrame((data2['max'] - data2['min'])/data2['std'])
        alpha.columns = ['alpha183']
        return alpha
        
    @timer    
    def alpha184(self):
        close = self.close
        Open = self.open
        data = pd.concat([close,Open], axis = 1, join  = 'inner')
        data['diff'] = data['Open'] - data['Close']
        diff_delay = Delay(pd.DataFrame(data['diff']),1)
        data1 = pd.concat([diff_delay,close],axis = 1, join  = 'inner')
        corr = Corr(data1,200)
        r1 = Rank(corr)
        r2 = Rank(pd.DataFrame(data['diff']))
        r = pd.concat([r1,r2], axis = 1, join = 'inner')
        r.columns = ['r1','r2']
        alpha = pd.DataFrame(r['r1'] + r['r2'])
        alpha.columns = ['alpha184']
        return alpha
    
    @timer
    def alpha185(self):
        close = self.close
        Open = self.open
        data = pd.concat([close,Open], axis = 1, join  = 'inner')
        temp =  pd.DataFrame(data['Open']/data['Close'])
        tep = -1 * (1 - np.power(temp,2))
        alpha = Rank(pd.DataFrame(tep))
        alpha.columns = ['alpha185']
        return alpha
    
    @timer
    def alpha186(self):
        high = self.high
        low = self.low
        hd = HD(high)
        ld = LD(low)
        data = pd.concat([hd,ld],axis = 1, join = 'inner')
        data.columns = ['hd','ld']
        data['temp'] = 0
        data['temp'][((data['hd'] > data['ld'])& (data['hd'] > 0)) | \
            ((data['ld'] > data['hd'])& (data['ld'] > 0))] = 1  
        temp = pd.DataFrame(data['temp'])
        temp_mean = Mean(temp,6)
        temp_mean_delay = Delay(temp_mean,6)
        data = pd.concat([temp_mean,temp_mean_delay], axis = 1, join = 'inner')
        data.columns  = ['mean','delay']
        alpha = pd.DataFrame((data['mean'] + data['delay'])/2)
        alpha.columns = ['alpha186']
        return alpha
    
    @timer    
    def alpha187(self):
        Open = self.open
        high = self.high 
        open_delay = Delay(Open,1)
        data = pd.concat([Open,high,open_delay], axis = 1, join  = 'inner')
        data.columns  = ['open','high','open_delay']
        diff = pd.DataFrame(data['high'] - data['open'])
        open_delta = Delta(Open,1)
        data1 = pd.concat([diff, open_delta], axis = 1, join  = 'inner')
        max_temp = pd.DataFrame(np.max(data1, axis = 1))
        temp = Sum(max_temp,20)
        data2 = pd.concat([Open,open_delay,temp],axis = 1, join  = 'inner')
        data2.columns = ['open','open_delay','temp']
        data2['temp'][data['open'] > data['open_delay']] = 0
        alpha = pd.DataFrame(data2['temp'])
        alpha.columns = ['alpha187']
        return alpha
    
    @timer
    def alpha188(self):
        high = self.high  
        low = self.low 
        data = pd.concat([high,low],axis = 1, join  = 'inner')
        temp = SMA(pd.DataFrame(data['High'] - data['Low']),11,2)
        data1 = pd.concat([temp,low,high],axis = 1, join  = 'inner')
        data1.columns = ['temp','low','high']
        alpha = (data1['high'] - data1['low'] - data1['temp'])/data1['temp'] * 100
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha188']
        return alpha
    
    @timer
    def alpha189(self):
        close = self.close
        close_mean = Mean(close,6)
        data = pd.concat([close,close_mean], axis = 1, join  = 'inner')
        data.columns  = ['close','close_mean']
        temp = pd.DataFrame(np.abs(data['close'] - data['close_mean']))
        alpha = Mean(temp,6)
        alpha.columns = ['alpha189']
        return alpha
    
    @timer
    def alpha190(self):
        close = self.close
        close_delay1 = Delay(close,1)
        close_delay19 = Delay(close,19)
        data1 = pd.concat([close,close_delay1], axis = 1, join  = 'inner')
        data1.columns= ['close','close_delay1']
        temp1 = pd.DataFrame(data1['close']/data1['close_delay1'])
        data2 = pd.concat([close,close_delay19], axis = 1, join = 'inner')
        data2.columns = ['close','close_delay19']
        temp2 = pd.DataFrame(np.power(data2['close']/data2['close_delay19'],1.0/20))
        temp3 = Count(0,temp1,temp2,20)
        data3 = pd.concat([temp1,temp2], axis = 1, join = 'inner')
        data3.columns = ['temp1','temp2']
        tep = pd.DataFrame(np.power(data3['temp1'] - data3['temp2'],2))
        data4 = pd.concat([tep,temp1,temp2],axis = 1, join  = 'inner')
        data4.columns = ['tep','temp1','temp2']
        temp4 = SUMIF(0,data4['tep'],20,data4['temp1'],data4['temp2'])
        temp5 = Count(1,temp2,temp1,20)
        temp6 = SUMIF(1,data4['tep'],20,data4['temp2'],data4['temp1'])
        data = pd.concat([temp3,temp4,temp5,temp6], axis = 1, join = 'inner')
        data.columns = ['temp3','temp4','temp5','temp6']
        alpha = np.log(data['temp3'] * data['temp4'] / (data['temp5'] * data['temp6']))
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha190']
        return alpha
    
    @timer
    def alpha191(self):
        high = self.high
        low = self.low
        close = self.close
        volume = self.volume
        volume_mean = Mean(volume,20)
        data1 = pd.concat([volume_mean,low],axis = 1, join  = 'inner')
        corr = Corr(data1,5)
        data = pd.concat([corr,high,low,close],axis = 1, join  = 'inner')
        data.columns  = ['corr','high','low','close']
        alpha = data['corr'] + (data['high'] + data['low'])/2 - data['close']
        alpha = pd.DataFrame(alpha)
        alpha.columns = ['alpha191']
        return alpha
    
    
    
    
          
#if __name__ == '__main__':
#    alpha  = stAlpha('2005-01-01','2017-12-31')
    
    

