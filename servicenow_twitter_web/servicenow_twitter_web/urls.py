from django.urls import path, re_path, include

urlpatterns = [
    re_path(r'^auth/', include('user.urls')),
    re_path(r'', include('api.routers'))
]
