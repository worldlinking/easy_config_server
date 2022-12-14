import signal

import cv2
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from mysite.models import User, DataSet, Model, StandModel, StandModelWeight, StandDataset
import os
import torch
from importlib import import_module
from mysite.config import type_path_map
from mysite.config import modelsName
from mysite.utils.writeFile import writeFile
from mysite.utils.isMeetStru import isMeetStru
from mysite.utils.getTotalAndLabelNum import getTotalAndLabelNum
from mysite.utils.killProcTree import killProcTree
import zipfile
from django.core import serializers
from mysite.utils.zipDirectory import zipDirectory
import shutil
import json
import subprocess
import psutil
import errno
import time
from django.db.models import Q
import urllib
import requests



# Create your views here.
def index(request):
    print(User.objects.filter(id=1).values("dataset__path"))
    print(DataSet.objects.filter(user__id=1).values("path"))
    return HttpResponse("hello!")

def test_upload(request):
    if(request.method == "POST"):
        myFile = request.FILES.get("myfile", None)  # 获取上传的文件，如果没有文件，则默认为None
        if not myFile:
            return HttpResponse("Failed")
        destination = open(os.path.join("mysite/models", myFile.name), 'wb+')  # 打开特定的文件进行二进制的写操作for chunk in myFile.chunks():      # 分块写入文件
        for chunk in myFile.chunks():      # 分块写入文件
            destination.write(chunk)
        destination.close()
        return HttpResponse("success")
    return HttpResponse("Failed")

def usemodel(request):
    model = import_module("mysite.Nets.Net")
    model = getattr(model,"Net")()
    model.load_state_dict(torch.load('mysite/models/model.pt'))
    predict = model(torch.tensor([[0.00632,18.00,2.310,0,0.5380,6.5750,65.20,4.0900,1,296.0,15.30,396.90,4.98]],dtype=torch.float32))
    print(predict)
    return HttpResponse("success")

