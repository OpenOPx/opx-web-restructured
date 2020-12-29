from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext

from myapp import models

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import(
    Paginator,
    EmptyPage
)
from django.db import (connection, transaction)
from django.forms.models import model_to_dict
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from myapp.view.utilidades import dictfetchall, obtenerParametroSistema, obtenerEmailsEquipo, usuarioAutenticado
from myapp.view.notificaciones import gestionCambios

##
# @brief recurso de almacenamiento de Tareas
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoTarea(request):
    print("1")
    print(request.data)
    restricciones = models.TaskRestriction(
        start_time = request.POST.get('???'),
        end_time = request.POST.get('???'),
        task_unique_date = request.POST.get('???'),
        task_start_date = request.POST.get('???'),
        task_end_date = request.POST.get('???')
    )
    print("2")

    territorioSubconjunto = models.TerritorialDimension(
        dimension_name = request.POST.get('nombreSubconjunto'),
        dimension_geojson = request.POST.get('getgeojsonsubconjunto'),
        dimension_type = models.DimensionType.objects.get(dim_type_id = request.POST.get('tipoDimension'))
    )
    print("3")

    territorioSubconjunto.full_clean()
    territorioSubconjunto.save()

    restricciones.full_clean()
    restricciones.save()

    print("4")
    tarea = models.Task(
        task_name = request.POST.get('tarenombre'),
        task_type = models.TaskType.objects.get(pk = request.POST.get('taretipo')),
        task_quantity = request.POST.get('tarerestriccant'),
        task_priority = models.TaskPriority.objects.get(priority_number = request.POST.get('tareprioridad')),
        task_description = request.POST.get('taredescripcion'),
        project = models.Project.objects.get(pk = request.POST.get('proyid')),
        task_observation = request.POST.get('task_observation'),
        
        #dimensionid = models.TerritorialDimension.objects.get(pk = request.POST.get('dimensionid')), # el id de la dimension mayor debe estar presente acá
        instrument = models.Instrument.objects.get(pk = request.POST.get('instrid')),


        territorial_dimension = territorioSubconjunto,
        task_restriction = restricciones,

        task_completness = request.POST.get('completitud'),
    )

    print("5")

    try:
        print("6")

        tarea.full_clean()
        tarea.save()
        print("7")

        data = serializers.serialize('python', [tarea])
        print("8")

        response = {
            'code':     201,
            'tarea':    data,
            'status':   'success'
        }

    except ValidationError as e:
        territorioSubconjunto.delete()
        restricciones.delete()
        response = {
            'code':     400,
            'errors':   dict(e),
            'status':   'error'
        }

    except IntegrityError as e:
        territorioSubconjunto.delete()
        restricciones.delete()
        response = {
            'code':     400,
            'message':  str(e),
            'status':   'success'
        }
    print("9")

    return JsonResponse(response, safe=False, status=response['code'])

    ##
# @brief recurso que provee el listado de tareas
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoTareas(request):

    try:
        # Obtener usuario autenticado
        usuario = usuarioAutenticado(request)
        person = models.Person.objects.get(user__userid = usuario.userid)
        tareasUsuario = []
        proyectosUsuario = []
        n = ""
        # Superadministrador
        if str(person.role_id) == '8945979e-8ca5-481e-92a2-219dd42ae9fc':
            tareasUsuario = []
            n = "SELECT tk.* FROM opx.task as tk;"

        # Consulta de proyectos para un usuario proyectista
        elif str(person.role_id) == '628acd70-f86f-4449-af06-ab36144d9d6a':
            n = "SELECT tk.* FROM opx.person AS person INNER JOIN opx.project AS pj ON person.pers_id = pj.proj_owner_id INNER JOIN opx.task as tk ON pj.proj_id = tk.project_id where person.pers_id = '"+ str(person.pers_id)+"';"

        # Consulta de proyectos para un usuario voluntario o validador
        elif str(person.role_id) == '0be58d4e-6735-481a-8740-739a73c3be86' or str(person.pers_id) == '53ad3141-56bb-4ee2-adcf-5664ba03ad65':
            n = "SELECT DISTINCT tk.* FROM opx.person AS person INNER JOIN opx.team_person AS tp ON person.pers_id =tp.person_id INNER JOIN opx.project_team AS pt ON tp.team_id = pt.team_id INNER JOIN opx.task AS tk ON tk.project_id = pt.project_id WHERE person.pers_id = '"+str(person.pers_id)+"';"

      # ================ Obtener página validación de la misma ========================
        page = request.GET.get('page')

        if (page is None):
            page = 1

        all = request.GET.get('all')

        # Obtener Búsqueda y validación de la misma
        search = request.GET.get('search')
        if search is not  None:
            if len(tareasUsuario) > 0:
                query += " and"
            query += " (t.task_name ~* '" + search + "');"        

        with connection.cursor() as cursor:
            cursor.execute(n)

            # formatear respuesta de base de datos
            tareas = dictfetchall(cursor)
       
        # Progreso de las Tareas
        for t in tareas:
            t['task_type_name'] = (models.TaskType.objects.get(pk = t['task_type_id'])).task_type_name
            t['instrument_name']= (models.Instrument.objects.get(pk = t['instrument_id'])).instrument_name
            t['proj_name']= (models.Project.objects.get(pk = t['project_id'])).proj_name
            t['priority_name']= (models.TaskPriority.objects.get(pk = t['task_priority_id'])).priority_name

            # Tipo encuesta
            if t['task_type_id'] == 1:
                encuestas = models.Survery.objects.filter(task_id__exact=t['task_id']) #Me quedé varado en el survey
                progreso = (len(encuestas) * 100) / t['completness']
                t['task_quantity'] = progreso

        if all is not None and all == "1":
            data = {
                'code': 200,
                'tareas': tareas,
                'status': 'success'
            }
        else:
            # Obtener Página
            paginator = Paginator(tareas, 10)
            # Obtener lista de tareas
            tareas = paginator.page(page).object_list
            data = {
                'code': 200,
                'paginator': {
                    'currentPage': page,
                    'perPage': paginator.per_page,
                    'lastPage': paginator.num_pages,
                    'total': paginator.count
                },
                'tareas': tareas,
                'status': 'success'
            }

    except EmptyPage:

        data = {
            'code': 400,
            'message': 'Página inexistente',
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])