from django.urls import path
from mailing.views import (mailing, mailing_logs, clients, MailingCreateView, mailing_info, MailingUpdateView,
                           MailingDeleteView, ClientCreateView, client_info, ClientUpdateView, ClientDeleteView, toggle_activity,
                           users, ban, blog)


app_name = 'mailing'

urlpatterns = [
    path('', mailing, name='mailings'),
    path('logs/', mailing_logs, name='mailing_logs'),
    path('clients/', clients, name='clients'),
    path('create/', MailingCreateView.as_view(), name='create_mailing'),
    path('mailing/<int:mailing_id>/', mailing_info, name='mailing_info'),
    path('mailing/edit/<int:pk>', MailingUpdateView.as_view(), name='update_mailing'),
    path('mailing/delete/<int:pk>', MailingDeleteView.as_view(), name='delete_mailing'),
    path('clients/create/', ClientCreateView.as_view(), name='create_client'),
    path('clients/<int:client_id>/', client_info, name='client_info'),
    path('clients/edit/<int:pk>', ClientUpdateView.as_view(), name='update_client'),
    path('clients/delete/<int:pk>', ClientDeleteView.as_view(), name='delete_client'),
    path('activity/<int:pk>', toggle_activity, name='toggle_activity'),
    path('users', users, name='users'),
    path('users/ban/<int:pk>', ban, name='ban'),
    path('blog/<int:pk>', blog, name='blog')
]
