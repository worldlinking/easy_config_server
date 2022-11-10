import cv2
from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from mysite.models import User,DataSet,Model,StandModel,StandModelWeight
import os
import torch
from importlib import import_module
from mysite.config import type_path_map
from mysite.utils.writeFile import writeFile
import zipfile
import cv2 as cv
import skimage

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
            trainScript = req.FILES.get("trainScript", None)
            train_path = ""
            type = post.get("type")
            info = post.get("info")
            user_id = post.get("user_id")
            net = req.FILES.get("net", None)
            net_path = ""
            if not name and not params and not trainScript and not type and not info and not user_id and not net and not net_path:
                reslut["code"] = 500
                reslut["info"] = "请求参数有误!"
                return JsonResponse(reslut, safe=False, content_type='application/json')

            # 保存训练脚本文件
            isScriptWrite = True
            if trainScript is not None:
                #保存训练脚本文件,并保存路径进数据库
                pass

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
            if isNetWrite and isScriptWrite:
                #将数据写入数据库
                if(suffix == ".zip"):
                    StandModel.objects.create(name=name, params=params, train_path=train_path,
                                              net_path=path+ '/admin' + user_id+"/"+name, type=type, info=info,
                                              user_id=user_id)
                else:
                    StandModel.objects.create(name=name, params=params, train_path=train_path,
                                              net_path=net_path + "/" + name + suffix, type=type, info=info,
                                              user_id=user_id)
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
    if(req.method == "POST"):
        try:
            #获取请求参数
            post = req.POST
            standModel_id = post.get("standModel_id")
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
                StandModelWeight.objects.create(weight_path = path+'/'+standModelWeight.name,standModel_id=standModel_id,user_id=user_id)
            return JsonResponse(reslut, safe=False, content_type='application/json')
        except Exception as e:
            reslut["code"] = 500
            reslut["info"] = "failed,reason:"+e
            return JsonResponse(reslut, safe=False, content_type='application/json')

#3 使用管理员上传的标准模型权重进行预测
def useStandModelWeightImage(req):
    reslut = {
        "code": 200,
        "info": "success",
        "data": []
    }
    path=""
    predict_file=None
    try:
        post = req.POST
        weight_id = post.get("weight_id")
        predict_file = req.FILES.get("predict_file", None)
        user_id = post.get("user_id")

        print(weight_id)

        #将用户上传图片保存成文件
        path = 'mysite/Temp/user'+user_id
        writeFile(predict_file,path,predict_file.name)

        #获取预测权重的地址和网络结构的地址
        smw = StandModelWeight.objects.filter(id=weight_id).first()
        weight_path = smw.weight_path
        #正查网络结构地址
        net_path = StandModelWeight.objects.filter(id=weight_id).first().standModel.net_path

        #运行系统命令将预测结果保存成文件
        #判断是否有用户预测文件夹,如果没有则创建
        user_path = "mysite/predict/user"+user_id
        if not os.path.exists(user_path):
            os.makedirs(user_path)
        os.system("python {}/predict.py --input {}  --dataset cityscapes --model deeplabv3plus_mobilenet --ckpt {} --save_val_results_to {}".
                  format(net_path,path+"/"+predict_file.name,weight_path,user_path))
        #删除临时上传文件
        reslut['data'] = "user"+user_id+"/"+predict_file.name#返回预测结果文件路径
        return JsonResponse(reslut, safe=False, content_type='application/json')
    except Exception as e:
        print(e)
        reslut["code"] = 500
        reslut["info"] = "failed"
        return JsonResponse(reslut, safe=False, content_type='application/json')
    finally:
        if predict_file:
            os.remove(path+"/"+predict_file.name)
