# written by cy on 2022-11-15 16:40
import os
def isMeetStru(data_type,type,dataset_path):
    """
    :param data_type: 对应的标准数据集类型
    :param type: 0：训练集+验证集，1：测试集， 4：训练集+测试集+验证集
    :param dataset_path:
    :return:是否满足标准数据集要求
    """
    if data_type=='coco':
        hasAnn = os.path.exists(dataset_path+'/'+'annotations')
        hasImages = os.path.exists(dataset_path+'/'+'images')
        hasLabels = os.path.exists(dataset_path+'/'+'labels')
        if not hasAnn or not hasLabels or not hasImages:
            return False
        if(type==0):
            hasImagesTrain2017 = os.path.exists(dataset_path+'/'+'images/train2017')
            hasLabelsTrain2017 = os.path.exists(dataset_path+'/'+'labels/train2017')
            if not hasImagesTrain2017 or not hasLabelsTrain2017:
                return False
            else:
                return True
    elif data_type == 'cityscapes':
        hasgtFine = os.path.exists(dataset_path+'/'+'gtFine')
        hasLeftImg8bit = os.path.exists(dataset_path+'/'+'hasLeftImg8bit')
        if not hasgtFine or not hasLeftImg8bit:
            return False
        if type == 0:
            return os.path.exists(dataset_path+'/'+'gtFine/train') and os.path.exists(dataset_path+'/'+'gtFine/val') and os.path.exists(dataset_path+'/'+'leftImg8bit/train') and os.path.exists(dataset_path+'/'+'leftImg8bit/val')
        return True
    elif data_type == 'shape':
        hasJPEGImages = os.path.exists(dataset_path + '/' + 'JPEGImages')
        hasJsons = os.path.exists(dataset_path + '/' + 'Jsons')
        if not hasJPEGImages or not hasJsons:
            return False
        if type == 0:
            return os.path.exists(dataset_path + '/' + 'Jsons/train_annotations.json') and os.path.exists(dataset_path + '/' + 'Jsons/val_annotations.json')