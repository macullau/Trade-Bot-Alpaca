import numpy as np
from scipy.signal import argrelextrema
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict


def get_max_min(prices, smoothing, window_range):
    """
    Function to find extreme points of data.
    :param prices: Dataset to find extreme points of. Must be pandas dataframe.
    :param smoothing: Parameter to determine how much we blend, or "smooth out", the data.
    :param window_range: Parameter that determines interval between extreme points.
    :return: Pandas dataframe with date and price of extreme points in prices.
    """
    smooth_prices = prices['close'].rolling(window=smoothing).mean().dropna()
    local_max = argrelextrema(smooth_prices.values, np.greater)[0]
    local_min = argrelextrema(smooth_prices.values, np.less)[0]
    price_local_max_dt = []
    for i in local_max:
        if (i > window_range) and (i < len(prices) - window_range):
            price_local_max_dt.append(prices.iloc[i - window_range:i + window_range]['close'].idxmax())
    price_local_min_dt = []
    for i in local_min:
        if (i > window_range) and (i < len(prices) - window_range):
            price_local_min_dt.append(prices.iloc[i - window_range:i + window_range]['close'].idxmin())
    maxima = pd.DataFrame(prices.loc[price_local_max_dt])
    minima = pd.DataFrame(prices.loc[price_local_min_dt])
    max_min = pd.concat([maxima, minima]).sort_index()
    max_min = max_min.reset_index()
    max_min = max_min[~max_min.timestamp.duplicated()]
    p = prices.reset_index()
    max_min['day_num'] = p[p['timestamp'].isin(max_min.timestamp)].index.values
    max_min = max_min.set_index('day_num')['close']

    return max_min


def find_patterns(max_min,win=5,n=100):
    patterns = defaultdict(list)

    # Window range is 5 units
    for i in range(win, len(max_min)):
        window = max_min.iloc[i - win:i]

        # Pattern must play out in less than n units
        if window.index[-1] - window.index[0] > n:
            continue

        a, b, c, d, e = window.iloc[0:5]

        # IHS
        if a < b and c < a and c < e and c < d and e < d and abs(b - d) <= np.mean([b, d]) * 0.02:
            patterns['IHS'].append((window.index[0], window.index[-1]))

    return patterns


if __name__ == "__main__":
    smoothing = 2
    window = 3
    resampled_data=pd.read_csv('AAPL_resampled_data.csv')
    minmax1 = get_max_min(resampled_data, smoothing, window)
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    resampled_data.reset_index()['close'].plot()
    plt.scatter(minmax1.index,minmax1.values,color='red',alpha=0.5,marker='x')
    fig.suptitle('Pattern Points')
    plt.title("Price over Time")
    plt.xlabel('Hours (indx)')
    plt.ylabel('Price (USD)')
    patterns = find_patterns(minmax1)
    print(patterns['IHS'])
    ax2 = fig.add_subplot(212)
    resampled_data.reset_index()['close'].plot()
    pts = patterns['IHS']
    for element in pts:
        x=[i for i in range(element[0],element[1]+1)]
        y=np.array(resampled_data.reset_index()['close'])[x]
        plt.scatter(x,y,alpha=0.5,marker='x')
    plt.show()
