from api.permissions import IsAdminOrIsObjectOwner
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action


from user.models import Twitter
from api.serializers import TwitterSerializer


class TwitterViewSet(viewsets.ModelViewSet):

    queryset = Twitter.objects.all()

    def list(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        sn = self.get_object()
        serializer = self.get_serializer(sn)

        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsAdminOrIsObjectOwner]
        return [permission() for permission in permission_classes]

    def get_serializer(self, *args, **kwargs):
        return TwitterSerializer(*args, **kwargs)
