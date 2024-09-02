from django.urls import path
from tickets import views

urlpatterns = [
    path('', views.book_ticket, name='book_ticket'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('search/', views.search_ticket, name='search_ticket'),
  
]
