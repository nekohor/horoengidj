
from rest_framework import views
from rest_framework import permissions
from rest_framework_simplejwt import authentication
from rest_framework.response import Response

# Create your views here.


class UserInfoView(views.APIView):
    # permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        resp = {}
        resp["code"] = 200
        resp["data"] = {
            "roles": ["engineer"],
            "introduction": "I am an engineer.",
            "avatar":  "http://192.168.88.158:8000/static/img/avatar.gif",
            "name": "Engineer"
        }
        resp["msg"] = "OK"

        return Response(resp)


class UserLogoutView(views.APIView):
    # permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = (authentication.JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        resp = {}
        resp["code"] = 200
        resp["data"] = "success"
        resp["msg"] = "OK"

        return Response(resp)
