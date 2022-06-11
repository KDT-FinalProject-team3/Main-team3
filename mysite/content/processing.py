from django.shortcuts import redirect, render
import paho.mqtt.client as mqtt
from paho.mqtt import client

from .kobert import KoBERT
from .models import InputSentence, ChatHistory

import time
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
from content.models import EmotionResult, User


class StatusJudgment:
    def __init__(self):
        self.death = ['죽음', '죽는', '절명', '임종', '죽다', '사망', '숨이', '숨통', '영면', '숨지', '숨졌', '돌아가시', '극단적',
                      "죽으려", '죽을', "떨어지고", "살기싫다", "죽고", "죽어", "끝났으", '뒤졌', "객사", "돌연사", "뒤졌", '뒈지', '뒈졌', '죽겠', '죽고싶다']
        self.suicide = ['자살']   # a3
        self.afterlife = ['천국', '지옥', '하늘나라', '다음생', '환생', '이번생', '하늘로', '저승', '저세상']
        self.self_Fulfilling_Prophecy = ["하는게", '차라리', '사라지면']
        self.suicide_method = ['자해', '목메달아', '목메', '가스로', '뛰어내릴', '투신', '분신', '방화', '불질러', '칼로', '칼', '올가미',
                               '수면제', '약으로', '독으로', '독약', '죽는법', '죽으려']
        self.self_deprecation = ['나따위', '고작', '겨우', '이거밖에', '병신', '한심한', '비참한', '장애인', '쓰레기', '이정도도',
                                 '따위', '필요없는', '틀렸어', '글렀어', '존재해선', '가치없는', '무가치한', '자괴감']
        self.physical_discomfort = ['불면증', '장애', '못자', '안와', '안움', '힘드냐', '힘들', '힘듦', '불편하다', '미칠']
        self.suicide_victim = ['자살한', '죽은', '죽었던', '돌아가신', '돌아가셨',"임종", "고인"]

        self.index_list = [self.death, self.suicide, self.afterlife, self.self_Fulfilling_Prophecy, self.suicide_method,
                           self.self_deprecation, self.physical_discomfort, self.suicide_victim]
        self.index_weight = [4, 5, 2, 3, 3, 4, 2, 1]

        self.negative_list = ['fear', 'sadness', 'anxiety', 'hurt', 'embarrasesd', 'boredom']
        self.negative_weight = [3, 3, 4, 4, 4, 2, 1]
        self.dict_list = {}
        for index in self.index_list:
            for i in index:
                self.dict_list[i] = 0

    def make_dataframe(self, number):
        now_date = datetime.now()
        now_date = now_date.date() + relativedelta(days=+1)
        start_date = now_date + relativedelta(days=-2)  # 6일 전부터
        print(now_date, start_date)

        e_score = 0     # 감정
        l_score = 0     # 언어
        total_cnt_list = [0 for _ in range(8)]  # 각 카테고리별 카운트 리스트

        week_sentences = InputSentence.objects.filter(user_num=number, date__range=[start_date, now_date]).values()
        week_emotions = EmotionResult.objects.filter(user_id=number, date__range=[start_date, now_date]).values()

        # 감정 점수 계산
        if week_emotions:
            emotions_df = pd.DataFrame(week_emotions)
            emotions_df = emotions_df.drop(['id', 'user_id', 'date'], axis=1)
            emotions = emotions_df.idxmax(axis=1)
            emotions_list = list(emotions)
            print(emotions_list)

            for emotion, weight in zip(self.negative_list, self.negative_weight):
                e_score += emotions_list.count(emotion) * weight
                print(emotion, "점수", emotions_list.count(emotion) * weight)

        # 언어 점수 계산
        if week_sentences:
            for sentence in week_sentences:
                score, cnt_list = self.calculate_score(sentence['sentence'])
                l_score += score
                for i in range(8):
                    total_cnt_list[i] += cnt_list[i]

            total_count = sum(total_cnt_list)

            for i in range(len(total_cnt_list)):
                total_cnt_list[i] = round(total_cnt_list[i] / total_count * 100, 2)

        total_score = l_score + e_score
        print("감정점수:", e_score, "언어점수:", l_score, "위험도점수:", total_score)

        return total_score, total_cnt_list, self.dict_list

    def calculate_score(self, sentence):
        score = 0
        cnt_list = []

        for index, weight in zip(self.index_list, self.index_weight):   # 각 카테고리
            cnt = 0
            for i in index:     # 각 카테고리에 해당하는 단어
                if i in sentence:
                    print(i, "포함", weight)
                    score = weight + score
                    cnt += 1
                    self.dict_list[i] += 1
            cnt_list.append(cnt)

        return score, cnt_list

    def total_score(self, user_id):
        user = User.objects.filter(user_id=user_id).first()
        total_score, total_cnt_list, dict_list = self.make_dataframe(user_id)

        client = mqtt.Client()
        client.connect("18.144.44.57")

        if total_score >= 200:
            user.status = '위험'
            user.save()
            client.publish("iot/bigdata", "환자가 위험합니다", qos=1)
            print(user.user_id, "번 유저의 상태가 위험합니다.")
        elif total_score < 200:
            user.status = '평온'
            user.save()
            print(user.user_id, "번 유저의 상태가 평온해졌습니다.")


