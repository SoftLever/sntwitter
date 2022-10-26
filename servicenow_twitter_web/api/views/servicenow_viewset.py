from api.permissions import IsAdminOrIsObjectOwner
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status


from user.models import Servicenow, CustomFields
from api.serializers import ServicenowSerializer, CustomFieldSerializer

from knox.models import AuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer


class TwittnowApiKeyViewSet(viewsets.ModelViewSet):
    def create(self, request):
        # This endpoint is used for both creation of new tokens and regeneration
        # We'll start by deleting any existing non-expiring token for the requesting user
        AuthToken.objects.filter(user=request.user, expiry=None,).delete()
        # Then we'll create a new token with no expiry
        token = AuthToken.objects.create(user=request.user, expiry=None)[1] # This token will never expire
        return Response(token, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsAdminOrIsObjectOwner]
        return [permission() for permission in permission_classes]

    def get_serializer(self, *args, **kwargs):
        return TwittnowApiKeySerializer(*args, **kwargs)


class CustomFieldViewSet(viewsets.ModelViewSet):
    queryset = CustomFields.objects.all()

    def list(self, request):
        queryset = CustomFields.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        data = request.data
        data["user"] = request.user.id
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        sn = self.get_object()
        sn.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsAdminOrIsObjectOwner]
        return [permission() for permission in permission_classes]


    def get_serializer(self, *args, **kwargs):
        return CustomFieldSerializer(*args, **kwargs)


class ServicenowViewSet(viewsets.ModelViewSet):
    queryset = Servicenow.objects.all()

    def list(self, request):
        try:
            queryset = Servicenow.objects.get(user=request.user)
        except Servicenow.DoesNotExist:
            return Response({"message": "No Servicenow record found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data
        if isinstance(data, list):
            return Response({"message": "Can only add one instance per user"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Non-admin users don't have to pass the user
            # attribute. Whether they do or don't, the value
            # will be determined by their credentials
            if not request.user.is_staff:
                data["user"] = request.user.id

            serializer = self.get_serializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        sn = self.get_object()
        data = request.data

        # Security - Disallow updating of the user associated with the record
        if data.get("user"):
            data.pop("user")

        serializer = self.get_serializer(sn, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        sn = self.get_object()
        sn.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsAdminOrIsObjectOwner]
        return [permission() for permission in permission_classes]

    def get_serializer(self, *args, **kwargs):
        return ServicenowSerializer(*args, **kwargs)
