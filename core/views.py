from rest_framework import viewsets
from rest_framework.response import Response
import bs4 as bs
import urllib.request
from .serializers import AuthorSerializer, TagSerializer, CategorySerializer, BlogPostSerializer, StockSerializer
from .models import Author, Tag, Category, BlogPost, Stock, StockRevenues, StockEbitda, StockEps


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

    def revenues(self, ticker):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/revenue'.format(ticker)
        sauce = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
        div = soup.find(id="style-1")
        revenues_tables = div.find_all("table")
        annual = revenues_tables[0]
        result = []
        for tr in annual.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) > 1:
                year = tds[0]
                revenues = tds[1]
                revenues = revenues.get_text().replace('$', '')
                revenues = revenues.replace(',', '')
                if len(revenues) > 0:
                    result.append({'ticker': ticker, 'date': int(year.get_text()), 'revenues': int(revenues)})
        return result

    def ebitda(self, ticker):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/ebitda'.format(ticker)
        sauce = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
        div = soup.find(id="style-1")
        revenues_tables = div.find_all("table")
        annual = revenues_tables[0]
        result = []

        for tr in annual.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) > 1:
                year = tds[0]
                revenues = tds[1]
                revenues = revenues.get_text().replace('$', '')
                revenues = revenues.replace(',', '')
                if len(revenues) > 0:
                    result.append({'ticker': ticker, 'date': int(year.get_text()), 'ebitda': int(revenues)})
        return result

    def eps(self, ticker):
        url = 'https://www.macrotrends.net/stocks/charts/{}/x/eps-earnings-per-share-diluted'.format(ticker)
        sauce = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
        div = soup.find(id="style-1")
        revenues_tables = div.find_all("table")
        annual = revenues_tables[0]
        quarter = revenues_tables[1]
        result = []

        for tr in quarter.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) > 1:
                year = tds[0]
                eps = tds[1]
                eps = eps.get_text().replace('$', '')
                eps = eps.replace(',', '')
                if len(eps) > 0:
                    result.append({'ticker': ticker, 'date': year.get_text(), 'eps': float(eps)})
        return result

    def list(self, request):
        result = []
        stocks = Stock.objects.all()
        print('scrap!!!')
        for stock in stocks:
            print(stock)
            revenues = self.revenues(stock)
            ebitda = self.ebitda(stock)
            eps = self.eps(stock)

            revenues_list = []
            ebitda_list = []
            eps_list = []

            for x in revenues:
                revenues_list.append(StockRevenues(stock=stock, year=x['date'], value=x['revenues']))
            # StockRevenues.objects.bulk_create(revenues_list)

            for x in ebitda:
                ebitda_list.append(StockEbitda(stock=stock, year=x['date'], value=x['ebitda']))
            # StockEbitda.objects.bulk_create(ebitda_list)

            for x in eps:
                eps_list.append(StockEps(stock=stock, date=x['date'], value=x['eps']))
            # StockEps.objects.bulk_create(eps_list)

        return Response(result)


class StockFairValueViewSet(viewsets.ViewSet):
    def list(self, request):
        serializer = StockSerializer(Stock.objects.all(), many=True)
        return Response(serializer.data)
