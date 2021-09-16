
from analytics import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter(trailing_slash=False)
router.register('analytics',
                views.AnalyticsViewSet, basename='analytics')

urlpatterns = router.urls
