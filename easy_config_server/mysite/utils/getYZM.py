# written by cy on 2023-01-06 20:32
import random
def getYZM():
    # 生成四位随机数的验证码
    # 用来保存生成的随机数或字母
    list = ""
    # range(x)生成x个随机数的验证码
    for i in range(6):
        list+=str(random.randint(0, 9))
    return list


