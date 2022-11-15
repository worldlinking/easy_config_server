# written by cy on 2022-11-15 16:40
import os
def isMeetStru(data_type,type,dataset_path):
    """
    :param data_type: 对应的标准数据集类型
    :param type: 0：训练集，1：测试集，2：验证机，3：训练集+测试集 4：训练集+测试集+验证集
    :param dataset_path:
    :return:
    """
    if data_type=='coco':
        hasAnn = os.path.exists(dataset_path+'/'+'annotations')
        hasImages = os.path.exists(dataset_path+'/'+'images')
        hasLabels = os.path.exists(dataset_path+'/'+'labels')
        if not hasAnn or not hasLabels or not hasImages:
            return False
        if(type==0):
            return True