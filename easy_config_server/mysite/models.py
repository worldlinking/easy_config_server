from django.db import models

# Create your models here.
class User(models.Model):
    account = models.CharField(max_length=64,unique=True)
    pwd = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    type = models.SmallIntegerField() #用户类型,0为管理员,1为普通用户
    class Meta:
        db_table = "user"

#定义支持的标准数据集格式
class StandDataset(models.Model):
    data_type = models.CharField(max_length=64,unique=True)#标准数据集格式名称,coco\voc
    class Meta:
        db_table = "stand_dataset"

class DataSet(models.Model):
    name = models.CharField(max_length=255,unique=True)
    type = models.SmallIntegerField()#数据集类型,0:测试，1:测试，2：验证,3:同时包含训练测试集
    model_type = models.IntegerField(null=True,blank=True)#标识模型的种类,目标检测\实例分割
    path = models.CharField(max_length=255,null=True,blank=True)#存储路径
    size = models.IntegerField(null=True,blank=True)#数据集大小/kb
    format = models.CharField(max_length=64,null=True,blank=True)#格式
    total_num = models.IntegerField(null=True,blank=True)#总训练/验证/测试训练样本数目
    label_num = models.IntegerField(null=True,blank=True)#标注数目
    limit = models.SmallIntegerField()#权限,0:公有,1:私有
    #设置外键
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    standDataset = models.ForeignKey(StandDataset,on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "dataset"

class StandModel(models.Model):
    name=models.CharField(max_length=255,unique=True)
    params = models.CharField(max_length=255)
    net_path = models.CharField(max_length=255)#网络结构和初始化函数
    type = models.IntegerField()#标识模型的种类,目标检测\实例分割
    info = models.CharField(max_length=255,null=True,blank=True)#模型的其他信息
    #设置外键
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    standDataset = models.ForeignKey(StandDataset, on_delete=models.DO_NOTHING)
    class Meta:
        db_table = "standmodel"


class StandModelWeight(models.Model):
    weight_path = models.CharField(max_length=1000)
    dataset=models.CharField(max_length=255,blank=True,null=True)
    #设置外键
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    standModel = models.ForeignKey(StandModel,on_delete=models.CASCADE)
    class Meta:
        db_table = "standmodelweight"

class Model(models.Model):
    name = models.CharField(max_length=255,unique=True)
    status = models.SmallIntegerField()#模型状态,0:未开始训练，1：训练中，2：训练完成
    process = models.BigIntegerField(null=True,blank=True) #模型对应的进程号
    weight = models.CharField(max_length=255,null=True,blank=True) #权重文件路径
    limit = models.SmallIntegerField(null=True,blank=True)#权限,0:公有,1:私有
    params = models.CharField(max_length=255,null=True,blank=True)#训练参数
    #设置外键
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    dataSet = models.ForeignKey(DataSet,on_delete=models.CASCADE)
    standModel = models.ForeignKey(StandModel,on_delete=models.CASCADE)
    class Meta:
        db_table = "model"

