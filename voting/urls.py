from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from voting import views

router = DefaultRouter(trailing_slash=False)

router.register('voting',views.VotingViewSet, basename='voting')
# router.register('evaluation',views.EvaluationViewSet, basename='evaluation')
urlpatterns = router.urls