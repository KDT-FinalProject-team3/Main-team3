from django.shortcuts import redirect, render
import paho.mqtt.client as mqtt

from .kobert import KoBERT
from .models import InputSentence

import time
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
from content.models import EmotionResult, User


def make_dict(number, start=None, end=None):
    now_date = datetime.now()
    now_date = now_date.date() + relativedelta(days=+1)
    start_date = now_date + relativedelta(days=-7)  # 6일 전부터

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
    return render(request, 'content/notifications.html')


def publish(request):
    print("post대기")
    if request.method == "POST":
        print("pub요청")
        message = request.POST['message']
        client = mqtt.Client()
        client.connect("18.144.44.57", 1883)
        client.publish("iot/django", message, qos=1)
        print("pub완료")
        return redirect('/content/pub')
