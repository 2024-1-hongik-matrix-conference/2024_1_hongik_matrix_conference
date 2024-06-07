# 이미지 처리 관련 library
from PIL import Image
# 파일 경로 관련 library & module
from os import listdir
from os.path import isfile, join

#원본 사진&label 관련 파일들이 있는 경로
dirpath=f'C:/Users/leeyu/Downloads/인튜웍스'
# 세부 데이터 중 과자와 관련된 건 들고오지 않기 위해 어느 폴더만을 선택할 지 기록
paths=[
    'dataset7_can',
    'dataset6_myeon',
    'dataset5_processed2',
    'dataset4_processed1',
    'dataset3_sauce',
]
# class 이름을 넣으면 encoding된 값이 나오도록 사용하는 dictionary
class_to_label={}
# encoding된 값을 넣으면 원 class 이름이 나오도록 사용하는 list
label_to_class=[]
# 각 원본 이미지에 대한 기본적인 정보 저장
# 각 원소는 ( 세부 데이터 분류(위 paths에 나눠진 분류에 해당)를 0~len(paths)-1 로 , 원본 이미지의 파일이름(전체경로는 X) )
files=[]
# 각 세부 분류에 상관없이 모든 class를 encoding하는 형태로 결정
# 제공된 데이터에서 class정보가 세부 분류마다 encoding이 된 형태라 중복 없이 통합시키기 위해 offset을 계산해야함
# 이를 위해 각 세부 분류별로 class의 수를 기록하는 list
label_cnt=[0 for _ in paths]
# 총 label 개수 (세부 분류 상관없이)
t_label_cnt=0


"""
제공된 데이터는 원본 이미지와 해당 이미지에 대한 정보가 같은 이름에 확장자만 jpg에서 txt로 바뀌어 있음
이를 처리하기 위해 각 세부 분류 폴더에서 모든 .txt로 끝나는 파일에 대해
대응되는 jpg 파일이 있는지를 검사
대응되는 jpg 파일이 있다면 데이터라고 판단하고 files[]에 명세에 맞게 값 저장
"""
for adj in enumerate(paths):
    fpath=f'{dirpath}/{adj[1]}/label/'
    for f in listdir(fpath):
        if isfile(fpath+f) and f.endswith('txt'):
            if isfile(fpath+f[:-3]+'jpg'):
                files.append((adj[0],f[:-4]))

    # 각 세부 폴더 속에 'obj.names' 파일이 있는데, 이 안에 encoding된 label과 그에 대응하는 실제 class명(이 경우에는 실제 상품의 이름)이 저장됨
    # 따라서 이 파일을 읽어 label에 대한 정보를 간결하게 저장할 수 있도록 정리하고자 함
    if isfile(fpath + 'obj.names'):
        with open(fpath+'obj.names', encoding='utf-8') as labels_txt:
            labels=[line for line in labels_txt.read().split("\n")]
            for label_name in labels:
                label_to_class.append(label_name)
                class_to_label[label_name] = t_label_cnt
                t_label_cnt += 1
                label_cnt[adj[0]] +=1

#label_cnt[] 의 맨 앞에 0을 원소로 넣어 쉽게 offset 계산을 할 수 있도록 만듬
label_cnt=[0]+label_cnt

instance_cnt =0 
# 절단된 이미지의 파일 이름 목록
X=[]
# X에 대응되어 각 이미지의 label & class명 목록
y=[]
# print(len(files))
# 진행률 확인용 instance 수 측정 변수
file_cnt=0
for fp in files[:]:
        # 해당 원본 이미지에 대해 확장자 없는 전체 경로
        full_path=f'{dirpath}/{paths[fp[0]]}/label/{fp[1]}'
        # 원본 이미지 열기
        im = Image.open(f'{full_path}.jpg')
        # 이미지 너비&높이
        width, height = im.size
        file_cnt+=1
        if file_cnt % 100 == 0:
            print(f"Run count : {instance_cnt}")
        # 해당 원본 이미지에 대한 정보가 기록되어있는 txt 파일
        with open(f'{full_path}.txt') as pos_txt:
            pos_info = [line.split() for line in pos_txt.readlines()]
            # 각 줄은
            # 정답label, 중심x좌표 (0~1), 중심y좌표 (0~1), 너비(0~1), 높이(0~1) 쌍으로 저장되어있음
            for pos in enumerate(pos_info):
                lab = int(pos[1][0]) + sum(label_cnt[:fp[0]+1]) #절단된 해당 이미지의 target label = 해당되는 세부 분류에서의 encoding 된 label + sum(이전 세부 분류들의 class 수)
                posx,posy,sx,sy = list(map(float, pos[1][1:])) # 중심x좌표 (0~1), 중심y좌표 (0~1), 너비(0~1), 높이(0~1) 정보 추출
                if 1/2 < (width*sx)/(height*sy) < 2/1: #너비:높이가 1:2 ~ 2:1의 사이일 때만 적합한 데이터로 인정함
                    left = width*(posx-0.5*sx) # 자를려는 부분의 원본 이미지에서의 왼쪽 변의 x좌표
                    top = height*(posy-0.5*sy) # 위쪽 변의 y좌표
                    right = width*(posx+0.5*sx) # 오른쪽 변의 x좌표
                    bottom = height*(posy+0.5*sy) # 아래쪽 변의 y좌표
                    im1 = im.crop((left, top, right, bottom)) # 원하는 부분만 자르기
                    X.append(instance_cnt)
                    y.append(lab)
                    im1.save(f'C:/홍대/Matrix/Advanced/Conference/cropped_images/{instance_cnt}.png','PNG') # 자른 부분 새 이미지로 저장
                    instance_cnt += 1


#label.txt에 각 X에 대응되는 y값(encoding된 label과 실제 class명) 기록
dataset_txt = open('C:/홍대/Matrix/Advanced/Conference/cropped_images/label.txt','w')
dataset_txt.write('\n'.join(map(lambda x : f'{x} {label_to_class[x]}',y)))
print(list(map(lambda x: (x[0],label_to_class[x[1]]),zip(X,y))))
dataset_txt.close()


# 각 encoding된 label의 실제 class명을 class_list.txt에 기록
dataset_txt = open('C:/홍대/Matrix/Advanced/Conference/cropped_images/class_list.txt','w')
dataset_txt.write('\n'.join(label_to_class))
dataset_txt.close()