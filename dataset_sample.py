from os import listdir, makedirs
from os.path import isfile, join, exists
from PIL import Image
import random as rand
import shutil

"""
cropped(center-cropped) : 중심을 기준으로 최대한 큰 정사각형으로 자른 사진
padding : 중심을 기준으로 사진을 모두 담을 수 있는 가장 작은 정사각형을 만들고, 그 빈칸을 검은색으로 채움
"""


dirpath ='C:\홍대\Matrix\Advanced\Conference\cropped_images' #이미지를 가져올 경로 
y_path = 'label.txt' #이미지 target 정보가 저장되어있는 파일
class_path = 'class_list.txt' #전체 class 목록이 저장되어있는 파일
N=1000# 총 샘플링할 instance 수
cropped_target_dir = './test_dataset/center_crop'# 샘플링된 center-cropped 데이터를 저장할 경로
padding_target_dir = './test_dataset/padding'# 샘플링된 padding 데이터를 저장할 경로
# 이미 경로에 무언가 있다면 먼저 다 지움
shutil.rmtree(cropped_target_dir,ignore_errors=True)
shutil.rmtree(padding_target_dir,ignore_errors=True) 
X = [f for f in listdir(dirpath) if f.endswith('png')] # 이미지 파일 모음
label_list = []
y=[]
#target 레이블 저장
with open(f'{dirpath}/{y_path}','r') as label_txt:
    y=list(map(lambda x: int(x.split()[1]),label_txt.readlines()))
    label_txt.close()

#클래스 목록 저장
with open(f'{dirpath}/{class_path}','r') as class_txt:
    label_list=class_txt.readlines()
    class_txt.close()

print(len(X))
rand.seed(42) # 난수 생성기 시드 설정
sample_X_path = rand.choices(X,k=N) # 데이터 instance 목록에서 N개의 레이블 무작위 샘플링
sample_X =[]
print(sample_X_path)
# 재샘플링된 파일들 저장할 경로 폴더 생성
makedirs(f'{cropped_target_dir}',exist_ok=True) 
makedirs(f'{padding_target_dir}',exist_ok=True) 
with open(f'{cropped_target_dir}/{y_path}','w+') as cropped_label_txt :
    with open(f'{padding_target_dir}/{y_path}','w+') as padding_label_txt :
        for data in enumerate(sample_X_path): #원 데이터셋의 이미지들에 대하여
            cur_image_label = y[int(data[1][:-4])]
            img = Image.open(f'{dirpath}/{data[1]}')
            width, height = img.size


            # 중심을 기준으로 가능한 크게 정사각형으로 자름
            min_L = min(width, height)
            imgn1 = img.crop((width/2-min_L/2, height/2-min_L/2, width/2+min_L/2, height/2+min_L/2))

            # 전체 이미지에 검은색 영역을 붙여 정사각형 이미지로 만듬
            max_L = max(width, height)
            imgn2 = Image.new("RGB",(max_L, max_L),'black')
            imgn2.paste(img,((max_L-width)//2,(max_L-height)//2))


            # 이미지를 200X200으로 rescale
            imgn1.thumbnail((200,200),Image.Resampling.LANCZOS)
            imgn2.thumbnail((200,200),Image.Resampling.LANCZOS)
            # 가공된 이미지 저장
            imgn1.save(f'{cropped_target_dir}/{len(sample_X)} {cur_image_label}.png') 
            imgn2.save(f'{padding_target_dir}/{len(sample_X)} {cur_image_label}.png') 
            sample_X.append(data[0])
            # 샘플링된 이미지의 target 데이터 기록
            cropped_label_txt.write(str(cur_image_label)+'\n')
            padding_label_txt.write(str(cur_image_label)+'\n')
        cropped_label_txt.close()
        padding_label_txt.close()