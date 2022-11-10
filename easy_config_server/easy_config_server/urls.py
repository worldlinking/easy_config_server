"""easy_config_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from mysite import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("index",views.index),
    path("test_upload",views.test_upload),
    path("test_usemodel", views.usemodel),

    #管理员

    #1 管理员上传标准模型
    path("uploadStandModel", views.uploadStandModel),
    #2 管理员上传模型权重
    path("uploadStandModelWeight", views.uploadStandModelWeight),
    #3 使用标准模型的权重进行预测
    path("useStandModelWeightImage", views.useStandModelWeightImage)
]
