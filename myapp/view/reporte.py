
from django.db import (connection, transaction)
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from myapp.view.utilidades import dictfetchall
from django.http.response import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from myapp import models

##
# @brief 
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def reporteEquiposView(request):
    return render(request, "reportes/reporte-equipo.html")


def miembrosEquipoView(request, planid):

    try:
        plantilla = models.Team.objects.get(pk=planid)

        response = render(request, "reportes/reportes-miembros.html", {'plantilla': plantilla})

    except ObjectDoesNotExist:
        response = HttpResponse("", status=404)

    except ValidationError:
        response = HttpResponse("", status=400)

    return response

##
# @brief 
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def reporteIndividualMiembroView(request):
    return render(request, "reportes/reporteIndividualMiembro.html")

##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def canva1(request):

    query = "select genero.gender_name, count(*) \
            from opx.gender as genero \
            inner join opx.person as persona on persona.gender_id = genero.gender_id \
            group by genero.gender_id"

    with connection.cursor() as cursor:
        cursor.execute(query)
        resultados = dictfetchall(cursor)

    response = {
        'code': 200,
        'data': resultados,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def canva2(request):

    query = "select rol.role_name, count(*) \
            from opx.role as rol \
            inner join opx.person as persona on persona.role_id = rol.role_id \
            group by rol.role_id"

    with connection.cursor() as cursor:
        cursor.execute(query)
        resultados = dictfetchall(cursor)

    response = {
        'code': 200,
        'data': resultados,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def canva3(request):

    query = "select nivelE.educlevel_name, count(*) \
            from opx.education_level as nivelE \
            inner join opx.person as persona on persona.education_level_id = nivelE.educlevel_id \
            group by nivelE.educlevel_id"

    with connection.cursor() as cursor:
        cursor.execute(query)
        resultados = dictfetchall(cursor)

    response = {
        'code': 200,
        'data': resultados,
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief 
# @param request instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def generales(request):
    
    with connection.cursor() as cursor:
        usuarios = "select count(*) as cantidad from opx.person" 
        cursor.execute(usuarios)
        usuarios = dictfetchall(cursor)[0]['cantidad']

        decisiones = "select count(*) as cantidad from opx.decision" 
        cursor.execute(decisiones)
        decisiones = dictfetchall(cursor)[0]['cantidad']

        contextos = "select count(*) as cantidad from opx.context" 
        cursor.execute(contextos)
        contextos = dictfetchall(cursor)[0]['cantidad']

        instrumentos = "select count(*) as cantidad from opx.instrument" 
        cursor.execute(instrumentos)
        instrumentos = dictfetchall(cursor)[0]['cantidad']

        proyectos = "select count(*) as cantidad from opx.project" 
        cursor.execute(proyectos)
        proyectos = dictfetchall(cursor)[0]['cantidad']

        tareas = "select count(*) as cantidad from opx.task" 
        cursor.execute(tareas)
        tareas = dictfetchall(cursor)[0]['cantidad']

        equipos = "select count(*) as cantidad from opx.team" 
        cursor.execute(equipos)
        equipos = dictfetchall(cursor)[0]['cantidad']

    response = {
        'code': 200,
        'data': {
            'usuarios': usuarios,
            'decisiones': decisiones,
            'contextos': contextos,
            'instrumentos': instrumentos,
            'proyectos': proyectos,
            'tareas': tareas,
            'equipos': equipos
        },
        'status': 'success'
    }

    return JsonResponse(response, safe=False, status=response['code'])