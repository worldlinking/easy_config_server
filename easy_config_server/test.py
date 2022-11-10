# written by cy on 2022-11-09 15:34

# Create your tests here.
# written by cy on 2022-11-09 15:34
import os
os.system("python mysite/Nets/net/admin1/deeplab/predict.py --input mysite/Nets/net/admin1/deeplab/datasets/data/cityscapes/leftImg8bit/train/bremen/bremen_000000_000019_leftImg8bit.png  --dataset cityscapes --model deeplabv3plus_mobilenet --ckpt mysite/Nets/net/admin1/deeplab/checkpoints/best_deeplabv3plus_mobilenet_cityscapes_os16.pth --save_val_results_to mysite/Nets/net/admin1/deeplab/test_results")

