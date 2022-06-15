# PROJECT TEAM3 (WITH)
자살 고위험군 대상자들의 위험한 시기 및 징후를 파악하여 관련 기관이나 보호자에게 알림을 주는 시스템

# FUNCTION
- 실시간 위험객체 검출
- 대상자의 음성을 인식, 감정분류 후 징후 포착
- 대상자의 현재 및 일정 기간 감정 수치 시각화

# HOW TO USE COMMAND "python manage.py result"
1. 구글drive - KoBERT모델 다운로드
https://drive.google.com/file/d/1uChid_GJ_X9AmF1wMqZyb1dxcN_jXdjc/view?usp=sharing
* file: model_state_dict.pt

2. 디렉토리 경로
* mysite/content/ai_model/*
* 폴더 생성하고 모델 옮기기

3. pip install -r requirements.txt
4. pip install --use-deprecated=legacy-resolver git+https://git@github.com/SKTBrain/KoBERT.git@master

# WHAT iS COMMAND "python manage.py emotion"

* 언어적 신호
논문을 근거로 한 자살 위험 단어를 8개의 사전으로 나누고 각 사전마다 가중치를 정하여
텍스트에 해당 단어가 있으면 점수를 더하는 시스템
현재 일주일동안의 기간을 정하여 음성데이터를 텍스트화하여 분석함.

* 감정적 신호
사용 테이블 : result emotion 테이블
  DB에 저장된 텍스트 데이터를 KoBERT 모델을 통하여 11가지의 감정으로 분류하여 수치를 저장한 테이블

해당 테이블에서 11가지의 각 수치를 불러오고 부정적인 감정들에 위험도 가중치를 설정한다.

* 마지막으로 언어 위험도 점수 + 감정 위험도 점수를 합산하여 현재 300점 이상일 시 상태를 위험으로 변경
* 상태가 위험으로 변경되면 SMS 메신저로 해당 ID의 환자의 위험을 알림.
* 또한 관리자 페이지의 User List 페이지에서도 확인이 가능함.
