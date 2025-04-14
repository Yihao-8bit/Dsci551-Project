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
from dsci551 import views  # 导入 dsci551 应用中的 views 模块
from django.shortcuts import redirect  # 如果你希望根路径重定向到查询页面

from django.contrib import admin
from django.urls import path
from dsci551 import views  # 导入 dsci551 应用中的 views 模块

from django.urls import path
from django.shortcuts import render 


urlpatterns = [
    path('admin/', admin.site.urls),

    # 主页选择页面
    path('', views.home, name='home'),

    # 登录、注册和注销路径
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # 查询页面
    path('query/', views.natural_language_query, name='natural_language_query'),
    path('history/', views.user_query_history, name='user_query_history'), 

    path('select_database/', views.select_database, name='select_database'),
    path('nosql_query/', views.nosql_query, name='nosql_query'),
    path('nosql_mongo_query/', views.nosql_mongo_query, name='nosql_mongo_query'),
]

