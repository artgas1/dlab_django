from django.urls import path
from . import views

urlpatterns = [
    # path('add_order/', views.add_order, name='add_order'),
    path('login/', views.login, name='login'),
    path('register', views.register, name='register')
]