#1 上传标准模型
def uploadStandModel(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    if(req.method == "POST"):
        try:
            # 获取请求参数
            post = req.POST
            name = post.get("name")
            params = post.get("params")
            type = post.get("type")
            info = post.get("info")
            user_id = post.get("user_id")
            stand_dataset_id = post.get("stand_dataset_id")
            net = req.FILES.get("net", None)
            net_path = ""
            if not name and not params and not type and not info and not user_id and not net and not net_path and not stand_dataset_id:
                reslut["code"] = 500
                reslut["info"] = "请求参数有误!"
                return JsonResponse(reslut, safe=False, content_type='application/json')

            #保存网络文件
            isNetWrite = False
            if net is not None:
                #保存网络结构
                type = int(type)
                folder = type_path_map[type]
                path = 'mysite/Nets/%s'%folder
                #获取文件后缀
                suffix = os.path.splitext(net.name)[-1]
                if suffix != ".py" and suffix != ".zip":
                    reslut["code"] = 500
                    reslut["info"] = "failed:文件类型只能为.py或者.zip"
                    return JsonResponse(reslut, safe=False, content_type='application/json')
                if(suffix == ".zip"):#如果是zip文件,需要解压后再保存文件夹
                    f = zipfile.ZipFile(net)
                    f.extractall(path=path+ '/' + "admin"+user_id+"/"+name)
                    isNetWrite = True
                else:
                    # 拼接路径
                    net_path = path + '/' +"admin"+user_id
                    # 写入文件
                    isNetWrite = writeFile(net, net_path, name + suffix)
            if isNetWrite:
                #将数据写入数据库
                if(suffix == ".zip"):
                    StandModel.objects.create(name=name, params=params,
                                              net_path=path+ '/admin' + user_id+"/"+name, type=type, info=info,
                                              user_id=user_id,standDataset_id=stand_dataset_id)
                else:
                    StandModel.objects.create(name=name, params=params,
                                              net_path=net_path + "/" + name + suffix, type=type, info=info,
                                              user_id=user_id,standDataset_id=stand_dataset_id)
                return JsonResponse(reslut, safe=False, content_type='application/json')
        except Exception as e:
            print(e)
            reslut["code"] = 500
            reslut["info"] = "failed"
            return JsonResponse(reslut, safe=False, content_type='application/json')
    else:
        reslut.info = "请求方法有误"
        return JsonResponse(reslut,safe=False, content_type='application/json')

#2 上传标准模型权重
def uploadStandModelWeight(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    if req.method == "POST":
        try:
            #获取请求参数
            post = req.POST
            standModel_id = post.get("standModel_id")
            dataset = post.get("dataset")
            user_id = post.get("user_id")
            standModelWeight = req.FILES.get("standModelWeight", None)
            if standModelWeight is None:
                reslut["code"] = 500
                reslut["info"] = "请求参数有误!"
                return JsonResponse(reslut, safe=False, content_type='application/json')
            #保存权重文件
            #获取标准模型对应的网络类型
            type = StandModel.objects.filter(id=standModel_id).first().type
            #拼接权重文件保存路径
            folder = type_path_map[type]
            path = 'mysite/weights/%s' % folder+"/admin"+user_id
            hasWrite = writeFile(standModelWeight,path,standModelWeight.name)
            if hasWrite:
                StandModelWeight.objects.create(weight_path = path+'/'+standModelWeight.name,standModel_id=standModel_id,user_id=user_id,dataset=dataset)
            return JsonResponse(reslut, safe=False, content_type='application/json')
        except Exception as e:
            reslut["code"] = 500
            reslut["info"] = "failed,reason:"+e
            return JsonResponse(reslut, safe=False, content_type='application/json')

#3 使用管理员上传的标准模型权重对单个样本进行预测
def useStandModelWeightImage(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    path=""
    predict_file=None
    path1 = os.path.abspath('.')
    try:
        post = req.POST
        weight_id = post.get("weight_id")
        predict_file = req.FILES.get("predict_file", None)
        user_id = post.get("user_id")

        #将用户上传图片保存成文件
        path = 'mysite/Temp/user'+user_id
        writeFile(predict_file,path,predict_file.name)

        #获取预测权重的地址和网络结构的地址
        smw = StandModelWeight.objects.filter(id=weight_id).first()
        weight_path = smw.weight_path
        dataset = smw.dataset
        #正查网络结构地址
        net_path = StandModelWeight.objects.filter(id=weight_id).first().standModel.net_path

        #运行系统命令将预测结果保存成文件
        #判断是否有用户预测文件夹,如果没有则创建
        user_path = "mysite/predict/user"+user_id
        if not os.path.exists(user_path):
            os.makedirs(user_path)
        os.system("python {}/predict.py --input {} --ckpt {} --save_val_results_to {} --dataset {}".
                  format(net_path,path1+'/'+path+"/"+predict_file.name,path1+'/'+weight_path,path1+'/'+user_path,dataset))
        reslut['data'] = "user"+user_id+"/"+os.path.splitext(predict_file.name)[0]#返回预测结果文件路径
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = "failed"
        return JsonResponse(reslut, safe=False, content_type='application/json')
    finally:
        if predict_file:
            os.remove(path+"/"+predict_file.name)


# 3.2 使用管理员上传的标准模型权重对单个文本样本进行预测
def useStandModelWeightText(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    predict_file = None
    try:
        post = req.POST
        weight_id = post.get("weight_id")
        content = post.get("content")
        user_id = post.get("user_id")
        predict_file = open('mysite/Temp/user' + user_id + '/sample.txt', 'w', encoding='utf-8')
        predict_file.write(content)
        predict_file.close()

        # 获取预测权重的地址和网络结构的地址
        smw = StandModelWeight.objects.filter(id=weight_id).first()
        weight_path = smw.weight_path
        dataset = smw.dataset
        # 正查网络结构地址
        net_path = StandModelWeight.objects.filter(id=weight_id).first().standModel.net_path

        # 运行系统命令将预测结果保存成文件
        # 判断是否有用户预测文件夹,如果没有则创建
        user_path = "mysite/predict/user" + user_id

        if not os.path.exists(user_path):
            os.makedirs(user_path)
        os.system("python {}/predict.py --input {} --ckpt {} --save_val_results_to {} --dataset {}".
                  format(net_path, predict_file.name, weight_path, user_path, dataset))
        file = open(user_path + "/" + os.path.basename(predict_file.name), "r", encoding='UTF-8')
        res = file.read()
        reslut['data'] = res.split()[0]
        file.close()
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = "failed"
        return JsonResponse(reslut, safe=False, content_type='application/json')
    finally:
        if predict_file:
            os.remove(predict_file.name)


# 4 使用管理员上传的标准模型权重对文件压缩包进行预测
def useStandModelWeightZip(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    path=""
    zipTempPath=""
    predictTempPath=""
    predict_file=None
    path1 = os.path.abspath('.')
    try:
        post = req.POST
        weight_id = post.get("weight_id")
        predict_file = req.FILES.get("predict_zip", None)
        user_id = post.get("user_id")

        #将用户上传压缩包保存成文件
        # 获取文件后缀
        suffix = os.path.splitext(predict_file.name)[-1]
        if suffix != '.zip':
            reslut['code']=500
            reslut['info']="请求方法有误"
            return JsonResponse(reslut, safe=False, content_type='application/json')

        #解压缩文件进指定文件夹
        f = zipfile.ZipFile(predict_file)
        zipTempPath = 'mysite/Temp/user'+user_id
        if not os.path.exists(zipTempPath):
            os.makedirs(zipTempPath)
        zipTempPath = 'mysite/Temp/user'+user_id+"/"+os.path.splitext(predict_file.name)[0]
        f.extractall(path = zipTempPath)

        #获取预测权重的地址和网络结构的地址
        smw = StandModelWeight.objects.filter(id=weight_id).first()
        weight_path = smw.weight_path
        dataset = smw.dataset
        #正查网络结构地址
        net_path = StandModelWeight.objects.filter(id=weight_id).first().standModel.net_path

        #运行系统命令将预测结果保存成文件
        #判断是否有用户预测文件夹,如果没有则创建
        user_path = "mysite/predict/user"+user_id
        if not os.path.exists(user_path):
            os.makedirs(user_path)

        predictTempPath = user_path + "/" + os.path.splitext(predict_file.name)[0]
        #在用户预测文件夹下创建压缩包同名文件夹
        if not os.path.exists(predictTempPath):
            os.makedirs(predictTempPath)

        #遍历所有的样本,进行批量预测
        for file in  os.listdir(zipTempPath):
            file_path = os.path.join(zipTempPath, file)
            os.system("python {}/predict.py --input {} --ckpt {} --save_val_results_to {} --dataset {}".
                      format(net_path, path1+'/'+file_path, path1+'/'+weight_path, path1+'/'+predictTempPath, dataset))

        #将预测结果保存为zip文件
        zipDirectory(predictTempPath)
        #删除预测文件夹
        shutil.rmtree(predictTempPath)
        #删除临时上传文件
        shutil.rmtree(zipTempPath)
        reslut['data'] = "user" + user_id + "/" + os.path.splitext(predict_file.name)[0] + ".zip"  # 返回预测结果文件路径
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = "failed"
        return JsonResponse(reslut, safe=False, content_type='application/json')


def getAllStandModelByType(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        type = req.GET.get("type")
        sm = StandModel.objects.filter(type=type).values("name","id")
        tempList = []
        for osm in sm:
            tempList.append(osm)
        reslut['data'] = tempList
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"]=500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')
def getStandModelWeight(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        standModel_id = req.GET.get("standModel_id")
        smw = StandModelWeight.objects.filter(standModel_id=standModel_id)
        smw = serializers.serialize("json",smw)
        reslut['data'] = smw
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"]=500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')


def uploadNewStandDataset(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        type = req.GET.get("type")
        StandDataset.objects.create(data_type=type)
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"]=500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')
def createDataset(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        data = json.loads(req.body)
        name = data.get('name')
        limit = data.get('limit')
        user_id = data.get('user_id')
        standDataset_id = data.get('standDataset_id')
        type = data.get('type')
        model_type = data.get('model_type')
        DataSet.objects.create(name=name,limit=limit,user_id=user_id,standDataset_id=standDataset_id,type=type,model_type=model_type)
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"]=500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')
def importData(req):
    if req.method=='POST':
        reslut = {
            "code": 200,
            "info": "success",
            "data": []
        }
        try:
            formatType = req.GET.get("formatType")#zip/url/...
            if formatType=='zip':
                post = req.POST
                user_id = post.get("user_id")
                dataset_id = post.get("dataset_id")
                dataset = req.FILES.get("dataset", None)

                #获取对应的数据集信息
                name = DataSet.objects.filter(id=dataset_id).first().name
                standDataset_id = DataSet.objects.filter(id=dataset_id).first().standDataset_id
                type = DataSet.objects.filter(id=dataset_id).first().type
                data_type = StandDataset.objects.filter(id=standDataset_id).first().data_type

                #保存数据
                user_dataset_path = 'mysite/datasets/user'+user_id
                if not os.path.exists(user_dataset_path):
                    os.mkdir(user_dataset_path)
                if os.path.exists(user_dataset_path + "/" + name):#已经导入过
                    shutil.rmtree(user_dataset_path + "/" + name)
                f = zipfile.ZipFile(dataset)
                f.extractall(path=user_dataset_path + "/" + name)

                #判断数据集是否满足特定格式要求
                isMeet = False
                isMeet = isMeetStru(data_type,type,dataset_path=user_dataset_path + "/" + name)
                if not isMeet:
                    shutil.rmtree(user_dataset_path + "/" + name)
                    reslut["code"] = 500
                    reslut["info"] = '文件不满足格式要求'
                    return JsonResponse(reslut, safe=False, content_type='application/json')
                #将信息写入数据库
                size = dataset.size/1024
                path = user_dataset_path + "/" + name
                total_num,label_num = getTotalAndLabelNum(data_type,type,dataset_path=user_dataset_path + "/" + name)
                DataSet.objects.filter(id=dataset_id).update(size=size,path=path,total_num=total_num,label_num=label_num)
                return JsonResponse(reslut, safe=False, content_type='application/json')
            reslut["code"] = 500
            reslut["info"] = 'formatType未知'
            return JsonResponse(reslut, safe=False, content_type='application/json')
        except Exception as e:
            print(e)
            reslut["code"]=500
            reslut["info"] = 'failed'
            return JsonResponse(reslut, safe=False, content_type='application/json')

def trainModel(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        if req.method == 'POST':
            data = json.loads(req.body)
            model_id = data.get("model_id")
            params = data.get("params")#用json字符串存起来的训练参数,eg:{"epoch":100}

            path1 = os.path.abspath('.')

            #查询得到网络地址和数据集地址
            model = Model.objects.filter(id=model_id).first()
            user_id = model.user.id
            dataset_path = path1+"/"+model.dataSet.path
            standmodel_path = model.standModel.net_path
            standmodel_params = model.standModel.params
            standmodel_params = json.loads(standmodel_params)
            #获得训练参数
            tempDict = {}
            for param in standmodel_params:
                pn = param.get('name')
                tempDict[pn] = params.get(pn)
            #拼接训练语句
            if not os.path.exists("mysite/modelWeights/user"+str(user_id)):
                os.makedirs("mysite/modelWeights/user"+str(user_id))
            if not os.path.exists("mysite/modelLogs/user" + str(user_id)):
                os.makedirs("mysite/modelLogs/user" + str(user_id))
            weight_path = path1+"/mysite/modelWeights/user"+str(user_id)+"/"+model.name
            log_path = path1+"/mysite/modelLogs/user"+str(user_id)+"/"+model.name
            if not os.path.exists(weight_path):
                os.makedirs(weight_path)
            # if os.path.exists(log_path):
            #     shutil.rmtree(log_path)
            if os.path.exists(log_path):
                shutil.rmtree(log_path)
                os.makedirs(log_path)
            if not os.path.exists(log_path):
                os.makedirs(log_path)

            train_script = 'python {}/train.py --inputs {} --weight_save_path {} --loss_save_path {}'.format(standmodel_path,dataset_path,weight_path,log_path)
            for key in tempDict.keys():
                train_script = train_script + ' --' + key +' '+str(tempDict.get(key))
            proc=None
            try:
                proc = subprocess.Popen(train_script, shell=True)
                repPro = Model.objects.filter(process = proc.pid)
                while len(repPro) > 0:
                    killProcTree(proc)
                    proc = subprocess.Popen(train_script, shell=True)
            except:
                Model.objects.filter(id=model_id).update(process=proc.pid, weight=weight_path,
                                                         params=json.dumps(tempDict), status=4)
            #获取进程的创建时间
            p = psutil.Process(proc.pid)
            atime = p.create_time()
            timeArray = time.localtime(atime)
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

            Model.objects.filter(id=model_id).update(process=proc.pid,weight=weight_path,params=json.dumps(tempDict),status=1,train_time=otherStyleTime,loss=log_path)
            return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def createModel(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        if req.method == 'POST':
            data = json.loads(req.body)
            name = data.get('name')
            status = 0
            limit = data.get('limit')
            standModel_id = data.get('standModel_id')
            user_id = data.get('user_id')

            Model.objects.create(name=name,status=status,limit=limit,standModel_id=standModel_id,user_id=user_id)
            return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def datasetToModel(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        data = req.GET
        model_id = data.get("model_id")
        dataset_id = data.get("dataset_id")
        Model.objects.filter(id=model_id).update(dataSet_id=dataset_id)
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def stopTrain(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }

    try:
        model_id = req.GET.get('model_id')
        #获取pid
        model = Model.objects.filter(id=model_id).first()
        pid = model.process

        #判断进程是否存在
        if not psutil.pid_exists(pid):
            reslut["code"] = 500
            reslut["info"] = '已训练完成'
            Model.objects.filter(id=model_id).update(status=2)
            return JsonResponse(reslut, safe=False, content_type='application/json')

        #杀死进程树
        try:
            killProcTree(pid)
        finally:
            Model.objects.filter(id=model_id).update(status=3)#修改为训练终止状态
            return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def selectAllTrain(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        user_id = req.GET.get('user_id')
        #先查询所有status=1(正在训练)的模型
        models = Model.objects.filter(user_id=user_id,status=1)
        #遍历这些models,获取pid
        for model in models:
            pid = model.process
            model_id = model.id
            #查询pid的状态,如果不存在，则更新状态
            if not psutil.pid_exists(pid):
                Model.objects.filter(id=model_id).update(status=2)
            else:
                p = psutil.Process(pid)
                if p.cpu_percent(None) < 2: #CPU占用率小,说明不是训练进程
                    Model.objects.filter(id=model_id).update(status=2)
        #获取所有的model并返回
        returnModels = Model.objects.filter(user_id=user_id)
        returnModels = serializers.serialize("json",returnModels)
        reslut['data'] = returnModels
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def selectAllDataset(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        user_id = req.GET.get('user_id')
        datasets = DataSet.objects.filter(user_id=user_id).values("id", "label_num", "limit", "model_type", "name", "path", "size", "total_num", "type", "user_id","standDataset__data_type")
        tempList = []
        for dataset in datasets:
            tempList.append(dataset)
        reslut['data'] = tempList
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def selectAllStandDataset(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        datasets = StandDataset.objects.all()
        datasets = serializers.serialize("json",datasets)
        reslut['data'] = datasets
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def selectDataTypeById(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        standDataset_id = req.GET.get('standDataset_id')
        sms = StandDataset.objects.filter(id=standDataset_id)
        sms = serializers.serialize("json",sms)
        reslut['data'] = sms
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def selectAllModel(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        user_id = req.GET.get('user_id')
        #先查询所有status=1(正在训练)的模型
        models = Model.objects.filter(user_id=user_id,status=1)
        #遍历这些models,获取pid
        for model in models:
            pid = model.process
            model_id = model.id
            #查询pid的状态,如果不存在，则更新状态
            if not psutil.pid_exists(pid):
                Model.objects.filter(id=model_id).update(status=2)
            else:
                # 获取进程的创建时间
                p = psutil.Process(pid)
                atime = p.create_time()
                timeArray = time.localtime(atime)
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                train_time = model.train_time
                if train_time != otherStyleTime:
                    Model.objects.filter(id=model_id).update(status=2)

        models = Model.objects.filter(user_id=user_id).values("id", "name", "status", "process", "weight", "limit", "params", "dataSet", "standModel", "standModel__params","standModel__name", "standModel__type","dataSet__id","dataSet__name")
        tempList = []
        for model in models:
            tempList.append(model)
        reslut['data'] = tempList
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def deleteDataset(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        dataset_id = req.GET.get('dataset_id')
        dataset = DataSet.objects.get(id=dataset_id)
        path = dataset.path
        num,_ = dataset.delete()
        if num != 0 and path!='0' and path:
            shutil.rmtree(path)
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')\

def selectConnectDataset(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        user_id = req.GET.get('user_id')
        model_type = req.GET.get('model_type')

        datasets = DataSet.objects.filter((Q(user_id=user_id) | Q(limit=0)) & Q(model_type=model_type) & (Q(type=0) | Q(type=3) | Q(type=4)))
        reslut['data'] = serializers.serialize("json",datasets)
        # reslut['data'] = list(datasets)
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def getWeightName(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        model_id = req.GET.get('model_id')
        weight_path = Model.objects.get(id=model_id).weight

        #遍历weight_path下的文件
        weight_name_arr = []
        for name in os.listdir(weight_path):
            hz = os.path.splitext(name)[-1][1:]
            if  hz== "pt" or hz == 'pth' or hz == 'pkl':
                weight_name_arr.append(name)
        reslut['data'] = weight_name_arr
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def useTrainedModelToPredictImage(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    path=""
    predict_file=None
    if req.method == 'POST':
        try:
            post = req.POST
            user_id = post.get('user_id')
            model_id = post.get('model_id')
            predict_file = req.FILES.get("predict_file", None)
            weight_name = post.get('weight_name')

            # 将用户上传图片保存成文件
            path = 'mysite/Temp/user' + user_id
            writeFile(predict_file, path, predict_file.name)

            # 获取预测权重的地址和网络结构的地址
            model = Model.objects.filter(id=model_id).first()
            weight_path = model.weight + '/' +  weight_name
            net_path = model.standModel.net_path

            dataset = DataSet.objects.filter(id=model.dataSet_id).first().standDataset.data_type
            # 运行系统命令将预测结果保存成文件
            # 判断是否有用户预测文件夹,如果没有则创建
            user_path = "mysite/predict/user" + user_id
            if not os.path.exists(user_path):
                os.makedirs(user_path)
            os.system("python {}/predict.py --input {} --ckpt {} --save_val_results_to {} --dataset {}".
                      format(net_path, path + "/" + predict_file.name, weight_path, user_path, dataset))
            reslut['data'] = "user" + user_id + "/" + os.path.splitext(predict_file.name)[0]  # 返回预测结果文件路径
            return JsonResponse(reslut, safe=False, content_type='application/json')

        except Exception as e:
            print(e)
            reslut["code"] = 500
            reslut["info"] = 'failed'
            return JsonResponse(reslut, safe=False, content_type='application/json')
        finally:
            if predict_file:
                os.remove(path + "/" + predict_file.name)
    else:
        reslut["code"] = 500
        reslut["info"] = '请求方法有误'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def useTrainedModelToPredictZip(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    path = ""
    zipTempPath = ""
    predictTempPath = ""
    predict_file = None
    if req.method == 'POST':
        try:
            post = req.POST
            model_id = post.get("model_id")
            weight_name = post.get("weight_name")
            predict_file = req.FILES.get("predict_zip", None)
            user_id = post.get("user_id")
            # 获取文件后缀
            suffix = os.path.splitext(predict_file.name)[-1]
            if suffix != '.zip':
                reslut['code'] = 500
                reslut['info'] = "请求方法有误"
                return JsonResponse(reslut, safe=False, content_type='application/json')
            # 解压缩文件进指定文件夹
            f = zipfile.ZipFile(predict_file)
            zipTempPath = 'mysite/Temp/user' + user_id
            if not os.path.exists(zipTempPath):
                os.makedirs(zipTempPath)
            zipTempPath = 'mysite/Temp/user' + user_id + "/" + os.path.splitext(predict_file.name)[0]
            f.extractall(path=zipTempPath)

            model = Model.objects.filter(id=model_id).first()
            weight_path = model.weight + '/' + weight_name
            net_path = model.standModel.net_path
            dataset = DataSet.objects.filter(id=model.dataSet_id).first().standDataset.data_type
            user_path = "mysite/predict/user" + user_id
            if not os.path.exists(user_path):
                os.makedirs(user_path)

            predictTempPath = user_path + "/" + os.path.splitext(predict_file.name)[0]
            # 在用户预测文件夹下创建压缩包同名文件夹
            if not os.path.exists(predictTempPath):
                os.makedirs(predictTempPath)

            # 遍历所有的样本,进行批量预测
            for file in os.listdir(zipTempPath):
                file_path = os.path.join(zipTempPath, file)
                print("python {}/predict.py --input {} --ckpt {} --save_val_results_to {} --dataset {}".
                          format(net_path, file_path, weight_path, predictTempPath, dataset))
                os.system("python {}/predict.py --input {} --ckpt {} --save_val_results_to {} --dataset {}".
                          format(net_path, file_path, weight_path, predictTempPath, dataset))

            # 将预测结果保存为zip文件
            zipDirectory(predictTempPath)
            # 删除预测文件夹
            shutil.rmtree(predictTempPath)
            # 删除临时上传文件
            shutil.rmtree(zipTempPath)
            reslut['data'] = "user" + user_id + "/" + os.path.splitext(predict_file.name)[0] + ".zip"
            return JsonResponse(reslut, safe=False, content_type='application/json')

        except Exception as e:
            print(e)
            reslut["code"] = 500
            reslut["info"] = 'failed'
            return JsonResponse(reslut, safe=False, content_type='application/json')
    else:
        reslut["code"] = 500
        reslut["info"] = '请求方法有误'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def getAllPubicModel(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        model_type = req.GET.get('model_type')
        user_id = req.GET.get('user_id')
        models = Model.objects.filter(Q(standModel__type=model_type) & ~Q(user_id=user_id) & Q(limit=0))
        models = serializers.serialize('json',models)
        reslut['data'] = models

        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def importDataFromUrl(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        post = json.loads(req.body)
        user_id = post.get("user_id")
        dataset_id = post.get("dataset_id")
        url = post.get("url")
        format = post.get("format")
        zip_save_path = ''

        if format == 'zip':
            # 获取对应的数据集信息
            name = DataSet.objects.filter(id=dataset_id).first().name
            standDataset_id = DataSet.objects.filter(id=dataset_id).first().standDataset_id
            type = DataSet.objects.filter(id=dataset_id).first().type
            data_type = StandDataset.objects.filter(id=standDataset_id).first().data_type

            user_dataset_path = 'mysite/datasets/user' + str(user_id)
            if not os.path.exists(user_dataset_path):
                os.mkdir(user_dataset_path)
            if os.path.exists(user_dataset_path + "/" + name):  # 已经导入过
                shutil.rmtree(user_dataset_path + "/" + name)
            # 引用 requests文件
            import requests
            # 把下载地址发送给requests模块
            f = requests.get(url)
            # 下载文件
            zip_save_path = user_dataset_path + '/' + name + '.'+format
            with open(user_dataset_path + '/' + name + '.'+format, "wb") as code:
                code.write(f.content)
                code.close()
            f = zipfile.ZipFile(zip_save_path)
            f.extractall(path=user_dataset_path + "/" + name)
            f.close()

            length = len(os.listdir(user_dataset_path + "/" + name))
            dataset_path = user_dataset_path + "/" + name
            if length == 1:
                dataset_path=user_dataset_path + "/" + name + os.listdir(user_dataset_path + "/" + name)[0]
            # 判断数据集是否满足特定格式要求
            isMeet = False
            isMeet = isMeetStru(data_type, type, dataset_path=dataset_path)
            if not isMeet:
                shutil.rmtree(user_dataset_path + "/" + name)
                reslut["code"] = 500
                reslut["info"] = '文件不满足格式要求'
                return JsonResponse(reslut, safe=False, content_type='application/json')

            size = os.path.getsize(zip_save_path)
            path = user_dataset_path + "/" + name
            total_num, label_num = getTotalAndLabelNum(data_type, type, dataset_path=dataset_path)
            DataSet.objects.filter(id=dataset_id).update(size=size, path=path, total_num=total_num, label_num=label_num)
            if os.path.exists(zip_save_path):
                os.remove(zip_save_path)
            return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def getLossData(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        user_id = req.GET.get("user_id")
        type = req.GET.get("model_type")

        lossArr = Model.objects.filter(Q(user_id=user_id) & ~Q(status=0) & Q(standModel__type=type)).values("id","loss")
        tempArr = {}
        for aLoss in lossArr:
            #解析txt文件
            names = os.listdir(aLoss["loss"])
            if not len(names) > 0:
                tempArr[aLoss['id']] = []
                break
            f = open(aLoss["loss"]+"/"+names[0])
            lines = f.readlines()
            f.close()
            data = []
            for line in lines:
                data.append(float(line.strip()))
            tempArr[aLoss['id']]=data
        reslut['data'] = tempArr
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def deleteModel(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        user_id = req.GET.get('user_id')
        model_id = req.GET.get('model_id')

        model = Model.objects.filter(id=model_id).first()
        pid = model.process

        #判断模型的状态
        if model.status == 1:#模型正在训练，需要先终止训练
            # 判断进程是否存在
            if psutil.pid_exists(pid):
                # 杀死进程树
                try:
                    killProcTree(pid)
                finally:
                    # 删除模型的文件
                    weight_path = "mysite/modelWeights/user" + str(user_id) + "/" + model.name
                    log_path = "mysite/modelLogs/user" + str(user_id) + "/" + model.name
                    if os.path.exists(weight_path):
                        shutil.rmtree(weight_path)
                    if os.path.exists(log_path):
                        shutil.rmtree(log_path)
                    # 从数据库中移除改项
                    model.delete()
                    return JsonResponse(reslut, safe=False, content_type='application/json')
        # 删除模型的文件
        weight_path = "mysite/modelWeights/user" + str(user_id) + "/" + model.name
        log_path = "mysite/modelLogs/user" + str(user_id) + "/" + model.name
        if os.path.exists(weight_path):
            shutil.rmtree(weight_path)
        if os.path.exists(log_path):
            shutil.rmtree(log_path)
        # 从数据库中移除改项
        model.delete()
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def getAllModelName(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        reslut['data'] = modelsName
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def getAllStandModelById(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        admin_id = req.GET.get('admin_id')
        sms = StandModel.objects.filter(user_id = admin_id)
        sms = serializers.serialize('json',sms)
        sms = json.loads(sms)
        reslut['data'] = sms
        return JsonResponse(reslut, safe=False, content_type='application/json')

    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')

def getStandModelWeightById(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        standmodel_id = req.GET.get('standmodel_id')
        smsw = StandModelWeight.objects.filter(standModel__id = standmodel_id)
        smsw = json.loads(serializers.serialize('json',smsw))
        reslut['data'] = smsw
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')
def deleteStandModelWeightById(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        weight_id = req.GET.get('weight_id')
        weight_path = StandModelWeight.objects.filter(id=weight_id).first().weight_path
        #删除权重
        os.remove(weight_path)
        StandModelWeight.objects.filter(id=weight_id).delete()
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = 'failed'
        return JsonResponse(reslut, safe=False, content_type='application/json')