"""
URL configuration for dsci551_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from dsci551 import views  # import views
from django.shortcuts import redirect  # if you want to redirect

from django.contrib import admin
from django.urls import path
from dsci551 import views  # import views

from django.urls import path
from django.shortcuts import render 


urlpatterns = [
    path('admin/', admin.site.urls),

    # choose page
    path('', views.home, name='home'),

    # register, login and logout path
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # query page
    path('connect/', views.connect_database, name='connect_database'), 
    path('query/', views.natural_language_query, name='natural_language_query'),
    path('history/', views.user_query_history, name='user_query_history'), 
    # path("natural-language-query/", views.natural_language_query, name="natural_language_query")
    path('select_database/', views.select_database, name='select_database'),
    path('nosql_query/', views.nosql_query, name='nosql_query'),
    path('nosql_mongo_query/', views.nosql_mongo_query, name='nosql_mongo_query'),
]

