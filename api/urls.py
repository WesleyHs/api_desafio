from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.uploadView.as_view(), name='upload'),
    path('all/', views.allView.as_view(), name='all'),
    path('order/<int:order_id>/', views.orderView.as_view(), name='order'),
    path('date/', views.dateView.as_view(), name='date'),
]