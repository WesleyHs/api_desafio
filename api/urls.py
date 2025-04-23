from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.uploadView.as_view(), name='upload'),
    path('all/', views.allView.as_view(), name='all'),
]