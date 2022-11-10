# written by cy on 2022-11-01 10:15
#写入文件到指定路径
import os
def writeFile(file,path,name):
    if not file:
        return False
    if not os.path.exists(path):
        os.mkdir(path)
    destination = open(path+'/'+name,'wb+')  #打开特定的文件进行二进制的写操作for chunk in myFile.chunks():分块写入文件
    for chunk in file.chunks():  # 分块写入文件
        destination.write(chunk)
    destination.close()
    return True