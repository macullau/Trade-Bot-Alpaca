import datetime
import pytz
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

client = StockHistoricalDataClient(api_key='PKJ7TUUMCUZ7PDY2PRTJ',
                                   secret_key='jfFmk7yr6OdfeM5Px2CoYtcQxx6BQvJ7H2h52f1L')


def get_date(UTC,day=30):
    """
    Function to get date x days into the past. Standard is 30 days back
    :param day: How many days into the past you want to find the date of.
    :return: String object containing the date x days from the present.
    """
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    if UTC:
        utc_ret = utc_now - datetime.timedelta(days=day)
        return utc_ret #.strftime("%Y-%m-%d")
    else:
        est_now = utc_now.astimezone(pytz.timezone("US/Eastern"))
        est_ret = est_now - datetime.timedelta(days=day)
        return est_ret #.strftime("%Y-%m-%d")


def get_data(symbol, lookback):
    request_params = StockBarsRequest(
        symbol_or_symbols=str(symbol),
        timeframe=TimeFrame.Hour,
        start=get_date(True)
    )
    all_data = client.get_stock_bars(request_params).df
    all_data.drop(columns=['volume'], inplace=True)
    all_data.dropna(inplace=True)
    all_data = all_data[~all_data.index.duplicated()]
    all_data.replace(0, method='bfill', inplace=True)
    all_data.reset_index(level=['symbol'], inplace=True)
    return all_data


data = get_data('AAPL', 50)
data.to_csv('AAPL_data.csv')

resampled_data = data.resample('30T', closed='right', label='right').agg({'open': 'first',
                                                                         'high': 'max',
                                                                         'low': 'min',
                                                                         'close': 'last'}).dropna()
resampled_data.to_csv('AAPL_resampled_data.csv')