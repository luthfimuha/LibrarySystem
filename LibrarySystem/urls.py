"""LibrarySystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from library import views

urlpatterns = [
    path('', views.getHome),
    path('admin/login/', views.admin_login),
    path('admin/logout/', views.admin_logout),
    path('admin/dashboard/', views.admin_dashboard),
    path('admin/booklist/', views.admin_booklist),
    path('admin/studentlist/', views.admin_studentlist),
    path('admin/booklist/update', views.admin_updatebook),
    path('admin/addbook', views.admin_addbook),
    path('admin/sendemail/', views.sendemail),
    path('saveupdate/', views.admin_saveupdate),
    path('admin/borrowlist/', views.admin_borrowlist),
    path('login/', views.login),
    path('logout/', views.logout),
    path('register/', views.register),
    path('getCode/', views.getCode),
    path('student/dashboard/', views.dashboard),
    path('student/booklist/', views.stu_booklist),
    path('student/booklist/detail/', views.stu_showbook),
    path('student/borrow/', views.stu_borrow),
    path('student/return/', views.stu_return),
    path('student/history/', views.stu_history),
    # path('student/dashboard/', views.dashboard),
]
