# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.conf import settings
# from .models import Ticket, Transaction
# import random
# import string
# import requests
# import os

# def generate_unique_code():
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# def book_ticket(request):
#     if request.method == 'POST':
#         name = request.POST['name']
#         phone = request.POST['phone_number']
#         email = request.POST['email']
#         ticket_type = request.POST['ticket_type']
#         amount = 50 if ticket_type == 'regular' else 70
#         unique_code = generate_unique_code()

#         ticket = Ticket.objects.create(name=name, phone_number=phone, email=email, ticket_type=ticket_type, unique_code=unique_code)
#         transaction = Transaction.objects.create(ticket=ticket, amount=amount)
#         try:
#             url = request.build_absolute_uri('/')[:-1] + '/account/pay-verify'  # Adjust according to actual URL
#             authorization_url = pay(transaction, url)
#             transaction.transaction_id = response['reference']  # Save the transaction reference from Paystack
#             transaction.save()
#             return redirect(authorization_url)
#         except Exception as e:
#             return JsonResponse({'error': str(e)})

#     return render(request, 'tickets/book.html')



# def pay(transaction , url):
#     try:

        


        

#         req = requests.post("https://api.paystack.co/transaction/initialize" , 
#         headers = {
#             "Authorization" : f"Bearer {os.getenv('PAY_KEY')}",
#             "Content_type" : "application/json"
#         },
#         data= {
#             "email" : transaction.user.email, 
#             "amount" : int(transaction.amount * 100),
#             "currency" : "GHS", 
#             "reference" : transaction.transaction_id, 
#             "callback_url" : f"{url}/account/pay-verify", 
#             "channels" : ["card" , "bank" , "ussd" , "qr" , "mobile_money" , "bank_transfer" , "eft"], 

#         })

       
#         if(req.status_code != 200):
#             raise Exception("Payment failed")

#         response = req.json()

        
#         req.close()

#         return response['data']['authorization_url']

#     except Exception as e:
#         # if e == ##### : custom handle some request errors or propagate error foward
#         print(e)
#         raise Exception(e)

# def verify_payment(transaction_id):
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json"
#     }
#     response = requests.get(f"https://api.paystack.co/transaction/verify/{transaction_id}", headers=headers)
#     if response.status_code == 200:
#         data = response.json()['data']
#         return data['status'] == 'success'
#     else:
#         raise Exception("Failed to verify payment")

# def pay_verify(request):
#     try:
#         transaction_id = request.GET.get('reference')
#         transaction = Transaction.objects.get(transaction_id=transaction_id)
#         if verify_payment(transaction_id):
#             transaction.settled = True
#             transaction.save()
#             # Consider redirecting to a success page or rendering success directly
#             return render(request, 'tickets/verify_pay.html')
#         else:
#             return JsonResponse({"status": "error", "message": "Payment verification failed"})
#     except Transaction.DoesNotExist:
#         return JsonResponse({"status": "error", "message": "Transaction not found"})
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)})


# # def verify_payment(transaction):
# #     try:
        
# #         req = requests.get(f"https://api.paystack.co/transaction/verify/{transaction.transaction_id}" , 
# #         headers = {
# #             "Authorization" : f"Bearer {os.getenv('PAY_KEY')}",
# #             "Content_type" : "application/json"
# #         })  

# #         if(req.status_code != 200):
# #             raise Exception("Payment verification failed")

# #         response = req.json()

# #         req.close()

# #         return response['data']['status'] == "success"

    

# #     except Exception as e:
# #         print(e)
# #         raise Exception(e)



# # def pay_verify(request):
#     try:

#         transaction_id = request.GET['reference']
        
#         transaction = Transaction.objects.get(transaction_id = transaction_id)

#         success = verify_payment(transaction)



#         if not success:
#             return Response({
#                 "status" : "error" , 
#                 "message" : f"Payment verification failed. If you've been charged, contact support at support@retailsensei.com with this id #{transaction_id}"
#             } , status = 200 , content_type= "application/json")

#         transaction.settled = True
#         transaction.save()

#         return render(request, 'tickets/verify_pay.html')

#     except Transaction.DoesNotExist:
#         return Response({
#             "status" : "error" , 
#             "message" : "Transaction not found"
#         } , status = 200 , content_type= "application/json")

#     except Exception as e:
#         print(e)
#         return Response("An internal error occured", 
#             status = 500 , content_type="application/json")



from django.shortcuts import render, redirect
from .models import Ticket, Transaction
import random
import string
from django.http import JsonResponse
import requests
import os
from django.conf import settings
def generate_unique_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

import uuid

def generate_transaction_id():
    return str(uuid.uuid4())  # Generates a unique UUID


def book_ticket(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone_number')
        email = request.POST.get('email')
        ticket_type = request.POST.get('ticket_type')
        amount = 69 if ticket_type == 'single' else 120
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


def payment_callback(request):
    ref = request.GET.get('reference')
    try:
        transaction = Transaction.objects.get(transaction_id=ref)
        if verify_payment(ref):
            transaction.settled = True
            transaction.save()

            # You might want to update the ticket status or send a confirmation message/email
            return render(request, 'tickets/verify_pay.html')
        else:
            return JsonResponse({'error': 'Payment verification failed'})
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})

def pay(transaction, callback_url):
    headers = {
        "Authorization": "Bearer sk_test_57902e34a214be5d691ec0d198f684b99325b299",
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
        "Authorization": 'Bearer sk_test_57902e34a214be5d691ec0d198f684b99325b299',
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://api.paystack.co/transaction/verify/{transaction_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        return data['status'] == 'success'
    else:
        raise Exception("Failed to verify payment")


# sms
# queue
# admin page
# bulk sms