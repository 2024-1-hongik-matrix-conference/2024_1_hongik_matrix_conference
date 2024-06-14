from os import listdir, makedirs
from os.path import isfile, join, exists
from PIL import Image
import random as rand
import shutil

"""
모델을 학습시키는데에 있어 데이터의 클래스의 수가 매우 많다.
따라서 그냥 무작위로 이미지를 가져오게 되면 분류해야 하는 클래스는 너무 많고, 각 클래스에 해당되는 데이터의 절대적인 수도 너무 적어진다.
결국 모델에게 가장 적합한 데이터셋은 감당할 수 있을 정도로 작은 클래스 수와 각 클래스당 가지고 있는 모든 데이터를 가져오는 식으로 샘플링하는 것이 가장 적절하다고 생각했다.


더 간단하게:
클래스의 수가 가지고있는 데이터셋의 크기에 비해 너무 많은 거 같음
그래서 테슽용 데이터셋을 만들 때 이미지를 일정 수 뽑는 게 아니라 정답 레이블을 몇개 뽑고
그 레이블에 해당하는 모든 이미지를 모두 다 들고오는 방식이 적절할 거 같다.

예를 들어 데이터셋 중 무작위로 사진 1000개를 뽑는 방식이 아니라
많은 클래스 중 "전복죽, 신라면, 토마토 소스"가 무작위로 뽑히면
전체 데이터셋에 있는 모든 전복죽, 신라면, 토마토 소스 사진을 들고오는 것이다.

"""



dirpath ='C:\홍대\Matrix\Advanced\Conference\cropped_images' #이미지를 가져올 경로
y_path = 'label.txt' #이미지 target 정보가 저장되어있는 파일
class_path = 'class_list.txt' #전체 class 목록이 저장되어있는 파일
N=5 # 샘플링할 class 수
sample_label=[]
target_dir = './test_dataset/padding'# 샘플링된 데이터를 저장할 경로
shutil.rmtree(target_dir,ignore_errors=True) # 이미 경로에 무언가 있다면 먼저 다 지움
X = [f for f in listdir(dirpath) if f.endswith('png')] # 이미지 파일 모음
label_list = []
y=[]
#target 레이블 저장
with open(f'{dirpath}/{y_path}','r') as label_txt:
    y=list(map(lambda x: int(x.split()[0]),label_txt.readlines()))
    label_txt.close()

#클래스 목록 저장
with open(f'{dirpath}/{class_path}','r') as class_txt:
    label_list=class_txt.readlines()
    class_txt.close()


rand.seed(42) # 난수 생성기 시드 설정
sample_X = []
sample_label = rand.choices(list(range(len(label_list))),k=N) # 클래스 목록에서 N개의 레이블 무작위 샘플링
print(sample_label)
makedirs(f'{target_dir}',exist_ok=True) # 재샘플링된 파일들 저장할 경로 폴더 생성
with open(f'{target_dir}/{y_path}','w+') as sample_label_txt :
    for data in enumerate(X): #원 데이터셋의 이미지들에 대하여
        if y[int(data[1][:-4].split()[0])] in sample_label: # 만약 해당 이미지의 target 레이블이 선택된 레이블 중 하나라면 추출&재가공

            img = Image.open(f'{dirpath}/{data[1]}')
            width, height = img.size


            # 중심을 기준으로 가능한 크게 정사각형으로 자름
            # min_L = min(width, height)
            # imgn = img.crop((width/2-min_L/2, height/2-min_L/2, width/2+min_L/2, height/2+min_L/2))

            # 전체 이미지에 검은색 영역을 붙여 정사각형 이미지로 만듬
            max_L = max(width, height)
            imgn = Image.new("RGB",(max_L, max_L),'black')
            imgn.paste(img,((max_L-width)//2,(max_L-height)//2))


            # 이미지를 100X100으로 rescale
            imgn.thumbnail((100,100),Image.Resampling.LANCZOS)
            imgn.save(f'{target_dir}/{len(sample_X)}.jpg') # 가공된 이미지 저장
            sample_X.append(data[0])
            sample_label_txt.write(str(y[int(data[1][:-4])])+'\n')# 샘플링된 이미지의 target 데이터 기록
    sample_label_txt.close()
print(f"Total data : {len(X)} \t Sampled : {len(sample_X)}")
# print(sample_X)