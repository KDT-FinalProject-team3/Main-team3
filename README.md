# PROJECT TEAM3 (WITH)
자살 고위험군 대상자들의 위험한 시기 및 징후를 파악하여 관련 기관이나 보호자에게 알림을 주는 시스템

# FUNCTION
- 실시간 위험객체 검출
- 대상자의 음성을 인식, 감정분류 후 징후 포착
- 대상자의 현재 및 일정 기간 감정 수치 시각화

# HOW TO USE COMMAND "python manage.py emotion"
1. slack - KoBERT모델 다운로드
* file: model_state_dict.pt

2. 디렉토리 경로
* mysite/content/ai_model/*
* 폴더 생성하고 모델 옮기기

3. pip install -r requirements.txt
4. pip install --use-deprecated=legacy-resolver git+https://git@github.com/SKTBrain/KoBERT.git@master