def make_dict(number, sdate=None, edate=None):
    now_date = datetime.now()
    now_date = now_date.date()
    start_date = now_date + relativedelta(days=-6)  # 6일 전부터

    # sdate 존재x -> 일주일 전부터 오늘날짜까지
    if sdate:
        results = EmotionResult.objects.filter(user_id=number, date__range=[sdate, edate + relativedelta(days=1)]).values()
    else:
        results = EmotionResult.objects.filter(user_id=number, date__range=[start_date, now_date]).values()

    results_df = pd.DataFrame(results)
    results_df = results_df.drop(['id'], axis=1)
    results_df = results_df.drop(['user_id'], axis=1)

    print(results_df)
    results_df['date'] = pd.to_datetime(results_df['date']).dt.date
    group = results_df.groupby(['date']).mean().reset_index()
    results_dict = group.to_dict('records')

    color_list = ["rgba(179,181,198, 1)", "rgba(253, 171, 88, 1)", "rgba(255,99,132, 1)",
                  "rgba(207, 149, 254, 1)", "rgba(168, 254, 149, 1)",
                  "rgba(149,243,254, 1)", "rgba(238, 165, 226, 1)"]
    back_color_list = ["rgba(179,181,198, 0.2)", "rgba(253, 171, 88, 0.2)", "rgba(255,99,132, 0.2)",
                       "rgba(207, 149, 254, 0.2)", "rgba(168, 254, 149, 0.2)",
                       "rgba(149,243,254, 0.2)", "rgba(238, 165, 226, 0.2)"]

    for i in range(len(results_dict)):
        results_dict[i]['color'] = color_list[i]
        results_dict[i]['back'] = back_color_list[i]

    return results_dict


def predict():
    kobert = KoBERT()
    user_num = 1
    if InputSentence.objects.filter(done=1):
        input_sentences = InputSentence.objects.filter(user_num=user_num, done=1)

        for input_sentence in input_sentences:
            sentence = input_sentence.sentence
            date = input_sentence.date
            result_figure = kobert.predict(sentence)
            kobert.object_figure(result_figure, date)
            input_sentence.done = 0
            input_sentence.save()
            print(input_sentence.sentence, "분류 완료")
            time.sleep(3)
        print("모든 분류가 완료되었습니다.")
    else:
        print("이미 모든 분류가 완료되었습니다.")


# mqtt
def pub(request):
    print("생성")
    publish(request)


def publish(request):
    print("post대기")
    if request.method == "POST":
        print("pub요청")
        message = request.POST['message']
        history = ChatHistory.objects.create(chats=message,
                                             date=datetime.now())
        client = mqtt.Client()
        client.connect("18.144.44.57", 1883)
        client.publish("iot/django", message, qos=1)
        print("pub완료")

        return redirect('/content/messages')
