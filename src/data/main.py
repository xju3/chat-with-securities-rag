
import sys
from datetime import date
import pandas as pd
from dateutil.relativedelta import relativedelta

from data.security import fetch_trans_items, fetch_stock_list, ma_calculation, clean_trans_history

from data.engine import get_engine
from data.model import SecInfo, TransItem, SecMa
from sqlalchemy import select, desc
from sqlalchemy.orm import Session


start_date = pd.to_datetime(date.today(), format="%Y-%m-%d") - pd.DateOffset(months=3)
end_date = date.today()

engine = get_engine()
session = Session(engine)

def init():
    """
        initialize database, including securities, daily transaction with past three months.
    """
    print(start_date)
    fetch_trans_items()

def daily():
    """
        update stock every day
    """
    fetch_stock_list()
    fetch_trans_items(date.today, date.today)
    ma_calculation()
    clean_trans_history()




if __name__ == '__main__':
    """
        if there is no parameters entered, run daily() else run init()
    """
    parameters = sys.argv[1:] 

    if len(parameters) == 0:
        daily()
    else:
        init()

