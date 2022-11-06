from django.urls import re_path
from rest_framework.routers import DefaultRouter
from .views import (
    TwitterActivity, Events, ServicenowViewSet,
    GetUrl, Subscribe, Unsubscribe,
    TwitterViewSet, CustomFieldViewSet,
    TwittnowApiKeyViewSet,
    DialogFlowFulfillment
)

router = DefaultRouter()
router.register(r'^servicenow-details', ServicenowViewSet, basename='servicenow-details')
router.register(r'^twitter-details', TwitterViewSet, basename='twitter-details')
router.register(r'^custom-fields', CustomFieldViewSet, basename='custom-fields')
router.register(r'^api-key', TwittnowApiKeyViewSet, basename='api-key')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^events', Events.as_view()),
    re_path(r'^twitter-activity', TwitterActivity.as_view()),
    re_path(r'^get-auth-url', GetUrl.as_view()),
    re_path(r'^twitter-auth', Subscribe.as_view()),
    re_path(r'^twitter-revoke', Unsubscribe.as_view()),
    re_path(r'^dialogflow', DialogFlowFulfillment.as_view())
]
