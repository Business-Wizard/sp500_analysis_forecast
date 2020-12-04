import pandas as pd
import numpy as np
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
plt.style.use('ggplot')
matplotlib.rcParams.update({'font.family' : 'sans'})
sm, med, lg = 10, 15, 20
plt.rc('font', size = sm)         # controls default text sizes
plt.rc('axes', titlesize = med)   # fontsize of the axes title
plt.rc('axes', labelsize = med)   # fontsize of the x & y labels
plt.rc('xtick', labelsize = sm)   # fontsize of the tick labels
plt.rc('ytick', labelsize = sm)   # fontsize of the tick labels
plt.rc('legend', fontsize = sm)   # legend fontsize
plt.rc('figure', titlesize = lg)  # fontsize of the figure title
plt.rc('axes', linewidth=2)       # linewidth of plot lines
import yfinance as yf
import mplfinance as mpf
from mplfinance.original_flavor import candlestick_ohlc
from scipy import stats
from datetime import *
today = date.today()
print('\n          * * * NO ISSUES - ALL IMPORTS LOADED * * * \n')


class StockForecast:    

    def __init__(self, stock, period, interval, dataname, parse_dates = True, index_col=0):
        self.stock = stock
        self.period = period
        self.interval = interval
        self.parse_dates = parse_dates
        self.index_col = index_col
        self.dataname = dataname

    def import_data(self):
        self.df = yf.download(self.stock, period = self.period, interval = self.interval, parse_dates = self.parse_dates, index_col=self.index_col)
        print('Historical Data Pulled Successfully')
        self.SaveData()
        self.GetData()
        return self.df1

    def SaveData(self):
        self.df.to_csv('data/ARIMA/' + self.dataname + '.csv')
        print('Data Saved To csv Successfully')

    def GetData(self):
        self.df1 = pd.read_csv('data/ARIMA/' + self.dataname + '.csv')
        print('Historical df Has been Imported Successfully, and is ready to be used.')
        return self.df1

    def df_top_bottom_plot(self, data_df):
        self.prices = data_df['Adj Close']
        self.volumes = data_df['Volume']
        
        # The top plot consisting of dailing closing prices
        self.top = plt.subplot2grid((4, 4), (0, 0), rowspan=3, colspan=4)
        self.top.plot(self.prices.index, self.prices, label='Adj Close')
        plt.title(f'{stock} Last Price from 2015 - 2018')
        plt.legend(loc=2)
        
        # The bottom plot consisting of daily trading volume
        self.bottom = plt.subplot2grid((4, 4), (3,0), rowspan=1, colspan=4)
        self.bottom.bar(self.volumes.index, self.volumes)
        plt.title(f'{stock} Daily Trading Volume')

        plt.gcf().set_size_inches(12, 8)
        plt.subplots_adjust(hspace=0.75)
        plt.show()

    def create_candlestick(self, start = '2019-11-01', end = '2020-11-01'):
        self.start = start
        self.end = end
        self.df_subset = yf.download(self.stock, start = self.start, end = self.end, interval = self.interval)
        self.df_subset['Date'] = self.df_subset.index.map(mdates.date2num)
        self.df_ohlc = self.df_subset[['Date','Open', 'High', 'Low', 'Close', 'Volume']]

        figure, ax = plt.subplots(figsize = (8,4), dpi = 100)
        formatter = mdates.DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        candlestick_ohlc(ax, self.df_ohlc.values, width=0.8, colorup='green', colordown='red')
        plt.show()

        self.df_ohlc['Date'] = pd.to_datetime(self.df_ohlc['Date'])
        self.df_ohlc.set_index('Date', inplace = True)
        mpf.plot(self.df_ohlc, type = 'candle', mav = (20, 50, 200), volume = True, width_adjuster_version='v0')
        plt.show()

    def plot_returns(self, fd):
        self.fd = fd
        self.daily_changes = self.fd['Adj Close'].pct_change(periods = 1)
        plt.title(f'Daily Returns {self.stock}')
        self.daily_changes.plot()
        plt.show()
        
        self.cumulative_returns = self.daily_changes.cumsum()
        self.cumulative_returns.plot()
        plt.title('Cumulative Annual Returns')
        plt.show()
        
        self.daily_changes.hist(bins=50, figsize=(8, 4))
        plt.title('Histogram Plot - Annual Returns')
        plt.show()

        self.df_vol = self.fd['Adj Close'].pct_change()
        self.df_std = self.df_vol.rolling(window=30, min_periods=30).std()
        self.df_std.plot()
        plt.title('Volatility Plot - Annual Returns')
        plt.show()
        
        self.daily_move = self.fd['Adj Close'].pct_change(periods = 1).dropna()
        figure = plt.figure(figsize = (8,4))
        ax = figure.add_subplot(111)
        stats.probplot(self.daily_move, dist = 'norm', plot = ax)
        plt.show()


if __name__ == '__main__':
    stock, dataname = '^GSPC', 'sp500_10y_1d' 
    period, interval = '10y', '1d'
    x = StockForecast(stock, period, interval, dataname)

    stock_data = x.import_data()
    stock_data = x.GetData()

    x.df_top_bottom_plot(stock_data)
    x.create_candlestick()
    x.plot_returns(stock_data)
