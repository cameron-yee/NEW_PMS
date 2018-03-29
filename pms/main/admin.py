# from django.contrib import admin
# from .models import Order, Contract, Quote

# class TaskAdmin(admin.ModelAdmin):
#     list_display = ['CName', 'CBudget', 'CStart', 'CEnd']


# def formfield_for_dbfield(self, db_field, request, **kwargs):
#     field = super(MyModelAdmin, self).formfield_for_dbfield(db_field, request, **kwargs)
#     if db_field.name == 'groups':
#         field.queryset = field.queryset.filter(user=request.user)
#     return field


# admin.site.register(Order)
# admin.site.register(Contract, TaskAdmin)
# admin.site.register(Quote)

from django.contrib import admin
from .models import Order, Contract, Quote

class ContractAdmin(admin.ModelAdmin):
    list_display = ['CName', 'CBudget', 'CStart', 'CEnd']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['OID', 'EID', 'CID', 'productName', 'total', 'orderDate', 'QID', 'isPending', 'isApproved', 'isDenied']

class QuoteAdmin(admin.ModelAdmin):
    list_display = ['OID', 'QPrice', 'Supplier']

admin.site.register(Order, OrderAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Quote, QuoteAdmin)