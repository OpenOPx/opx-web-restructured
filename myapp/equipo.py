
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
# @brief Función que provee plantilla HTML para gestión de plantillas de equipo
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def equiposView(request):
    return render(request, "proyectos/gestion-plantillas.html")

##
# @brief Recurso de listado de plantillas de equipo
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def listadoEquipos(request):

    user = usuarioAutenticado(request)
    person = models.Person.objects.get(user__userid = user.userid)
    rol = str(person.role.role_id)
    
    if (rol == '8945979e-8ca5-481e-92a2-219dd42ae9fc'):
        equipos = models.Team.objects.all().values()
        response = {
            'code': 200,
            'data': list(equipos),
            'status': 'success'
        }

    elif (rol == '628acd70-f86f-4449-af06-ab36144d9d6a'):
        equipos = models.Team.objects.filter(team_leader__pers_id__exact = person.pers_id).values()
        response = {
            'code': 200,
            'data': list(equipos),
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

        team_description = request.POST.get('team_description')

        plantilla = models.Team(
            team_name = request.POST.get('team_name'), 
            team_leader = person,
            #team_description = request.POST.get('descripcionEquipo')
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

##
# @brief Recurso de eliminación de plantilla de equipo
# @param request Instancia HttpRequest
# @param planid Identificación de Plantilla de Equipo
# @return cadena JSON
#
@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def eliminarEquipo(request, planid):

    proyecto_equipo = models.ProjectTeam.objects.filter(team__team_id__exact = planid)
    proyecto_equipo = list(proyecto_equipo.values())

    if len(proyecto_equipo) > 0:
        raise ValueError("El equipo esta asociado a un proyecto")

    try:
        plantilla = models.Team.objects.get(pk=planid)
        
        plantilla.delete()

        response = {
            'code': 200,
            'status': 'success'
        }

    except ObjectDoesNotExist:

        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:
        response = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

    ##
# @brief Recurso de edición de plantilla de equipo
# @param request Instancia HttpRequest
# @param planid Identificación de plantilla de Equipo
# @return cadena JSON
#
@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def actualizarEquipo(request, planid):

    try:
        plantilla = models.Team.objects.get(pk=planid)

        plantilla.team_name = request.POST.get('name')

        response = {
            'code': 200,
            'data': model_to_dict(plantilla),
            'status': 'success'
        }

        plantilla.full_clean()
        plantilla.save()

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError as e:
        response = {
            'code': 400,
            'errors': dict(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])