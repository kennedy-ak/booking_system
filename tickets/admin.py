from django.contrib import admin
from .models import Ticket, Transaction

class TicketAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'ticket_type', 'unique_code')
    search_fields = ('unique_code',)

admin.site.register(Ticket, TicketAdmin)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'ticket', 'amount', 'settled')
    list_filter = ('settled',)
    search_fields = ('transaction_id', 'ticket__unique_code')

admin.site.register(Transaction, TransactionAdmin)
