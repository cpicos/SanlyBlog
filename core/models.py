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
    ticker = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'stock'
        app_label = 'core'

    def __str__(self):
        return self.ticker


class StockRevenues(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField()
    value = models.IntegerField()

    class Meta:
        db_table = 'revenue'
        app_label = 'core'

    def __str__(self):
        return '% % %'.format(self.ticker, self.year, self.value)


class StockEbitda(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField()
    value = models.IntegerField()

    class Meta:
        db_table = 'ebitda'
        app_label = 'core'

    def __str__(self):
        return '% % %'.format(self.stock, self.year, self.value)


class StockEps(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    value = models.FloatField()

    class Meta:
        db_table = 'eps'
        app_label = 'core'

    def __str__(self):
        return '% % %'.format(self.ticker, str(self.date), self.value)
