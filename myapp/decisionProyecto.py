
from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext

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
# @brief Recurso de listado de decisiones-proyectos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoDecisionesProyecto(request,proyid):
     decisionesProyecto = models.ProjectDecision.objects.filter(project__proj_id__exact = proyid)
     decisionesProyecto = list(decisionesProyecto.values())
     return JsonResponse(decisionesProyecto, safe = False)

##
# @brief Funcion que asigna decision(es) a un proyecto especifico
# @param proyecto instancia del modelo proyecto
# @param decisiones listado de identificadores de decisiones
# @return booleano
#
def almacenarDecisionProyecto(proyecto, decisiones):
    
    try:
        for decisionI in decisiones:

            decisionProyecto = None

            decisionProyecto = models.ProjectDecision(
                project = proyecto, 
                decision = decisionI
            )

            decisionProyecto.save()

        return True

    except ValidationError as e:
        return False

    
    
    
    try:
        proj_id = request.POST.get('proj_id')
        decisiones = request.POST.get('decision')
        proyecto = models.Project.objects.get(proj_id=proj_id)
        decision = models.Decision.objects.get(decs_id=decisiones)
        decisionProyecto = models.ProjectDecision(
            project = proyecto, 
            decision = decision
        )
        decisionProyecto.save()
    #try:
    #    for decision in decisiones:
    #
    #        decisionProyecto = None
#
    #        decisionProyecto = models.ProjectDecision(
    #            project = proj_id, 
    #            decision = decisiones
    #        )
#
    #        decisionProyecto.save()
#
    #    return True

    except ValidationError as e:
        return False

##
# @brief Recurso de eliminación de decisiones-proyectos
# @param request Instancia HttpRequest
# @param desproid Identificación de la decisión-proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarDecisionProyecto(request, desproid):

    try:
        decision = models.ProjectDecision.objects.get(pk = desproid)
        decision.delete()
        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'La decision no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

