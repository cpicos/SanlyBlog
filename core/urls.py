from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, TagViewSet, CategoryViewSet, BlogPostViewSet

router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'tags', TagViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'blog-posts', BlogPostViewSet)

urlpatterns = [
    path("", include(router.urls))
]
