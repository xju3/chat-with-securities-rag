import akshare as ak
from data.engine import get_engine
from data.model import SecInfo, TransItem, SecMa
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from datetime import datetime

_engine = get_engine()
_session = Session(_engine)

from datetime import date
import pandas as pd

_start_date = pd.to_datetime(date.today(), format="%Y-%m-%d") - pd.DateOffset(months=3)
_end_date = date.today()


def clean_trans_history():
    '''
        delete transaction records which the date before 3 months ago
    '''
    stmp = select(TransItem.__table__).where(TransItem.date < _start_date)
    _session.delete(stmp)


def ma_calculation():
    '''
        calculate moving average value for each security
    '''
    idx = 0
    securities = _session.execute(select(SecInfo.__table__)).mappings().all()
    list = []
    for row in securities:
        code = row.code
        print(f'{idx}: {code}')
        ma = _session.execute(select(SecMa).where(SecMa.code == code)).one_or_none()
        hit = False
        if ma is None:
            ma = SecMa(code = code)
            hit = True
        transactions = _session.execute(select(TransItem.__table__).where(TransItem.code == code).order_by(desc(TransItem.date))).mappings().all()
        ma.ma5 = _calc_ma(transactions, 5)
        ma.ma10 = _calc_ma(transactions, 10)
        ma.ma15 = _calc_ma(transactions, 15)
        ma.ma20 = _calc_ma(transactions, 20)
        ma.ma30 = _calc_ma(transactions, 30)
        ma.ma60 = _calc_ma(transactions, 60)

        if hit:
            list.append(ma)
    
    if len(list) > 0:
        _session.add_all(list)
    _session.commit()

def _calc_ma(transactions:list,  days: int) -> float:
    if len(transactions) < days:
        days = len(transactions)

    total = 0.0
    for i in range(days):
        total += transactions[i].close
    return total / days


def fetch_stock_list():
    '''
        get stock list, if exists then skip.
    '''
    df = ak.stock_info_a_code_name()
    new_item_list = []
    for index, row in df.iterrows():
        code = row['code']
        name = row['name']
        result  = _session.execute(select(SecInfo).where(SecInfo.code == code))
        if result is None or len(result.all()) == 0:
            inst = SecInfo(code = code, name = name)
            new_item_list.append(inst)

    print(len(new_item_list))
    if len(new_item_list) == 0:
        return

    _session.add_all(new_item_list)
    _session.commit()

def fetch_trans_items(start_date:datetime = None, end_date:datetime = None):
    '''
        fetching daily transaction records of all securities with the specify date range (start_date, end_date)
    '''
    result  = _session.execute(select(SecInfo))
    all = result.scalars().all()
    print(len(all))
    if start_date is None:
        start_date = _start_date
    
    if end_date is None:
        end_date = _end_date

    for sec in all:
        _fetch_trans_items(sec.code, start_date, end_date)


def _fetch_trans_items(sec_code: str, start_date:datetime, end_date: datetime):
    '''
        - for each security.
    '''
    df = ak.stock_zh_a_hist(symbol=f"{sec_code}", 
                            period="daily", 
                            start_date=f'{start_date:%Y%m%d}', 
                            end_date=f'{end_date:%Y%m%d}', adjust="")
    df = df.reset_index()

    list = []
    for _, row in df.iterrows():

        code = row['股票代码']
        date = row['日期']
        if _check_daily_trans_exists(sec_code=code, trans_date=date):
            continue
        
        open = row['开盘']
        close = row['收盘']
        high = row['最高']
        low = row['最低']
        qty = row['成交量']
        amt = row['成交额']
        fluc = row['振幅']
        pct = row['涨跌幅']
        delta = row['涨跌额']
        rate = row['换手率']

        daily_trans = TransItem(code = code, date = date, open = open, close = close,
                                 high = high, low = low, qty = qty, amt = amt, fluc = fluc, pct =pct, delta = delta, rate = rate)
        
        list.append(daily_trans)
    
    if len(list) == 0:
        return
    print(f'{sec_code}: {len(list)}')

    '''
        update curr price which stored in sec_ma table.
    '''
    if start_date == end_date and len(list) == 1:
        ma = _session.execute(select(SecMa.__table__).where(SecMa.code == sec_code)).one_or_none
        if ma is not None:
            ma.curr = list[0].close
    _session.add_all(list)
    _session.commit()

def _check_daily_trans_exists(sec_code, trans_date):
    '''
        # to ensure there is no duplicate daily transaction records.
        # to reduce the db access time, we can store an unique key in redis database.
    '''
    result = _session.execute(select(TransItem).where(TransItem.date == f'{trans_date:%Y-%m-%d}'))
    if result is None or len(result.all()) == 0:
        return False;
    return True