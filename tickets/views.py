
from django.shortcuts import render, redirect, get_object_or_404
from .models import Ticket, Transaction
import random
import string
from django.http import JsonResponse
import requests
import os
from django.db.models import Q
from django.conf import settings
def generate_unique_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

import uuid

def generate_transaction_id():
    return str(uuid.uuid4())  # Generates a unique UUID

#     api_url = "https://smsc.hubtel.com/v1/messages/send"
#     params = {
#         "clientsecret": "efaaiwtl",  # Your Hubtel client secret
#         "clientid": "pzpyfjaj",      # Your Hubtel client ID
#         "from": "DJThomas",            # The sender ID (adjust as needed)
#         "to": phone_number,
#         "content": message
#     }
    
#     response = requests.get(api_url, params=params)
    
#     if response.status_code == 200:
#         response_data = response.json()
#         if response_data.get("status") == 0:
#             # Handle pending status
#             print("SMS is pending delivery. Message ID:", response_data.get("messageId"))
#         else:
#             print("SMS sent successfully. Message ID:", response_data.get("messageId"))
#         return response_data
#     else:
#         raise Exception(f"Failed to send SMS: {response.text}")
def send_sms(phone_number, message):
    api_url = "https://smsc.hubtel.com/v1/messages/send"
    params = {
        "clientsecret": "cxvdnzcw", 
        "clientid": "adgliigb",      
        "from": "DJTommy",          # The sender ID (adjust as needed)
        "to": phone_number,
        "content": message
    }
    
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("status") == 0:
            # SMS is pending delivery, but it's still considered successfully sent
            print("SMS is pending delivery. Message ID:", response_data.get("messageId"))
            return response_data
        elif response_data.get("status") == 1:
            # SMS was sent successfully
            print("SMS sent successfully. Message ID:", response_data.get("messageId"))
            return response_data
        else:
            raise Exception(f"Failed to send SMS: {response.text}")
    else:
        raise Exception(f"Failed to send SMS: {response.text}")

def book_ticket(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone_number')
        email = request.POST.get('email')
        ticket_type = request.POST.get('ticket_type')
        amount = 1 if ticket_type == 'single' else 1
        unique_code = generate_unique_code()

        ticket = Ticket.objects.create(name=name, phone_number=phone, email=email, ticket_type=ticket_type, unique_code=unique_code)
        transaction_id = generate_transaction_id()
        transaction = Transaction(transaction_id=transaction_id, ticket=ticket, amount=amount)
        transaction.save()

        try:
            url = request.build_absolute_uri('/')[:-1] + '/callback/'
            authorization_url = pay(transaction, url)
            return redirect(authorization_url)
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return render(request, 'tickets/book.html')


# def payment_callback(request):
#     ref = request.GET.get('reference')
#     try:
#         transaction = Transaction.objects.get(transaction_id=ref)
#         if verify_payment(ref):
#             transaction.settled = True
#             transaction.save()


#         # Send SMS with the unique code
#             message = f"Dear {transaction.ticket.name}, your ticket purchase for {transaction.ticket.ticket_type} was successful! Your unique code is {transaction.ticket.unique_code}. Show this code at the event. Thank you!"
#             send_sms(transaction.ticket.phone_number, message)
#             # You might want to update the ticket status or send a confirmation message/email
#             return render(request, 'tickets/verify_pay.html')
#         else:
#             return JsonResponse({'error': 'Payment verification failed'})
#     except Transaction.DoesNotExist:
#         return JsonResponse({'error': 'Transaction not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})

# def payment_callback(request):
#     ref = request.GET.get('reference')
#     try:
#         transaction = Transaction.objects.get(transaction_id=ref)
#         if verify_payment(ref):
#             transaction.settled = True
#             transaction.save()

#             # Send SMS with the unique code
#             message = f"Dear {transaction.ticket.name}, your ticket purchase for {transaction.ticket.ticket_type} was successful! Your unique code is {transaction.ticket.unique_code}. Show this code at the event. Thank you!"
#             send_sms(transaction.ticket.phone_number, message)

#             # Redirect to the verification success template after SMS is sent
#             return render(request, 'tickets/verify_pay.html')
#         else:
#             return JsonResponse({'error': 'Payment verification failed'})
#     except Transaction.DoesNotExist:
#         return JsonResponse({'error': 'Transaction not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})
def payment_callback(request):
    ref = request.GET.get('reference')
    try:
        transaction = Transaction.objects.get(transaction_id=ref)
        if verify_payment(ref):
            transaction.settled = True
            transaction.save()

            # Send SMS with the unique code
            message = f"Dear {transaction.ticket.name}, your ticket purchase for {transaction.ticket.ticket_type} was successful! Your unique code is {transaction.ticket.unique_code}. Show this code at the event. Thank you!"
            sms_response = send_sms(transaction.ticket.phone_number, message)

            # Log the SMS response for tracking if needed
            print("SMS Response:", sms_response)

            # Redirect to the verification success template after SMS is sent
            return render(request, 'tickets/verify_pay.html')
        else:
            return JsonResponse({'error': 'Payment verification failed'})
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})

def pay(transaction, callback_url):
    headers = {
        "Authorization": "Bearer sk_live_407fb08d42eeffbc54dfab47d786ecae6b15d396",
        "Content-Type": "application/json"
    }
    data = {
        "email": transaction.ticket.email,
        "amount": int(transaction.amount * 100),
        "currency": "GHS",
        "reference": transaction.transaction_id,
        "callback_url": callback_url
    }
    response = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=data)
    if response.status_code == 200:
        data = response.json()['data']
        return data['authorization_url']
    else:    
        error_message = response.json().get('message', 'No error message received')
    raise Exception(f"Payment initialization failed with Paystack: {error_message}")



def verify_payment(transaction_id):
    headers = {
        "Authorization": 'Bearer sk_live_407fb08d42eeffbc54dfab47d786ecae6b15d396',
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://api.paystack.co/transaction/verify/{transaction_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        return data['status'] == 'success'
    else:
        raise Exception("Failed to verify payment")



def search_ticket(request):
    if request.method == 'POST':
        unique_code = request.POST.get('unique_code')
        try:
            ticket = Ticket.objects.get(unique_code=unique_code)
            return render(request, 'tickets/ticket_details.html', {'ticket': ticket})
        except Ticket.DoesNotExist:
            return render(request, 'tickets/search.html', {'error': 'Ticket not found'})
    
    return render(request, 'tickets/search.html')


# sms
# queue
# admin page
# bulk sms