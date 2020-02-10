from django.urls import path
from reminder import views

urlpatterns = [
    path(r'register/', views.Register.as_view())
]
