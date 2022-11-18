# written by cy on 2022-11-15 17:10
import os
def getTotalAndLabelNum(data_type,type,dataset_path):
    """
    :param data_type: 对应的标准数据集类型
    :param type: 0：训练集，1：测试集，2：验证机，3：训练集+测试集 4：训练集+测试集+验证集
    :param dataset_path:
    :return:样本数目和对应的标准数目
    """
    if data_type=='coco':
        if(type==0):
            total_num = len(os.listdir(dataset_path + "/images/train2017"))
            label_num = len(os.listdir(dataset_path + "/labels/train2017"))
            return total_num,label_num