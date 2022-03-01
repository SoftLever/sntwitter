from api.permissions import IsAdminOrIsObjectOwner
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action


from user.models import Servicenow
from api.serializers import ServicenowSerializer


class ServicenowViewSet(viewsets.ModelViewSet):

    queryset = Servicenow.objects.all()

    def list(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        sn = self.get_object()
        serializer = self.get_serializer(sn)

        return Response(serializer.data)

    def create(self, request):
        data = request.data
        if isinstance(data, list):
            return Response({"message": "Can only add one instancer per user"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Non-admin users don't have to pass the user
            # attribute. Whether they do or don't, the value
            # will be determined by their credentials
            if not request.user.is_staff:
                data["user"] = request.user.id

            serializer = self.get_serializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        sn = self.get_object()
        data = request.data

        # Disallow updating of the user associated with the record
        data.pop("user")
        serializer = self.get_serializer(sn, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        sn = self.get_object()
        sn.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsAdminOrIsObjectOwner]
        return [permission() for permission in permission_classes]

    def get_serializer(self, *args, **kwargs):
        return ServicenowSerializer(*args, **kwargs)
