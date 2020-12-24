
from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext

from django.forms.models import model_to_dict

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import(
    Paginator,
    EmptyPage
)
from django.db import (connection, transaction)
from django.db.utils import IntegrityError, DataError
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from myapp import models
from myapp.view.utilidades import usuarioAutenticado

##
# @brief Recurso de listado de plantillas de equipo
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def listadoEquipos(request):

    user = usuarioAutenticado(request)
    rol = models.Person.objects.get(user__userid = user.userid)

    if(rol == '628acd70-f86f-4449-af06-ab36144d9d6a' or rol == '8945979e-8ca5-481e-92a2-219dd42ae9fc'):

        plantillas = PlantillaEquipo.objects.filter(userid__exact = user.userid).values()

        response = {
            'code': 200,
            'data': list(plantillas),
            'status': 'success'
        }

    else:
        response = {
            'code': 403,
            'message': 'Usuario no permitido',
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])


##
# @brief Recurso de creación de plantilla de equipo
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def crearEquipo(request):
    try:
        user = usuarioAutenticado(request)
        person = models.Person.objects.get(user__userid = user.userid)

        plantilla = models.Team(
            team_name = request.POST.get('nombreEquipo'), 
            team_leader = person
        )

        plantilla.full_clean()
        plantilla.save()

        response = {
            'code': 201,
            'data': model_to_dict(plantilla),
            'status': 'success'
        }

    except ValidationError as e:

        response = {
            'code': 400,
            'errors': dict(e),
            'status': 'success'
        }

    return JsonResponse(response, safe=False, status=response['code'])