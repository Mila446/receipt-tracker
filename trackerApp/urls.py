from django.urls import path
from . import views


urlpatterns = [
    path('',views.index, name='index'),
    path('callback/', views.callback, name='callback'),
    path('emails', views.emails, name='emails'),
    path('summary',views.summ,name='summ')
]