from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, TagViewSet, CategoryViewSet, BlogPostViewSet, MacroTrendScrapViewSet, \
    Eps3yCagrViewSet, TestFinance, SltPortfolioViewSet

blogRouter = DefaultRouter()
# BLOG
blogRouter.register(r'authors', AuthorViewSet)
blogRouter.register(r'tags', TagViewSet)
blogRouter.register(r'categories', CategoryViewSet)
blogRouter.register(r'blog-posts', BlogPostViewSet)

adminRouter = DefaultRouter()
# ADMIN
adminRouter.register(r'macro-scrap', MacroTrendScrapViewSet, basename='macro_trends_scrap') # only admin
adminRouter.register(r'set-eps3y-cagr', Eps3yCagrViewSet, basename='set_eps3y_cagr')  # only admin

portfolioRouter = DefaultRouter()
# PORTFOLIO
portfolioRouter.register(r'slt', SltPortfolioViewSet, basename='slt_portfolio')  # SanlyTech, Stable Long Term

# PYTHON FOR FINANCE BOOK
portfolioRouter.register(r'test-finance', TestFinance, basename='test_finance')

urlpatterns = [
    path("blog/", include(blogRouter.urls)),
    path("admin/", include(adminRouter.urls)),
    path("portfolio/", include(portfolioRouter.urls))
]
