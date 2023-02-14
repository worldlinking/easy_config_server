# written by cy on 2023-02-13 19:33
import os
def entryAnns(path,folder,imgName,imgSize,standDataset,Anns):
    if(standDataset == 'coco'):
        imgWidth = imgSize[0]
        imgHeight = imgSize[1]
        name = os.path.splitext(imgName)[0]
        file = open(path + '/labels/' + folder + "/" + name + '.txt', 'w')
        for ann in Anns:
            center_x = ann['leftX'] +  ann['width']/2
            center_y = ann['topY'] +  ann['height']/2

            center_x = center_x/imgWidth
            center_y = center_y/imgHeight
            width = ann['width']/imgWidth
            height = ann['height']/imgHeight
            file.write(str(ann['index']) + " " + str(center_x) + ' ' + str(center_y) + ' ' + str(width) + ' ' + str(height) + "\n")
        file.close()


