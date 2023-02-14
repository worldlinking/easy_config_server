# written by cy on 2023-02-08 10:41
import os
def getImageList(path,standDataset):
    if(standDataset == 'coco'):
        imageList = {'train2017':[]}
        #获得训练集中的图片信息
        trainPath = path + "/images/train2017"
        trainLabelPath = path + "/labels/train2017"
        files = os.listdir(trainPath)
        for file in files:
            labelName = file.split('.')[0] + ".txt"
            #查询是否标注
            hasLabeled = os.path.exists(trainLabelPath+ "/" +labelName)
            if(hasLabeled):
                imageList['train2017'].append({file:1})
            else:
                imageList['train2017'].append({file:0})
        valPath = path + "/images/val2017"
        valLabelPath = path + "/labels/val2017"
        if(os.path.exists(valPath)):
            imageList['val2017'] = []
            files = os.listdir(valPath)
            for file in files:
                labelName = file.split('.')[0] + ".txt"
                # 查询是否标注
                hasLabeled = os.path.exists(valLabelPath + "/" + labelName)
                if (hasLabeled):
                    imageList['val2017'].append({file: 1})
                else:
                    imageList['val2017'].append({file: 0})
        return imageList