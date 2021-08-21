from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from app_manager import views

router = DefaultRouter(trailing_slash=False)

router.register('admin-management',views.AdminManagementViewSet, basename='admin-management')
urlpatterns = router.urls