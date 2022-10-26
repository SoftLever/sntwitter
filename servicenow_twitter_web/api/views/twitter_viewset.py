from api.permissions import IsAdminOrIsObjectOwner
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status


from user.models import Twitter
from api.serializers import TwitterSerializer


class TwitterViewSet(viewsets.ModelViewSet):
    def list(self, request):
        try:
            queryset = Twitter.objects.get(user=request.user)
            serializer = self.get_serializer(self.queryset)
        except Twitter.DoesNotExist:
            return Response({"message": "No Twitter integration record found"}, status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status.HTTP_200_OK)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsAdminOrIsObjectOwner]
        return [permission() for permission in permission_classes]

    def get_serializer(self, *args, **kwargs):
        return TwitterSerializer(*args, **kwargs)
