# written by cy on 2022-11-15 17:10
import os
def getTotalAndLabelNum(data_type,type,dataset_path):
    """
    :param data_type: 对应的标准数据集类型
    :param type: 0：训练集+验证集，1：测试集， 4：训练集+测试集+验证集
    :param dataset_path:
    :return:样本数目和对应的标准数目
    """
    if data_type=='coco':
        if(type==0):
            total_num = len(os.listdir(dataset_path + "/images/train2017"))
            label_num = len(os.listdir(dataset_path + "/labels/train2017"))
            return total_num,label_num
    elif data_type=='cityscapes':
        if type==4 or type==0:
            total_num = len(os.listdir(dataset_path + "/gtFine/train"))+len(os.listdir(dataset_path + "/gtFine/val"))
            label_num = len(os.listdir(dataset_path + "/leftImg8bit/train"))+len(os.listdir(dataset_path + "/leftImg8bit/val"))
            return total_num,label_num
    elif data_type == 'shape':
        if type==0 or type==4:
            total_num = len(os.listdir(dataset_path + "/JPEGImages"))
            length1 = 0
            length2 = 0
            with open(dataset_path + "/Jsons/train_annotations.json", encoding='utf-8') as file_obj:
                contents = file_obj.read()
                length1 = contents.rstrip().count('jpg')
            with open(dataset_path + "/Jsons/val_annotations.json", encoding='utf-8') as file_obj:
                contents = file_obj.read()
                length2 = contents.rstrip().count('jpg')
            return total_num,length1+length2