# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 16:00:39 2018

@author: admin
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from utils import winsorize,standardize,get_industry_matrix,get_resi_factor

class factorAnalyzer(object):
    def __init__(self,begin,end):
        self.begin = begin
        self.end = end
    
    @staticmethod    
    def factor_information_coefficient(factor_data,
                                       ret,
                                       mode):
        """
        Compute the information coefficient between factor values and N period forward
        returns 
        
        Params:
        ---------------------
            factor_data:
                pd.DataFrame, MultiIndex, indexed by date(level 0) and secID(level 1)
            ret:
                pd.DataFrame, MultiIndex, indexed by date(level 0) and secID(level 1)
            mode:
                enums, if mode == 0: IC is the corr(Rank(ret), Rank(factor)), if mode == 1: 
                    IC is the corr(ret, Rank(factor)), and else IC is the corr(ret, factor)
                
        """
        
        
        
        
        

    
