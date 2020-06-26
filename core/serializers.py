from rest_framework import serializers
import bs4 as bs
import urllib.request
from .models import Author, Tag, Category, BlogPost, Stock, StockValuation


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
    class Meta:
        model = Stock
        fields = ('ticker', )


class StockValuationSerializer(serializers.ModelSerializer):
    ticker = serializers.SerializerMethodField()
    value_price = serializers.SerializerMethodField()
    mof = serializers.SerializerMethodField()

    class Meta:
        """
        eps_ttm Twelve Trailing Months
        eps_start Eps 3 years before
        """
        model = StockValuation
        fields = ('ticker', 'date', 'price', 'value_price', 'mof', 'pe_ratio', 'eps_ttm', 'eps_start', 'eps3y_cagr',
                  'roe', 'roi', 'roa',
                  'gross_margin', 'net_profit_margin', 'ebitda_margin', 'current_ratio', 'debt_to_equity',)

    @staticmethod
    def get_ticker(obj):
        return obj.stock.ticker

    @staticmethod
    def get_value_price(obj):
        if obj.eps3y_cagr:
            if obj.eps3y_cagr > 25:
                result = obj.eps_ttm * 25
            else:
                result = obj.eps_ttm * obj.eps3y_cagr
        else:
            result = None
        return result

    def get_mof(self, obj):
        result = 0.00
        if obj.price and self.get_value_price(obj):
            result = ((self.get_value_price(obj) / obj.price) - 1) * 100

        return result
