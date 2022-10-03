from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.welcome.__init__, name="welcome-screen"),
    path('device/', include("device.urls")),
    path('user/', include("user.urls")),
]