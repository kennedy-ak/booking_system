from django.db import models

class Ticket(models.Model):
    TICKET_CHOICES = (
        ('regular', 'single - 69 Cedis'),
        ('double', 'Double - 120 Cedis'),
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    ticket_type = models.CharField(max_length=7, choices=TICKET_CHOICES)
    unique_code = models.CharField(max_length=10, blank=True, unique=True)

    def __str__(self):
        return f"{self.unique_code} - {self.ticket_type}"


        
class Transaction(models.Model):
    transaction_id = models.CharField(max_length= 20 , primary_key= True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    settled = models.BooleanField(default= False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_settled = models.DateTimeField(null = True)

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)