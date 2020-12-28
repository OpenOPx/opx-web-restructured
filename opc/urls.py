"""opc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import handler404, handler500

from myapp import views, proyecto, decision, equipo, comentario, decisionProyecto, equipoPersona, equipoMiembros
from myapp.view import (
    userview, instrumentview, koboclient, 
    utilidades, osm, rolesview, tiposProyecto, profileview, estadisticas, contextoview, tareas #,contextualizacion, tareas
)

urlpatterns = [

#los id's los pasan por el path y deberian pasarlos internamente



    path('admin/', admin.site.urls), 

    path('', views.loginView), #OK LEO
    path('login/', views.login), #OK LEO OK

    #path('auth/password-reset/', auth.passwordReset),
    #path('auth/password-reset-verification/', auth.passwordResetVerification),
    #path('auth/password-reset/<str:token>', auth.passwordResetConfirmation),
    #path('auth/password-reset-done/', auth.passwordResetDone),

    path('usuarios/', userview.listadoUsuariosView), #OK K.O LEO
    path('usuarios/list/', userview.listadoUsuarios), #OK K.O LEO
    path('usuarios/store/', userview.almacenarUsuario), #ok OK L
    path('usuarios/detail/<str:userid>', userview.detalleUsuario), #OK LEO
    path('usuarios/delete/<str:userid>', userview.eliminarUsuario),
    path('usuarios/<str:userid>', userview.actualizarUsuario),

    path('contextos/', contextoview.listadoContextosView), #OK S OK
    path('contextos/list/', contextoview.listadoContextos), #OK S OK
    path('contextos/store/', contextoview.almacenamientoContexto), #OK S OK
    path('contextos/delete/<str:contextoid>', contextoview.eliminarContexto), #OK S 
    path('contextos/<str:contextoid>', contextoview.actualizarContexto), #OK S OK
    path('contextos/datos/<str:contextoid>', contextoview.listadoDatosContextoView), #OK S OK
    path('contextos/<str:proyid>/list/', contextoview.listadoContextosProyecto), #OK S OK

    path('datos-contexto/list/', contextoview.listadoDatosContextoCompleto), # OK S OK
    path('datos-contexto/list/<str:contextoid>', contextoview.listadoDatosContexto), # OK S OK
    path('datos-contexto/store/', contextoview.almacenarDatoContexto), # OK S OK
    path('datos-contexto/delete/<str:dataid>', contextoview.eliminarDatoContexto), #OK S OK
    path('datos-contexto/<str:dataid>', contextoview.actualizarDatoContexto), #OK S OK

    #path('decisiones/<str:proyid>/list/', views.listDecisionesProyecto),

    path('decisiones/', decision.listadoDecisionesView), #JM OK OK
    path('decisiones/list/', decision.listadoDecisiones), #JM OK OK
    path('decisiones/store/', decision.almacenarDecision), #JM OK OK
    path('decisiones/delete/<str:desiid>/', decision.eliminarDecision), #JM OK OK
    path('decisiones/<str:desiid>', decision.actualizarDecision), #JM OK OK

    path('decisiones-proyecto/<str:proyid>/', decisionProyecto.listadoDecisionesProyecto), #JM OK
    path('decisiones-proyecto/store/', decisionProyecto.almacenarDecisionProyecto), #JM ???
    path('decisiones-proyecto/delete/<str:desproid>/', decisionProyecto.eliminarDecisionProyecto), #JM OK

    path('equipos/', equipo.equiposView), #JM OK
    path('equipos/<str:planid>/miembros/', equipo.miembrosEquipoView), #JM OK OK
    #path('equipos/list/<str:proyid>', equipo.equipoProyecto),
    #path('equipos/<str:proyid>/usuarios-disponibles/', equipo.usuariosDisponiblesProyecto),
    #path('equipos/store/', equipo.almacenamientoEquipo),
    #path('equipos/delete/<str:equid>', equipo.eliminarEquipo),
    #path('equipos/<str:equid>', equipo.actualizarEquipo),
    #path('equipos/proyecto/<str:proyid>', equipo.equipoProyectoView),

    path('plantillas-equipo/list/', equipo.listadoEquipos), #JM OK OK
    path('plantillas-equipo/<str:planid>/delete/', equipo.eliminarEquipo), #JM OK OK
    path('plantillas-equipo/store/', equipo.crearEquipo), #JM OK OK
    path('plantillas-equipo/<str:planid>/', equipo.actualizarEquipo), #JM OK OK
 
    path('miembros-plantilla/<str:planid>/list/', equipoMiembros.listadoMiembros), #JM OK OK
    path('miembros-plantilla/<str:planid>/store/', equipoMiembros.agregarMiembro), #JM OK OK
    path('miembros-plantilla/<str:miplid>/delete/', equipoMiembros.eliminarMiembro), #JM OK OK
    path('miembros-plantilla/<str:planid>/usuarios-disponibles/', equipoMiembros.miembrosDisponibles), #JM OK

    path('acciones/list/', rolesview.listadoAcciones), #OK - S OK

    path('funciones-rol/list/<str:rolid>', rolesview.listadoFuncionesRol), # OK - S OK
    path('funciones-rol/store/', rolesview.almacenamientoFuncionRol), # OK - S OK
    path('funciones-rol/delete/<str:funcrolid>', rolesview.eliminarFuncionRol), #OK - S OK

    path('instrumentos/', instrumentview.listadoInstrumentosView), #OK OK LF
    path('instrumentos/list/', instrumentview.listadoInstrumentos), #OK OK LF
    path('instrumentos/store/', instrumentview.almacenamientoInstrumento), # OK OK LF
    #path('instrumentos/delete/<str:instrid>', views.eliminarInstrumento), # ESTO ALGUNA VEZ ESTUVO?
    path('instrumentos/<str:instrid>', instrumentview.actualizarInstrumento), # OK OK LF
    #path('instrumentos/<str:id>/informacion/', views.informacionInstrumento),
    path('instrumentos/<str:id>/implementar/', koboclient.implementarFormularioKoboToolbox), #OK OK LF
    path('instrumentos/<str:id>/verificar-implementacion/', koboclient.verificarImplementaciónFormulario), #OK OK LF
    #path('instrumentos/encuesta/crear', views.creacionEncuestaView),
    path('instrumentos/formularios-kobotoolbox/list/', koboclient.listadoFormulariosKoboToolbox), # OK OK LF
    path('instrumentos/enlace-formulario/<str:tareid>', koboclient.enlaceFormularioKoboToolbox), #OKOK LF
    #path('instrumentos/mapear/<str:tareid>', osm.AgregarElemento),
    #path('instrumentos/detalle-cartografia/<str:tareid>', osm.cartografiasInstrumento),
    #path('instrumentos/eliminar-cartografia/<str:cartografiaid>', osm.eliminarCartografia),
    #path('instrumentos/revisar-encuesta/<str:encuestaid>', views.revisarEncuesta),

    path('proyectos/', proyecto.listadoProyectosView), #JM
    path('proyectos/gestion/', proyecto.gestionProyectosView), #JM
    path('proyectos/list/', proyecto.listadoProyectos), #JM
    path('proyectos/store/', proyecto.almacenamientoProyecto), #JM
    path('proyectos/delete/<str:proyid>/', proyecto.eliminarProyecto),
    path('proyectos/<str:proyid>', proyecto.actualizarProyecto),
    #path('proyectos/detail/<str:proyid>', proyecto.detalleProyecto),
    path('proyectos/dimensiones-territoriales/<str:proyid>', proyecto.dimensionesTerritoriales),
    #path('proyectos/<str:proyid>/tareas/', proyecto.tareasProyectoView),
    #path('proyectos/<str:dimensionid>/cambio-territorio/', proyecto.cambioTerritorio),

    path('tipos-proyecto/', tiposProyecto.tiposProyectoView), #OK - S OK
    path('tipos-proyecto/list/', tiposProyecto.listadoTiposProyecto), #OK - S OK 
    path('tipos-proyecto/<str:tiproid>/delete/', tiposProyecto.eliminarTipoProyecto),#OK - S OK
    path('tipos-proyecto/<str:tiproid>', tiposProyecto.edicionTipoProyecto), #OK - S OK
    path('tipos-proyecto/store/', tiposProyecto.almacenamientoTiposProyecto), #OK - S OK

    path('roles/', rolesview.listadoRolesView), #OK - S OK
    path('roles/list/', rolesview.listadoRoles), #OK - S  OK
    path('roles/store/', rolesview.almacenamientoRol), #OK - S NO APLICA 
    path('roles/delete/<str:rolid>', rolesview.eliminarRol), #OK - S NO APLICA
    path('roles/<str:rolid>', rolesview.actualizarRol), #OK - S NO APLICA
    path('roles/permisos/<str:rolid>', rolesview.permisosRolView), #OK - S OK

    path('tareas/', tareas.listadoTareasView), #OK S
    path('tareas/list/', tareas.listadoTareas), # S - 
    #path('tareas/store/', tareas.almacenamientoTarea), S - Me dio sueño
    path('tareas/delete/<str:tareid>/', tareas.eliminarTarea),
    #path('tareas/<str:tareid>', tareas.actualizarTarea),
    #path('tareas/datos-geoespaciales/', tareas.listadoTareasMapa),
    #path('tareas/detail/<str:tareid>', tareas.detalleTarea),
    #path('instrumentos/informacion/<str:id>', views.informacionInstrumentoView),
    #path('tareas-dimension-territorial/<str:dimensionid>', tareas.tareasXDimensionTerritorial),
    path('tareas/tipos/', views.listadoTiposDeTareas),

    path('generos/list/', utilidades.listadoGeneros), #OK S OK
    path('niveles-educativos/list/', utilidades.listadoNivelesEducativos), #OK S OK
    path('elementos-osm/list/', osm.elementosOsm),  # OK - S

    path('barrios/list/', utilidades.listadoBarrios), #OK S OK

    #path('contextualizacion/categorizacion/', contextualizacion.categorizacion), # Falta cargarlo en el modelo para seguir
    #path('contextualizacion/todo/', contextualizacion.todo), # Falta cargarlo en el modelo para seguir
    #path('contextualizacion/mes/', contextualizacion.mensual), # Falta cargarlo en el modelo para seguir
    #path('contextualizacion/semana/', contextualizacion.semanal), # Falta cargarlo en el modelo para seguir
    #path('contextualizacion/dia/', contextualizacion.dia), # Falta cargarlo en el modelo para seguir

    # ========================== Estadisticas Antes =================================
    path('estadisticas/datos-generales/', estadisticas.datosGenerales), #OK - S PROBAR
    path('estadisticas/usuarios-x-rol/', estadisticas.usuariosXRol), #OK - S PROBAR
    path('estadisticas/usuarios-x-genero/', estadisticas.usuariosXGenero), #OK - S PROBAR
    path('estadisticas/usuarios-x-nivel-educativo/', estadisticas.usuariosXNivelEducativo), #OK - S PROBAR (OJO CON ESE NOMBRE EN LA IMAGEN DEL MODELO QUE NO ME LO VAYA A CAMBIAR)
    path('estadisticas/usuarios-x-barrio/', estadisticas.usuariosXBarrio), #OK - S PROBAR
    path('estadisticas/ranking/', estadisticas.ranking),  #OK - S PROBAR 
    path('estadisticas/tareas-x-tipo/', estadisticas.tareasXTipo), #OK - S OJO CON LOS CAMBIOS A HACER

    # ======================== Estadisticas Durante ===================================

    path('estadisticas/proyectos-tareas/', estadisticas.proyectosTareas), # QUEDÉ EN LA PARTE DE ENCUESTAS Y PROGRESO - S
    #path('estadisticas/estado-proyectos/', estadisticas.estadoActualProyectos), # AHORA QUE ME ACUERDO ESTO NO SE VA A USAR 

    # ======================== Estadisticas Después ===================================

    #path('estadisticas/proyectos-tareas-vencidos/', estadisticas.proyectosTareasVencidos),
    #path('estadisticas/estado-proyectos-vencidos/', estadisticas.estadoActualProyectosVencidos),

    # ======================== Estadísticas - Detalle Proyecto ========================

    #path('estadisticas/<str:proyid>/tareas-x-tipo/', estadisticas.tareasXTipoProyecto),
    #path('estadisticas/<str:proyid>/tareas-x-estado/', estadisticas.tareasXEstadoProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-rol/', estadisticas.usuariosXRolProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-barrio/', estadisticas.usuariosXBarrioProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-barrio/<str:keyword>', estadisticas.usuariosXBarrioEspecifico),
    #path('estadisticas/<str:proyid>/usuarios-x-genero/', estadisticas.usuariosXGeneroProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-nivel-educativo/', estadisticas.usuariosXNivelEducativoProyecto),
    #path('estadisticas/<str:proyid>/datos-generales/', estadisticas.datosGeneralesProyecto),
    #path('estadisticas/<str:proyid>/exportar-encuestas/', estadisticas.exportarDatos),
    #path('estadisticas/<str:proyid>/exportar-proyecto/', estadisticas.exportarDatosProyecto),
    #path('estadisticas/<str:proyid>/ranking/', estadisticas.rankingPorProyecto),
    #path('estadisticas/<str:proyid>/campanas/', estadisticas.dimensionesProyecto),
    #path('estadisticas/<str:dimensionid>/tareas-campana/', estadisticas.tareasDimensionProyecto),
    #path('estadisticas/<str:proyid>/instrumentos/', estadisticas.instrumentosProyecto),

    # ========================= Vista Estadísticas =====================================

    path('reportes/antes/', estadisticas.estadisticasView), #OK - S OJO CON LOS CAMBIOS A HACER
    path('reportes/durante/', estadisticas.estadisticasDuranteView), #OK - S OJO CON LOS CAMBIOS A HACER
    path('reportes/despues/', estadisticas.estadisticasDespuesView), #OK - S OJO CON LOS CAMBIOS A HACER
    path('reportes/<str:proyid>/detalle/', estadisticas.estadisticasDetalleView), #OK - S OJO CON LOS CAMBIOS A HACER

    #path('reportes/ranking/', estadisticas.rankingView),  #S - Vistas que se agregan después por nuestra funcionalidad
    #path('reportes/proyecto/', estadisticas.reportesProyectosIndividualesView), #S - Vistas que se agregan después por nuestra funcionalidad
    #path('reportes/proyectos/', estadisticas.reportesProyectosGeneralesView),  #S - Vistas que se agregan después por nuestra funcionalidad

    # =========================== Perfil ===============================================
    path('mi-perfil/', profileview.perfilView), # SEBAS - LEO DIJO QUE LE HARÍA

    #Comment
    path('comentario/<str:proyid>/', comentario.listadoComentarios), #JM 
    path('comentario/<str:commentid>/delete/', comentario.eliminarComentario), #JM ???
    path('comentario/store/', comentario.crearComentario), #JM ???
    path('comentario/<str:commentid>/', comentario.actualizarComentario), #JM ???

    #TeamPerson
    path('equipo-persona/list/', equipoPersona.listadoEquiposPersona), #JM OK
    path('equipo-persona/<str:teamPersonId>/delete/', equipoPersona.eliminarEquipoPersona), #JM - pendiente que Leo le agregue Pk para verificar
    path('equipo-persona/store/', equipoPersona.crearEquipoPersona), #JM - pendiente que Leo le agregue Pk para verificar
    path('equipo-persona/<str:teamPersonId>/', equipoPersona.actualizarEquipoPersona), #JM -  pendiente que Leo le agregue Pk para verificar

    path('external-platforms/kobo-kpi/', koboclient.getKoboKpiUrl)
]
