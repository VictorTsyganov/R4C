from django.urls import path

from . import views

app_name = 'robots'

urlpatterns = [
    path('create_robot', views.create_robot),
    path('download_report', views.download_report),
]
