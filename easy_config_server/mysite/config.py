# written by cy on 2022-11-01 10:01
type_path_map = ["objectDetection","SemanticSegmentation","InstanceDivision","singleCategory","multiCategory","sentimentCategory"]
modelsName = ["目标检测", "语义分割", "实例分割", '单标签文本分类', '多标签文本分类', '情感分析']
file_ip = 'http://localhost:8001/server_predict'

SECRET_KEY = 'configuration' # 定义秘钥，很重要，请勿泄露