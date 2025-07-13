# notifications/urls.py

from django.urls import path
from .views import UserNotificationsView, UnreadNotificationCountView, MarkNotificationAsReadView

urlpatterns = [
    path('', UserNotificationsView.as_view(), name='user_notifications'),
    path('unread-count/', UnreadNotificationCountView.as_view(), name='unread_notifications'),
    path('mark-as-read/<int:pk>/', MarkNotificationAsReadView.as_view(), name='mark_notification_as_read'),

]
