from django.urls import re_path
from . import views

urlpatterns = [
    re_path('events', views.Events.as_view()),
    re_path('activity', views.TwitterActivity.as_view())
]
