from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ClubViewSet

router = DefaultRouter()
router.register(r'clubs', ClubViewSet, basename='clubs')

urlpatterns = [
    path('', include(router.urls)),
]

