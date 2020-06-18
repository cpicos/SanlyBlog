from warnings import catch_warnings

from rest_framework import viewsets
from rest_framework.response import Response
from django.views.generic import TemplateView
import bs4 as bs
import urllib.request
from itertools import groupby
from dateutil.relativedelta import relativedelta
import math
from .serializers import AuthorSerializer, TagSerializer, CategorySerializer, BlogPostSerializer
from .models import Author, Tag, Category, BlogPost, Stock, StockValuation


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


# class StockFairValueViewSet(viewsets.ViewSet):
#     def list(self, request):
#         serializer = StockSerializer(Stock.objects.all(), many=True)
#         return Response(serializer.data)

class GenerateScrap(TemplateView):
    template_name = "generate_scrap.html"
