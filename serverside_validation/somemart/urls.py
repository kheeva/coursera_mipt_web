from django.urls import path
from django.contrib.auth import views as auth_views

from .views import AddItemView, GetItemView, PostReviewView


urlpatterns = [
    path('login/', auth_views.LoginView.as_view()),
    path('api/v1/goods/', AddItemView.as_view()),
    path('api/v1/goods/<int:item_id>/', GetItemView.as_view()),
    path('api/v1/goods/<int:item_id>/reviews/', PostReviewView.as_view()),
]
