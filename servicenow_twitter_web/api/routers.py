from django.urls import re_path
from rest_framework.routers import DefaultRouter
from .views import (
    TwitterActivity, Events, ServicenowViewSet,
    GetUrl, Subscribe, Unsubscribe,
    TwitterViewSet,
)

router = DefaultRouter()
router.register(r'^servicenow-details', ServicenowViewSet, basename='servicenow-details')
router.register(r'^twitter-details', TwitterViewSet, basename='twitter-details')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^events', Events.as_view()),
    re_path(r'^activity', TwitterActivity.as_view()),
    re_path(r'^get-auth-url', GetUrl.as_view()),
    re_path(r'^twitter-auth', Subscribe.as_view()),
    re_path(r'^twitter-revoke', Unsubscribe.as_view())
]
