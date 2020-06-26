from warnings import catch_warnings

from rest_framework import viewsets
from rest_framework.response import Response
from django.views.generic import TemplateView
import bs4 as bs
import urllib.request
from itertools import groupby
from dateutil.relativedelta import relativedelta
import math
from .serializers import AuthorSerializer, TagSerializer, CategorySerializer, BlogPostSerializer, \
    StockValuationSerializer
from .models import Author, Tag, Category, BlogPost, Stock, StockValuation
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib as mpl
import matplotlib.pyplot as plt
import time
from datetime import datetime
import json


class AuthorViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class BlogPostViewSet(viewsets.ModelViewSet):
    serializer_class = BlogPostSerializer
    queryset = BlogPost.objects.all()


class MacroTrendScrapViewSet(viewsets.ViewSet):

    @staticmethod
    def _scrap_margins(url, margin_type):
        result = []
        sauce = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
        div = soup.find(id="style-1")
        revenues_tables = div.find_all("table")
        data = revenues_tables[0]

        for tr in data.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) > 1:
                date = tds[0]
                x = tds[2]
                x = x.get_text()
                if len(x) > 0:
                    margin = tds[3]
                    margin = margin.get_text().replace('%', '')
                    if len(margin) > 0:
                        if margin_type == 'eps_ttm':
                            x = x.replace('$', '')
                            x = x.replace(',', '')
                            result.append({'date': date.get_text(), margin_type: x})
                        elif margin_type == 'price':
                            price = tds[1]
                            price = price.get_text().replace('$', '')
                            price = price.replace(',', '')
                            result.append({'date': date.get_text(), margin_type: price})
                        else:
                            result.append({'date': date.get_text(), margin_type: margin})
        return result

    @staticmethod
    def _scrap_eps(url):
        result = []
        sauce = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
        div = soup.find(id="style-1")
        table = div.find_all("table")
        data = table[1]

        for tr in data.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) > 1:
                date = tds[0]
                margin = tds[1]
                margin = margin.get_text().replace('$', '')
                margin = margin.replace(',', '')
                if len(margin) > 0:
                    result.append({'date': date.get_text(), 'eps': margin})
        return result

    def roe(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/roe'.format(stock)
        return self._scrap_margins(url, 'roe')

    def roi(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/roi'.format(stock)
        return self._scrap_margins(url, 'roi')

    def roa(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/roa'.format(stock)
        return self._scrap_margins(url, 'roa')

    def net_profit_margin(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/net-profit-margin'.format(stock)
        return self._scrap_margins(url, 'net_profit_margin')

    def gross_margin(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/gross-margin'.format(stock)
        return self._scrap_margins(url, 'gross_margin')

    def operating_margin(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/operating-margin'.format(stock)
        return self._scrap_margins(url, 'operating_margin')

    def ebitda_margin(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/ebitda-margin'.format(stock)
        return self._scrap_margins(url, 'ebitda_margin')

    def current_ratio(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/current-ratio'.format(stock)
        return self._scrap_margins(url, 'current_ratio')

    def debt_to_equity(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/debt-equity-ratio'.format(stock)
        return self._scrap_margins(url, 'debt_to_equity')

    def pe_ratio(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/pe-ratio'.format(stock)
        return self._scrap_margins(url, 'pe_ratio')

    def eps_ttm(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/pe-ratio'.format(stock)
        return self._scrap_margins(url, 'eps_ttm')

    def eps(self, stock):

        url = 'https://www.macrotrends.net/stocks/charts/{}/x/eps-earnings-per-share-diluted'.format(stock)
        return self._scrap_eps(url)

    def price(self, stock):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/pe-ratio'.format(stock)
        return self._scrap_margins(url, 'price')

    def list(self, request):
        result = []
        start = int(request.GET.get('start', 0))
        end = int(request.GET.get('end', 0))
        stocks = Stock.objects.all()[start:end]
        for stock in stocks:
            print(stock)
            roe_data = self.roe(stock)
            roi_data = self.roi(stock)
            roa_data = self.roa(stock)
            net_profit_margin = self.net_profit_margin(stock)
            gross_margin = self.gross_margin(stock)
            operating_margin = self.operating_margin(stock)
            ebitda_margin = self.ebitda_margin(stock)
            current_ratio = self.current_ratio(stock)
            debt_to_equity = self.debt_to_equity(stock)
            pe_ratio = self.pe_ratio(stock)
            eps_ttm = self.eps_ttm(stock)
            price = self.price(stock)

            lst = roe_data + roi_data + roa_data + current_ratio + net_profit_margin + debt_to_equity + gross_margin \
                + operating_margin + ebitda_margin + pe_ratio + eps_ttm + price
            lst.sort(key=lambda d: d['date'])

            lines = []

            for k, v in groupby(lst, key=lambda x: x['date']):
                res_dict = {'stock_id': stock.id, 'date': k}
                for d in v:
                    t = list(d.items())[1]
                    if t[1] in ('inf', 'nan'):
                        print('IGNORE')
                    else:
                        res_dict[t[0]] = t[1]

                lines.append(StockValuation(**res_dict))

            StockValuation.objects.bulk_create(lines)
        return Response(result)


class Eps3yCagrViewSet(viewsets.ViewSet):

    def list(self, request):
        result = []
        stocks = Stock.objects.all()
        for stock in stocks:
            # try:
            valuation = StockValuation.objects.filter(stock_id=stock.id, eps_ttm__gt=0).order_by('-date')
            dates_eps = valuation.values('id', 'date', 'eps_ttm')
            for data in dates_eps:
                mrqrtr = data.get('date')  # most recent quarter
                start_period_date = mrqrtr - relativedelta(months=33)  # last 12 quarters, 11 prev + 1 current
                end_eps = data.get('eps_ttm')
                if valuation.filter(date=start_period_date, eps_ttm__gt=0).exists():
                    start_eps = valuation.get(date=start_period_date).eps_ttm
                    cagr = (math.pow(end_eps / start_eps, 1 / 3) - 1) * 100
                else:
                    start_eps = None
                    cagr = None

                x = StockValuation.objects.get(id=data.get('id'))
                x.eps3y_cagr = cagr
                x.eps_start = start_eps
                x.save()
                print(stock)
        return Response(result)


class SltPortfolioViewSet(viewsets.ViewSet):
    def list(self, request):
        start = datetime.now()
        # stocks = StockValuation.objects.filter(roe__gte=15, roi__gte=10, roa__gte=5, net_profit_margin__gte=10,
        #                                        current_ratio__gte=1.2, pe_ratio__lte=25)\
        #          .order_by('stock__ticker', 'date')
        stocks = StockValuation.objects.all().values('stock__ticker', 'date', 'roe', 'roi', 'roa', 'net_profit_margin',
                                                     'gross_margin', 'operating_margin', 'ebitda_margin',
                                                     'current_ratio', 'debt_to_equity', 'eps_ttm', 'pe_ratio',
                                                     'eps3y_cagr', 'eps_start', 'price')
        df = pd.DataFrame(stocks)
        # CONDITIONS, FILTERS df[df['columns'] = condition ]
        df_gt25 = df[df['eps3y_cagr'] > 25]
        df_gt25['value_price'] = round(df_gt25['eps_ttm'] * 25, 2)

        df_lt25 = df[df['eps3y_cagr'] <= 25]
        df_lt25['value_price'] = round(df_lt25['eps_ttm'] * df_lt25['eps3y_cagr'], 2)

        # MERGE FRAMES
        frames = [df_gt25, df_lt25]
        result = pd.concat(frames)
        result['mof'] = round(((result['value_price'] / result['price']) - 1) * 100, 2)
        result['eps3y_cagr'] = round(result['eps3y_cagr'])

        # Convert pandas date
        result["date"] = pd.to_datetime(result["date"]).dt.strftime("%Y-%m-%d")

        # VALUATION FILTER
        result = result[result['pe_ratio'] < result['eps3y_cagr']]

        # result.to_csv(r'C:\Users\Omar\Desktop\SLTPortFolio.csv', index=False)
        # rule sell after 1 year holding for the last positition

        # FUNCTIONS
        print(result.describe())
        end = datetime.now()
        print('ELAPSED TIME', end - start)
        out = result.to_json(orient='records')
        return Response([])


class GenerateScrap(TemplateView):
    template_name = "generate_scrap.html"


class TestFinance(viewsets.ViewSet):

    def list(self, request):
        result = []
        # tickers = Stock.objects.all().values_list('ticker', flat=True)[:5]
        # start = '2000-01-01'
        # end = '2020-12-31'
        # df = pd.concat([web.DataReader('BIIB', 'yahoo', start, end) for ticker in tickers]).reset_index()
        # print(df)
        # https://www.nasdaq.com/market-activity/stocks/screener?exchange=nasdaq&letter=0&render=download
        # https://www.nasdaq.com/market-activity/stocks/screener?exchange=nyse&letter=0&render=download
        # ftp://ftp.nasdaqtrader.com/symboldirectory
        # https://pypi.org/project/Yahoo-ticker-downloader/

        # df = pd.concat([web.DataReader(ticker,'morningstar', start, end) for ticker in tickers]).reset_index()
        # ts_log = np.round(sp500['Close'])
        # sp500['42d'] = ts_log.rolling(42).mean()
        # sp500['252d'] = ts_log.rolling(252).mean()
        # sp500['42d-252d'] = sp500['42d'] - sp500['252d']

        # GOOD ONLY FOR INDEXES
        # SD = 50
        # sp500['Regime'] = np.where(sp500['42d-252d'] > SD, 1, 0)
        # sp500['Regime'] = np.where(sp500['42d-252d'] < SD, -1, sp500['Regime'])
        # sp500['Regime'].value_counts()
        # sp500['Market'] = np.log(sp500['Close'] / sp500['Close'].shift(1))
        # sp500['Strategy'] = sp500['Regime'].shift(1) * sp500['Market']
        #
        i = 0
        for stock in Stock.objects.all().values_list('ticker', flat=True):
            if stock not in ['BHGE']:
                try:
                    sp500 = web.DataReader(stock, data_source='yahoo', start='2000-01-01', end='2020-12-31')
                    sp500['Symbol'] = stock
                    # print(stock)
                    # print(sp500[['Adj Close', 'Close', 'Symbol']])
                except Exception as err:
                    print(stock, err)
            i += 1
            if i == 30:
                time.sleep(30)
                i = 0
        print('END !!!!!')
        return Response(result)
