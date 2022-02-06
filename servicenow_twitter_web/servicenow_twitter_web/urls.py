from django.urls import path, re_path, include

from twitter_client.views import redirect_user, save_access_tokens

from user.views import (
    landing, signup,
    registerServicenow,
    loginUser, logoutUser,
    dashboard
)

urlpatterns = [
    re_path(r'^$', landing),
    re_path(r'^signup/$', signup, name="signup"),
    re_path(r'^servicenow-reg/$', registerServicenow, name="servicenow-reg"),
    re_path(r'^addtwitteraccount/$', redirect_user, name="addtwitteraccount"),
    re_path(r'^addtwitteraccount/confirm/$', save_access_tokens, name="addtwitteraccount/confirm"),
    re_path(r'^login$', loginUser, name="login"),
    re_path(r'^logout$', logoutUser, name="logout"),
    re_path(r'^dashboard$', dashboard, name="dashboard"),
    re_path(r'^api/', include('api.routers'))
]
