from rest_framework.views import APIView

# for API responses
from rest_framework.response import Response
from rest_framework import status


class DialogFlowFulfillment(APIView):
    def post(self, request):
        print(request.data)

        return Response(
            {"message": "Bot response acknowledged"},
            status.HTTP_200_OK
        )
