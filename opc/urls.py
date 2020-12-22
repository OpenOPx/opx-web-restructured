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

from myapp import views, proyecto


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.loginView),
    path('login/', views.login),

    path('proyectos/', proyecto.listadoProyectosView),
    path('proyectos/gestion/', proyecto.gestionProyectosView),
    path('proyectos/list/', proyecto.listadoProyectos),
    path('proyectos/store/', proyecto.almacenamientoProyecto),

    #path('auth/password-reset/', auth.passwordReset),
    #path('auth/password-reset-verification/', auth.passwordResetVerification),
    #path('auth/password-reset/<str:token>', auth.passwordResetConfirmation),
    #path('auth/password-reset-done/', auth.passwordResetDone),
    path('usuarios/', views.listadoUsuariosView),
    path('usuarios/list/', views.listadoUsuarios),
    #path('usuarios/store/', views.almacenarUsuario),
    #path('usuarios/detail/<str:userid>', views.detalleUsuario),
    #path('usuarios/delete/<str:userid>', views.eliminarUsuario),
    #path('usuarios/<str:userid>', views.actualizarUsuario),
]
