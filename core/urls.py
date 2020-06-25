from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, TagViewSet, CategoryViewSet, BlogPostViewSet, MacroTrendScrapViewSet, \
    Eps3yCagrViewSet, TestFinance, SltPortfolioViewSet

router = DefaultRouter()
# BLOG
router.register(r'authors', AuthorViewSet)
router.register(r'tags', TagViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'blog-posts', BlogPostViewSet)

# ADMIN
router.register(r'macro-scrap', MacroTrendScrapViewSet, basename='macro_trends_scrap') # only admin
router.register(r'set-eps3y-cagr', Eps3yCagrViewSet, basename='set_eps3y_cagr')  # only admin

# PORTFOLIO
router.register(r'slt-portfolio', SltPortfolioViewSet, basename='slt_portfolio')  # SanlyTech, Stable Long Term

# PYTHON FOR FINANCE BOOK
router.register(r'test-finance', TestFinance, basename='test_finance')

urlpatterns = [
    path("", include(router.urls))
]
