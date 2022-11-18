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
from spider import views as spiderView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("index",views.index),
    path("test_upload",views.test_upload),
    path("test_usemodel", views.usemodel),

    # 爬虫任务列表
    path('spider/taskJobList/', spiderView.taskJobList),
    # 爬虫任务请求
    path('spider/spiderRequest/', spiderView.spiderRequest),
    # 爬虫资源查看
    path('spider/itemList/', spiderView.itemList),

    #管理员
    #1 管理员上传标准模型
    path("uploadStandModel", views.uploadStandModel),
    #2 管理员上传模型权重
    path("uploadStandModelWeight", views.uploadStandModelWeight),
    #3 使用标准模型的权重进行单图片预测
    path("useStandModelWeightImage", views.useStandModelWeightImage),
    #4 使用标准模型权重对zip压缩包内的所有文件进行预测
    path("useStandModelWeightZip", views.useStandModelWeightZip),
    #5 上传标准数据类型
    path('uploadNewStandDataset',views.uploadNewStandDataset),

    #用户
    #1 获取特定类型的所有标准模型
    path("getAllStandModelByType",views.getAllStandModelByType),
    #2 获取某个标准模型对应的所有权重
    path("getStandModelWeight",views.getStandModelWeight),
    #3 创建数据集
    path('createDataset',views.createDataset),
    #4 向创建的数据集中导入数据
    path('importData', views.importData),
    #5 模型训练
    path('trainModel', views.trainModel),
    #6 模型创建
    path('createModel',views.createModel),
    #7 为模型指定数据集
    path('datasetToModel',views.datasetToModel),
    #8 终止训练
    path('stopTrain',views.stopTrain),
    #9 查询所有训练进程并更新所有进程状态
    path('selectAllTrain',views.selectAllTrain),
    #10 查询所有的数据集
    path('selectAllDataset', views.selectAllDataset),
    #11 查询所有的标准数据集
    path('selectAllStandDataset',views.selectAllStandDataset),
    #12 根据type查询对应的标准数据集
    path('selectDataTypeById',views.selectDataTypeById)
]
