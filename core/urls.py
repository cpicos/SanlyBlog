from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, TagViewSet, CategoryViewSet, BlogPostViewSet, MacroTrendScrapViewSet, Eps3yCagrViewSet

router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'tags', TagViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'blog-posts', BlogPostViewSet)

router.register(r'macro-scrap', MacroTrendScrapViewSet, basename='macro_trends_scrap')
router.register(r'set-eps3y-cagr', Eps3yCagrViewSet, basename='set_eps3y_cagr')

urlpatterns = [
    path("", include(router.urls))
]
