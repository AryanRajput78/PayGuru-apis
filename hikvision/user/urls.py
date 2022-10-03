from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

#APIs to access the devices and perform functions.
urlpatterns = [
    path('', views.checkOnline, name='user-info-api'),
    path('getusers/', views.getUsers, name='user-online-check-api'),
    path('getCount/', views.getCount, name='user/cards/face-count-api'),
    path('getCardList/', views.getCardList, name='card-list'),
    path('create/', views.create_user, name='create-user'),
    path('update/<int:pk>', views.update_user, name='update-user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)