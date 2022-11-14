from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect
import requests
from spider import models
from django import forms
import datetime
from django.http import JsonResponse


class TaskModelForm(forms.ModelForm):
    class Meta:
        model = models.Tasks
        fields = ["taskName", "siteName", "keyword"]


def taskJobList(request):
    result = {
        "code": 200,
        "info": "success",
        "data": []
    }
    try:
        queryset = models.Tasks.objects.all()
        get_url = 'http://localhost:6800/listjobs.json?project=weibo'
        get_response = requests.get(get_url)
        get_json = get_response.json()
        running = get_json['running']
        finished = get_json['finished']
        for obj in queryset:
            jobid = obj.jobid
            flag = False
            if len(jobid) != 0:
                for runTask in running:
                    if runTask["id"] == jobid:
                        obj.startTime = runTask["start_time"]
                        # now_ms = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                        now_ms = datetime.datetime.now()
                        obj.status = 'running'
                        obj.runtime = now_ms - datetime.datetime.strptime(obj.startTime, '%Y-%m-%d %H:%M:%S.%f')
                        obj.save()
                        flag = True
                        break
                if flag:
                    continue
                for finishTask in finished:
                    if finishTask["id"] == jobid:
                        obj.startTime = finishTask["start_time"]
                        obj.status = 'finished'
                        obj.endTime = finishTask["end_time"]
                        obj.runtime = datetime.datetime.strptime(obj.endTime,
                                                                 '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime.strptime(
                            obj.startTime, '%Y-%m-%d %H:%M:%S.%f')
                        obj.save()
                        break
        for obj in queryset:
            data = {'id': obj.id, 'taskName': obj.taskName, 'siteName': obj.siteName, 'keyword': obj.keyword,
                    'status': obj.status,
                    'statTime': obj.startTime, 'runtime': obj.runtime, 'endTime': obj.endTime}
            result["data"].append(data)
        return JsonResponse(result, safe=False, content_type='application/json')
    except Exception as e:
        result["code"] = 500
        result["info"] = "failed,reason:" + e
        return JsonResponse(result, safe=False, content_type='application/json')


def spiderRequest(request):
    result = {
        "code": 200,
        "info": "success",
        "data": []
    }
    if request.method == "POST":
        try:
            post = request.POST
            taskName = post.get('taskName')
            siteName = post.get('siteName')
            keyword = post.get('keyword')
            startdate = post.get('startdate')
            enddate = post.get('enddate')
            row_object = models.Tasks.objects.create(taskName=taskName, siteName=siteName, keyword=keyword)
            task_id = row_object.id
            post_url = 'http://127.0.0.1:6800/schedule.json'
            # if siteName == '微博':
            data = {'project': 'weibo', 'spider': 'search', 'key': keyword, 'task_id': task_id, 'startdate': startdate,
                    'enddate': enddate}
            post_response = requests.post(url=post_url, data=data)
            res_json = post_response.json()
            jobid = res_json['jobid']
            row_object.jobid = jobid
            row_object.save()
            return JsonResponse(result, safe=False, content_type='application/json')
        except Exception as e:
            result["code"] = 500
            result["info"] = "failed,reason:" + e
            return JsonResponse(result, safe=False, content_type='application/json')
    else:
        result["info"] = "请求方法有误"
        return JsonResponse(result, safe=False, content_type='application/json')


def itemList(request):
    # nid = int(request.GET['id'])
    nid = int(request.GET.get('id'))
    result = {
        "code": 200,
        "info": "success",
        "header": [],
        "data": [],
    }
    try:
        row_object = models.Tasks.objects.filter(id=nid).first()

        if row_object.siteName == '微博':
            queryset = models.weibo.objects.filter(task_id=nid)
            fields = models.weibo._meta.get_fields()
            fields = fields[:10]
        else:
            queryset = models.wyNews.objects.filter(task_id=nid)
            fields = models.wyNews._meta.get_fields()
        fieldName = []
        for field in fields:
            header = {}
            name = field.name
            fieldName.append(name)
            header["prop"] = name
            header["label"] = field.verbose_name
            result["header"].append(header)
        for obj in queryset:
            data = {}
            for i in fieldName:
                if i == 'task':
                    content = obj.task.siteName
                else:
                    content = getattr(obj, i)
                data[i] = content
            result["data"].append(data)
        return JsonResponse(result, safe=False, content_type='application/json')
    except Exception as e:
        result["code"] = 500
        result["info"] = "failed,reason:" + e
        return JsonResponse(result, safe=False, content_type='application/json')
