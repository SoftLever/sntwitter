from django.urls import path, re_path, include

from twitter_client.views import redirect_user, save_access_tokens

from user.views import registerServicenow

urlpatterns = [
    # re_path(r'^servicenow-reg/$', registerServicenow, name="servicenow-reg"),
    # re_path(r'^addtwitteraccount/$', redirect_user, name="addtwitteraccount"),
    # re_path(r'^addtwitteraccount/confirm/$', save_access_tokens, name="addtwitteraccount/confirm"),
    re_path(r'auth/', include('user.urls')),
    re_path(r'^api/', include('api.routers'))
]
