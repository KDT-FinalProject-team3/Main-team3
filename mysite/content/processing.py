from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from content.models import EmotionResult, User


def make_dict(number):
    results = EmotionResult.objects.filter(user_id=number).values()
    results_df = pd.DataFrame(results)
    results_df = results_df.drop(['id'], axis=1)
    results_df = results_df.drop(['user_id'], axis=1)

    now_date = datetime.now()
    now_date = now_date.date()
    start_date = now_date + relativedelta(days=-6)  # 6일 전부터

    results_df['date'] = pd.to_datetime(results_df['date']).dt.date
    group = results_df.groupby(['date']).mean().reset_index()
    results_dict = group.to_dict('records')

    return results_dict