from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, TagViewSet, CategoryViewSet, BlogPostViewSet, MacroTrendScrapViewSet

router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'tags', TagViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'blog-posts', BlogPostViewSet)

router.register(r'macro-scrap', MacroTrendScrapViewSet, basename='macro_trends_scrap')
# router.register(r'fair-value', StockFairValueViewSet, basename='stock_fair_value')

urlpatterns = [
    path("", include(router.urls))
]
