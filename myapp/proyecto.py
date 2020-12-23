
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
from myapp.view.utilidades import usuarioAutenticado, reporteEstadoProyecto

##
# @brief Función que provee una plantilla HTML para la gestión de proyectos
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoProyectosView(request):
    return render(request, 'proyectos/listado.html')

##
# @brief Función que provee una plantilla HTML para la gestión de cambios de un proyecto
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def gestionProyectosView(request):
    return render(request, "proyectos/gestion-proyectos-mapa.html")

    ##

# @brief Recurso de listado de proyectos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((AllowAny,))
def listadoProyectos(request):
    search = request.GET.get('search')
    page = request.GET.get('page')
    all = request.GET.get('all')

    try:
        if 'HTTP_AUTHORIZATION' in request.META.keys() and request.META['HTTP_AUTHORIZATION'] != 'null':

            # # Decodificando el access token
            # tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
            #                             settings.SIMPLE_JWT['VERIFYING_KEY'])
            # tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)
            # #consultando el usuario
            # user = models.Usuario.objects.get(pk = tokenDecoded['user_id'])
            user = usuarioAutenticado(request)

            # ============================ Consultando proyectos ====================================

            #Consulta de proyectos para super administrador

            person = models.Person.objects.get(user__userid = user.userid)
                
            if str(person.role.role_id) == '8945979e-8ca5-481e-92a2-219dd42ae9fc':
                proyectos = models.Project.objects.all()

            # Consulta de proyectos para proyectista
            elif str(person.role.role_id) == '628acd70-f86f-4449-af06-ab36144d9d6a':
                proyectos = models.Project.objects.filter(proj_owner__pers_id__exact = person.pers_id)

            # Consulta de proyectos para voluntarios o validadores
            elif str(person.role.role_id) == '0be58d4e-6735-481a-8740-739a73c3be86' or str(person.role.role_id) == '53ad3141-56bb-4ee2-adcf-5664ba03ad65':

                proyectosAsignados = models.Team.objects.filter(team_leader__pers_id__exact = person.pers_id)
                proyectosAsignadosID = []

                for p in proyectosAsignados:
                    proyectosAsignadosID.append(p.proj_id)

                proyectos = models.Project.objects.filter(pk__in = proyectosAsignadosID)

            #Tipo de usuario distinto
            else:
                proyectos = models.Project.objects.filter(proj_name = 'qwerty')

        # Usuario Invitado
        else:
            proyectos = models.Project.objects.all()

        # ================= Busqueda de proyectos
        if search:
            proyectos = proyectos.filter(proj_name__icontains = search)

        # Especificando orden
        proyectos = proyectos.order_by('-proj_creation_date')

        # convirtiendo a lista de diccionarios
        proyectos = list(proyectos.values())
        print(proyectos)
        listadoProyectos = []
        for p in proyectos:

            #Consulta del proyectista
            persona = models.Person.objects.get(pk = p['proj_owner_id'])
            p['proyectista'] = persona.pers_name + ' ' + persona.pers_lastname 

            if 'user' in locals() and str(person.role.role_id) == '628acd70-f86f-4449-af06-ab36144d9d6a':

                p['dimensiones_territoriales'] = []

                dimensionesTerritoriales = models.TerritorialDimension.objects\
                                           .filter(proyid__exact = p['proyid'])\
                                           .filter(estado=1)\
                                           .values()

                dimensionesTerritoriales = list(dimensionesTerritoriales)

                for dim in dimensionesTerritoriales:
                    tareas = list(models.Tarea.objects.filter(dimensionid__exact=dim['dimensionid'])\
                                                      .filter(proyid = p['proyid'])\
                                                      .values())

                    dim['tareas'] = tareas

                    p['dimensiones_territoriales'].append(dim)

            # Reportes
            p['reportes'] = reporteEstadoProyecto(p['proyid'])

            listadoProyectos.append(p)

        if all is not None and all == "1":

            data = {
                'code': 200,
                'proyectos': listadoProyectos,
                'status': 'success'
            }

        else:

            # Paginación
            paginator = Paginator(listadoProyectos, 10)

            # Validación de página
            if page is None:
                page = 1

            #Petición de página
            proyectos = paginator.page(page).object_list

            data = {
                'code': 200,
                'paginator': {
                    'currentPage': int(page),
                    'perPage': paginator.per_page,
                    'lastPage': paginator.num_pages,
                    'total': paginator.count
                },
                'proyectos': proyectos,
                'status': 'success',
            }

    except EmptyPage:

        data = {
            'code': 404,
            'message': 'Página inexistente',
            'status': 'error'
        }

    except IndexError:
        data = {
            'code': 400,
            'status': 'error'
        }

    except TokenBackendError as e:
        data = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de almacenamiento de proyectos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoProyecto(request):

    # Decodificando el access token
    tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'], settings.SIMPLE_JWT['VERIFYING_KEY'])
    tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)

    decisiones = request.POST.get('decisiones')
    contextos = request.POST.get('contextos')
    equipos = request.POST.get('plantillas')
    delimitacionGeograficas = request.POST.get('delimitacionesGeograficas')

    proyecto = models.Project(
        proj_name = request.POST.get('proynombre'),
        proj_description= request.POST.get('proydescripcion'),
        proj_external_id = 12345,
        proj_creation_date = datetime.today(),
        proj_close_date = request.POST.get('proyfechacierre'),
        proj_start_date = request.POST.get('proyfechainicio'),
        proj_completness = 0,
        isactive = 1,
        project_type = request.POST.get('tiproid'),
        proj_owner = tokenDecoded['user_id']
    )

    try:
        proyecto.full_clean()

        if delimitacionGeograficas is None:
            raise ValidationError({'delitacionesGeograficas': 'Requerido'})

        proyecto.save()

        if decisiones is not None:
            decisiones = json.loads(decisiones)
            almacenarDecisionProyecto(proyecto, decisiones)

        if contextos is not None:
            contextos = json.loads(contextos)
            almacenarContextosProyecto(proyecto, contextos)

        almacenarDelimitacionesGeograficas(proyecto, delimitacionGeograficas)

        if equipos is not None:
            equipos = json.loads(equipos)
            asignarEquipos(proyecto, equipos)

        data = serializers.serialize('python', [proyecto])[0]

        data = {
            'code': 201,
            'proyecto': data,
            'status': 'success'
        }

    except ValidationError as e:

        try:
            errors = dict(e)
        except ValueError:
            errors = list(e)[0]

        data = {
            'code': 400,
            'errors': errors,
            'status': 'error'
        }

    except IntegrityError as e:

        data = {
            'code': 500,
            'message': str(e),
            'status': 'success'
        }

    except ObjectDoesNotExist as e:
        data = {
            'code': 404,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Funcion que asigna decision(es) a un proyecto especifico
# @param proyecto instancia del modelo proyecto
# @param decisiones listado de identificadores de decisiones
# @return booleano
#
def almacenarDecisionProyecto(proyecto, decisiones):

    try:
        for decision in decisiones:
    
            decisionProyecto = None

            decisionProyecto = models.DecisionProyecto(
                project = proyecto.proj_id, 
                decision = decision
            )

            decisionProyecto.save()

        return True

    except ValidationError as e:
        return False

        ##
# @brief Funcion que asigna contexto(s) a un proyecto especifico
# @param proyecto instancia del modelo proyecto
# @param contextos listado de identificadores de contextos
# @return booleano
#
def almacenarContextosProyecto(proyecto, contextos):

    try:
        for contexto in contextos:

            contextoProyecto = models.ProjectContext(
                project = proyecto.proj_id, 
                context = contexto
            )

            contextoProyecto.save()

            del contextoProyecto

        return True

    except ValidationError as e:
        return False

##
# @brief Funcion que almacena las dimensiones geograficas de un proyecto especifico
# @param proyecto instancia del modelo proyecto
# @param delimitacionesGeograficas delimitaciones geograficas generadas por el mapa
# @return Diccionario
#
def almacenarDelimitacionesGeograficas(proyecto, delimitacionesGeograficas):

    try:

        delimitaciones = json.loads(delimitacionesGeograficas)

        with transaction.atomic():

            for d in delimitaciones:
                delimitacion = models.TerritorialDimension(
                    proyid = proyecto.proyid, 
                    dimension_name = d['nombre'], 
                    dimension_geojson = d['geojson'],
                    isactive = 1
                    #preloaded = ???,
                    #dimension_type = ???
                )

                delimitacion.full_clean()

                delimitacion.save()

                del delimitacion

        data = {
            'result': True
        }

    except ValidationError as e:

        data = {
            'result': False,
            'message': dict(e)
        }

    return data

##
# @brief Funcion que asigna integrantes a un proyecto en base a los integrantes de una plantilla de equipo
# @param proyecto instancia del modelo proyecto
# @param equipos lista de identificadores de plantillas de equipo
#
def asignarEquipos(proyecto, equipos):

    with transaction.atomic():

        for equipo in equipos:

            plantilla = models.PlantillaEquipo.objects.get(pk=equipo)

            usuarios = models.MiembroPlantilla.objects.filter(planid__exact=equipo)

            for usuario in usuarios:
#???
                integrante = models.Team(
                    userid=usuario.userid, 
                    proyid=proyecto.proyid
                )
                integrante.save()