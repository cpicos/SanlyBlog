from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'author'
        app_label = 'core'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=35)

    class Meta:
        db_table = 'tag'
        app_label = 'core'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'category'
        app_label = 'core'

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    posted_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)
    picture = models.FileField()
    text = models.TextField()
    tags = models.ManyToManyField(Tag)
    main_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='main_category')
    related_categories = models.ManyToManyField(Category, related_name='related_categories')

    class Meta:
        db_table = 'blog_post'
        app_label = 'core'

    def __str__(self):
        return self.title


class Stock(models.Model):
    ticker = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'stock'
        app_label = 'core'

    def __str__(self):
        return self.ticker


class StockValuation(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    roe = models.FloatField(null=True)
    roi = models.FloatField(null=True)
    roa = models.FloatField(null=True)
    net_profit_margin = models.FloatField(null=True)
    gross_margin = models.FloatField(null=True)
    operating_margin = models.FloatField(null=True)
    ebitda_margin = models.FloatField(null=True)
    current_ratio = models.FloatField(null=True)
    debt_to_equity = models.FloatField(null=True)
    eps_ttm = models.FloatField(null=True)
    pe_ratio = models.FloatField(null=True)
    eps3y_cagr = models.FloatField(null=True)
    eps_start = models.FloatField(null=True)
    price = models.FloatField(null=True)

    class Meta:
        db_table = 'stock_valuation'
        app_label = 'core'

    def __str__(self):
        return self.stock.ticker

