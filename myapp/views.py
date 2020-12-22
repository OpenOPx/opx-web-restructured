# from django.shortcuts import render
from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext
import shapely.geometry
import geopandas

from myapp import models

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import (connection, transaction)
from django.db.utils import DataError, IntegrityError
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

# Create your views here.

##
# Vista de Autenticación Dashboard
# @param request Instancia HttpRequest
# @return Plantilla Html
#


def loginView(request):

    return render(request, "auth/login.html")


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):

    data = {
        'token': 'str(refresh.access_token)',
        'user': {
            'userid':       'user.userid',
            'userfullname': 'user.userfullname',
            'useremail':    'user.useremail',
            'rol':          'rol.rolname',
            'puntaje':      'user.puntaje'
        },
        'code': 200
        }

    return JsonResponse(data, status = data['code'])

