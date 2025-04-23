from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.uploadView.as_view(), name='upload'),

]