from django.urls import path

from content.views import Dashboard, UserProfile, Table, Notifications, ImageList, Messages
from . import processing


app_name = 'content'

urlpatterns = [
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('dashboard/<int:number>/', Dashboard.as_view(), name='dashboard'),
    path('user/', UserProfile.as_view(), name='userprofile'),
    path('user/<int:number>/', UserProfile.as_view(), name='userprofile'),
    path('table/', Table.as_view(), name='table'),
    path('table/<int:number>/', Table.as_view(), name='table'),
    # path('notifications/', Notifications.as_view(), name='notifications'),
    path('messages/', Messages.as_view(), name='messages'),
    path('image/', ImageList.as_view(), name='image'),
    path('publish/', processing.publish),
    path('pub/', processing.pub)
]