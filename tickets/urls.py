from django.urls import path
from tickets import views

urlpatterns = [
    path('book/', views.book_ticket, name='book_ticket'),
    path('callback/', views.payment_callback, name='payment_callback'),
]
