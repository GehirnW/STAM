# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 14:42:23 2018

@author: admin
"""

import datetime
import time
from functools import wraps

import pandas as pd
from WindPy import w
from logbook import FileHandler, Logger
from pypika import Query, Table
from sqlalchemy import create_engine

w.start()


def timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print("Total time running %s: %s seconds" % (function.__name__, str(round((t1 - t0), 2))))
        return result

    return function_timer


def get_tdays(engine, is_trade_day=1):
    '''
    Get all the trade day series
    
    Params:
        engine:
            database engine
        is_trade_day:
            int, 1 is trade day; 0 is not
    Returns:
        pd.Series, values: str
    
    '''
    a = Table('trade_calendar')
    q = Query.from_(a).select(
        a.calendar_date
    ).where(
        a.is_trade_day == is_trade_day
    ).orderby(
        a.calendar_date)

    tdays = (pd.read_sql(q.get_sql(), engine)
             .calendar_date
             .apply(lambda dt: dt.strftime('%Y%m%d')))
    return tdays


def get_code(date, engine):
    # 获取当期所有的股票 list
    a = Table('stock_market_data')
    q = Query.from_(a).select(
        a.stock_id
    ).where(
        a.trade_date == date
    ).orderby(
        a.stock_id
    )
    data = pd.read_sql(q.get_sql(), engine)
    return data.stock_id.tolist()


def create_table():
    sql = '''
             create table if not exists stock_industry_citic_new
             (
                id                   int           not null   primary key auto_increment,
                trade_date        varchar(8)       not null,
                stock_id          varchar(10)      not null,
                industry_citic    varchar(12)      not null,
                unique key index_1(trade_date, stock_id) 
             );
          '''
    engine.execute(sql)

    return


@timer
def cs_indus(date, engine):
    '''
    Params:
        date:
            string, like '%Y%m%d' 
        engine:
            target database engine to save data
    '''
    code = get_code(date, engine)
    wdata = w.wss(code, "indexcode_citic", industryType=1, tradeDate=date)
    while wdata.ErrorCode == -40522017:
        print('Quota exceeded')

    if wdata.ErrorCode == 0:
        data = pd.DataFrame(dict(zip(wdata.Fields, wdata.Data)), index=wdata.Codes)
        data = data.reset_index().dropna()
        data.rename(columns={'index': 'stock_id', 'INDEXCODE_CITIC': 'industry_citic'}, inplace=True)
        data['trade_date'] = date
        data.sort_values(by='stock_id', inplace=True)

        try:
            data.to_sql(name='stock_industry_citic_new', con=engine, if_exists='append', index=False)
            print('Successfully fininshed updating stock_industry_citic:', date)
            return
        except:
            print(date, 'stock_industry_citic already exists')
            return
    else:
        raise TypeError(wdata)


def check_log(date, log_file_name):
    '''
    if the date next day successfully wrote to database, then ignore the date
    because there four py file need to be executed
    
    Params:
        date:
            str, like '%Y%m%d'
    '''
    with open(log_file_name) as f:
        log_text = f.read()
    if date + ': 1' in log_text:
        return True
    else:
        return False


if __name__ == "__main__":
#    import os

    # PATH = r'G:\quant\MaintainDB\cs_industry'
    # PATH = r'G:\quant\MaintainDB\cs_industry_new'
    # PATH = r'I:\quant\MaintainDB\cs_industry_new'

    # os.chdir(PATH)
    log_file_name = r'cs_industry.log'
    log_handler = FileHandler(log_file_name).push_application()

    engine = create_engine(r'mysql+pyodbc://quant')
    tdays = get_tdays(engine)
    # tdays = tdays[tdays > '20061231']
    for date in tdays[tdays > '20100225']:
        if date <= datetime.date.today().strftime("%Y%m%d"):
            if not check_log(date, log_file_name):
                print("***************** %s *****************" % date)

                try:
                    cs_indus(date, engine)
                    Logger().info(date + ': 1')
                except ValueError as e:
                    Logger().info(date + ': ' + str(e))
                except:
                    Logger().info(date + ': Unknow Error')
