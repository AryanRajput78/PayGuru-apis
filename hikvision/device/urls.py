from django.urls import path, include
from . import views

#APIs to access the devices and perform functions.
urlpatterns = [
    path('', views.device_list, name='device-list-api'),
    path('createDevice/', views.device_list_create, name='device-create-api'),
    path('update/<int:pk>/', views.device_update, name='device-update-api'),
]