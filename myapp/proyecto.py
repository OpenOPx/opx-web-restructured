
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
from myapp.view.utilidades import usuarioAutenticado, reporteEstadoProyecto, dictfetchall

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
           # p['reportes'] = reporteEstadoProyecto(p['proyid'])

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

    user = usuarioAutenticado(request)
    person = models.Person.objects.get(user__userid = user.userid)

    # Decodificando el access token
    tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'], settings.SIMPLE_JWT['VERIFYING_KEY'])
    tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)

    decisiones = request.POST.get('decisiones')
    contextos = request.POST.get('contextos')
    equipos = request.POST.get('plantillas')
    delimitacionGeograficas = request.POST.get('delimitacionesGeograficas')
    tipoP = models.ProjectType.objects.get(projtype_id__exact = request.POST.get('tiproid'))
    
    try:
        if((delimitacionGeograficas != "[]") and (decisiones != "[]") and (contextos != "[]") and (equipos != "[]")):
            proyecto = models.Project(
                proj_name = request.POST.get('proynombre'),
                proj_description= request.POST.get('proydescripcion'),
                proj_external_id = 12345,
                proj_creation_date = datetime.today(),
                proj_close_date = request.POST.get('proyfechacierre'),
                proj_start_date = request.POST.get('proyfechainicio'),
                proj_completness = 0,
                project_type = tipoP,
                proj_owner = person
            )

            proyecto.full_clean()
            proyecto.save()

            delimitacionGeograficas = json.loads(delimitacionGeograficas)
            almacenarDelimitacionesGeograficas(proyecto, delimitacionGeograficas)

            decisiones = json.loads(decisiones)
            almacenarDecisionProyecto(proyecto, decisiones)

            contextos = json.loads(contextos)
            almacenarContextosProyecto(proyecto, contextos)

            equipos = json.loads(equipos)
            asignarEquipos(proyecto, equipos)

            data = serializers.serialize('python', [proyecto])[0]
            data = {
                'code': 201,
                'proyecto': data,
                'status': 'success'
            }
        else:
            raise ValidationError({'Información incompleta'})

    except ValidationError as e:
        proyecto.delete()
        try:
            errors = dict(e)
        except ValueError:
            errors = list(e)[0]

        data = {
            'code': 400,
            'errors': errors,
            'message': str(e),
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
        for decisionI in decisiones:

            desicionP = None
            decisionProyecto = None

            desicionP = models.Decision.objects.get(decs_id__exact = decisionI)

            decisionProyecto = models.ProjectDecision(
                project = proyecto, 
                decision = desicionP
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
            contextoP = None
            contextoProyecto = None

            contextoP = models.Context.objects.get(context_id__exact = contexto)
            contextoProyecto = models.ProjectContext(
                project = proyecto, 
                context = contextoP
            )

            contextoProyecto.save()


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

            for d in delimitacionesGeograficas:
                delimitacion = None
                delimitacion = models.TerritorialDimension(
                    dimension_name = d['nombre'], 
                    dimension_geojson = d['geojson'],
                    dimension_type = models.DimensionType.objects.get(dim_type_id__exact = '35b0b478-9675-45fe-8da5-02ea9ef88f1b')
                )
                delimitacion.save()
                delimitacionP = models.ProjectTerritorialDimension(
                    project = proyecto,
                    territorial_dimension = delimitacion
                )
                delimitacionP.save()
                delimitacionP = None
        
            return True

    except ValidationError as e:
        return False

##
# @brief Funcion que asigna integrantes a un proyecto en base a los integrantes de una plantilla de equipo
# @param proyecto instancia del modelo proyecto
# @param equipos lista de identificadores de plantillas de equipo
#
def asignarEquipos(proyecto, equipos):
    try:
            for equipo in equipos:
                equipoP = None
                proyectoEquipo = None

                equipoP = models.Team.objects.get(pk=equipo)

                proyectoEquipo = models.ProjectTeam(
                    team = equipoP,
                    project = proyecto
                )
                print(proyectoEquipo)
                proyectoEquipo.save()
    
            return True

    except ValidationError as e:
        return False

##
# @brief recurso de actualización de proyectos
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarProyecto(request, proyid):
    try:
        proyecto = models.Project.objects.get(pk=proyid)
        decisiones = request.POST.get('decisiones')
        contextos = request.POST.get('contextos')
        equipos = request.POST.get('plantillas')
        delimitacionGeograficas = request.POST.get('delimitacionesGeograficas')

        if((delimitacionGeograficas != "[]") and (decisiones != "[]") and (contextos != "[]") and (equipos != "[]")):
            proyecto.proj_name = request.POST.get('proynombre')
            proyecto.proj_description = request.POST.get('proydescripcion')
            proyecto.project_type = models.ProjectType.objects.get(projtype_id__exact = request.POST.get('tiproid'))
            proyecto.proj_start_date = request.POST.get('proyfechainicio')
            proyecto.proj_close_date = request.POST.get('proyfechacierre')
            #Actualiza las decisiones
            decisiones = json.loads(decisiones)
            if len(decisiones)>0:
                decisionesP = models.ProjectDecision.objects.filter(project__proj_id__exact = proyecto.proj_id)
                if decisionesP.exists():
                    for decisionProj in decisionesP:
                        decisionProj.delete()

                for decision in decisiones:
                    descProj = models.ProjectDecision(project = proyecto, decision = models.Decision.objects.get(pk = decision))
                    descProj.save()

            #Actualiza los contextos
            contextos = json.loads(contextos)
            if len(contextos)>0:
                contextosP = models.ProjectContext.objects.filter(project__proj_id__exact = proyecto.proj_id)
                if contextosP.exists():
                    for contextoProj in contextosP:
                        contextoProj.delete() 
                
                for contexto in contextos:
                    contProj = models.ProjectContext(project = proyecto, context = models.Context.objects.get(pk = contexto))
                    contProj.save()

            proyecto.full_clean()
            proyecto.save()

        # ================== Notificación de Gestion de cambios ========================
#        if request.POST.get('gestionCambio', None) is not None:
    
            #obtener usuarios que hacen parte del proyecto:
#            usuarios = obtenerEmailsEquipo(proyid)

            # Detalle del Cambio
#            detalle = "<b> Fecha Inicio: </b> {} <br />" \
#                      "<b> Fecha Fin </b> {}" \
#                      .format(proyecto.proj_start_date, proyecto.proj_close_date)

            #Enviar notificaciones
#            gestionCambios(usuarios, 'proyecto', proyecto.proj_name, 2, detalle)

        return JsonResponse(serializers.serialize('python', [proyecto]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)

##
# @brief recurso de eliminación de proyectos
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarProyecto(request, proyid):

    try:
        print("1")
        models.ProjectDecision.objects.get(project__proj_id = proyid).delete()
        print("2")
        models.ProjectContext.objects.get(project__proj_id = proyid).delete() 
        print("3")
        models.ProjectTeam.objects.get(project__proj_id = proyid).delete()
        print("4")
        models.TerritorialDimension.filter(dimension_id = (models.ProjectTerritorialDimension.get(project__proj_id = proyid)).dimension_id ).delete()
        print("5")
        #borrar las tareas antes de borrar e pj al igual que
        proyecto = models.Project.objects.get(pk = proyid)
        proyecto.delete()
        print("6")
        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)


        ##

# @brief Plantilla para la gestión del equipo de un proyecto
# @param request instancia HttpRequest
# @param proyid Identificación de un proyecto
# @return cadena JSON
#
def equipoProyectoView(request, proyid):

    try:
        models.Project.objects.get(pk = proyid)
        return render(request, "proyectos/equipo.html")

    except ObjectDoesNotExist:
        return HttpResponse("", status = 404)

    except ValidationError:
        return HttpResponse("", status = 400)

##
# @brief Recurso que provee los integrantes de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificacion del proyecto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def equipoProyecto(request, proyid):

    try:
        query = "select tm.team_name, tm.team_effectiveness, tm.team_leader_id, pt.proj_team_id  from opx.project as pj inner join opx.project_team as pt on pj.proj_id = pt.project_id inner join opx.team as tm on pt.team_id = tm.team_id where pj.proj_id = '"+ proyid+"';"
        with connection.cursor() as cursor:
            cursor.execute(query)
            equipos = dictfetchall(cursor)

            for n in equipos:
                n['name_owner'] = (models.Person.objects.get(pk = n['team_leader_id'])).pers_name

            data = {
                'code': 200,
                'equipo': equipos,
                'status': 'success'
            }

    except ValidationError as e:

        data = {
            'code': 400,
            'equipo': list(e),
            'status': 'success'
        }

    return JsonResponse(data, safe = False, status = data['code'])


    ##
# @brief Recurso que provee los integrantes de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificacion del proyecto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def equiposDisponiblesProyecto(request, proyid):

    try:
        query = "select * from opx.team \
            except(select team1.* from opx.project_team as pt \
            inner join opx.team as team1 on pt.team_id = team1.team_id \
            where pt.project_id = '"+proyid+"');"
            
        with connection.cursor() as cursor:
            cursor.execute(query)
            equipos = dictfetchall(cursor)

            for n in equipos:
                n['name_owner'] = (models.Person.objects.get(pk = n['team_leader_id'])).pers_name

            data = {
                'code': 200,
                'equipo': equipos,
                'status': 'success'
            }

    except ValidationError as e:
        data = {
            'code': 400,
            'equipo': list(e),
            'status': 'success'
        }

    return JsonResponse(data, safe = False, status = data['code'])

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def agregarEquipo(request):
    
    try:
        equipoId = request.POST.get('equipoId')
        proyectoId = request.POST.get('proyectoId')

        equipoP = models.Team.objects.get(pk=equipoId)
        proyectoP = models.Project.objects.get(pk=proyectoId)

        proyectoEquipo = models.ProjectTeam(
                team = equipoP,
                project = proyectoP
        )
    
        proyectoEquipo.save()

        data = {
            'code': 201,
            'integrante': serializers.serialize('python', [proyectoEquipo])[0],
            'status': 'success'
        }

    except ValidationError as e:

        data = {
            'code': 400,
            'errors': dict(e),
            'status': 'error'
        }

    except IntegrityError as e:

        data = {
            'code': 500,
            'errors': str(e),
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarEquipo(request,equid):
        
    try:
        proyectoEquipo = models.ProjectTeam.objects.get(pk = equid)
        proyectoEquipo.delete()

        response = {
            'code': 200,
            'status': 'success'
        }

    except ValidationError as e:

        response = {
            'code': 400,
            'errors': list(e)[0],
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])