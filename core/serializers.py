from rest_framework import serializers
import bs4 as bs
import urllib.request
from .models import Author, Tag, Category, BlogPost, Stock, StockEbitda, StockRevenues, StockEps


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ('id', 'title')


class StockSerializer(serializers.ModelSerializer):
    # ebitda = serializers.SerializerMethodField()
    # revenue = serializers.SerializerMethodField()
    # data = serializers.SerializerMethodField()
    # eps_ttm = serializers.SerializerMethodField()
    # growth_rate = serializers.SerializerMethodField()
    fair_margin = serializers.SerializerMethodField()
    yahoo_link = serializers.SerializerMethodField()
    finviz_link = serializers.SerializerMethodField()
    etoro_link = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = ('ticker', 'fair_margin', 'yahoo_link', 'finviz_link', 'etoro_link')

    def get_ebitda(self, obj):
        return StockEbitda.objects.filter(stock=obj)

    def get_revenue(self, obj):
        return StockRevenues.objects.filter(stock=obj)

    def get_data(self, obj):
        result = []
        years = self.get_ebitda(obj).values_list('year', flat=True)
        sum_growth_rate = 0
        x = 0
        for year in years:
            try:
                ebitda = self.get_ebitda(obj).get(year=year)
                revenue = self.get_revenue(obj).get(year=year)
                growth_rate = ebitda.value/revenue.value
                if x < 5:
                    sum_growth_rate += growth_rate
                x += 1
                result.append({'year': year,
                               'info':
                                   {
                                       'ebitda': ebitda.value,
                                       'revenue': revenue.value,
                                       'growth_rate': round(growth_rate * 100, 2)
                                   }
                               })
            except Exception as err:
                print(err)
                print(obj, year)

        avg_growth_rate = round((sum_growth_rate/5) * 100, 2)
        if avg_growth_rate > 25:
            avg_growth_rate = 25
        return result, avg_growth_rate

    def get_eps_ttm(self, obj):
        result = 0
        for eps in StockEps.objects.filter(stock=obj).values('date', 'value')[:4]:
            result += eps.get('value', 0)
        return round(result, 2)

    def get_growth_rate(self, obj):
        data, growth = self.get_data(obj)
        return growth

    def get_fair_margin(self, obj):
        growth_rate = self.get_growth_rate(obj)
        eps_ttm = self.get_eps_ttm(obj)
        fair_value = eps_ttm * growth_rate
        margin_of_safety = fair_value - (fair_value * 0.30)
        prev_close = self.get_prev_close(obj)
        if prev_close < margin_of_safety:
            status = 'Undervalued'
        elif margin_of_safety < prev_close < fair_value:
            status = 'CHECK_THIS'
        else:
            status = 'Overvalued'

        result = {'fair_value': round(fair_value, 2), 'margin_of_safety': round(margin_of_safety, 2),
                  'growth_rate': growth_rate, 'eps_ttm': eps_ttm, 'prev_close': prev_close, 'status': status}
        return result

    def get_yahoo_link(self, obj):
        return 'https://finance.yahoo.com/quote/{}'.format(obj.ticker)

    def get_finviz_link(self, obj):
        return 'https://www.finviz.com/screener.ashx?v=161&t={}'.format(obj.ticker)

    def get_etoro_link(self, obj):
        return 'https://www.etoro.com/markets/{}'.format(obj.ticker)

    def get_prev_close(self, obj):
        url = 'https://finance.yahoo.com/quote/{}/history?p={}'.format(obj.ticker, obj.ticker)
        print(url)
        sauce = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
        table = soup.find('tbody')
        trs = table.find_all('tr')
        tds = trs[0].find_all('td')
        span = tds[5].find('span')
        span = span.get_text()
        span = span.replace(',', '')
        previous_close = float(span)
        return round(previous_close, 2)

