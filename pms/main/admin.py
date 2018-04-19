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
from django.forms import ValidationError

class ContractAdmin(admin.ModelAdmin):
    class Media:
        js = ("/static/js/script.js",)
        # css = {
        #     'all': ("/static/styles/css/styles.css",)
        # }

    list_display = ['CName', 'CBudget', 'remainingBudget', 'CStart', 'CEnd']
    exclude = ['remainingBudget',] #list of fields to exclude from the Django add function
    def get_readonly_fields(self, request, obj=None):
        if obj: #This is the case when obj is already created i.e. it's an edit
            return ['CBudget', 'remainingBudget']
        else:
            return []


class OrderAdmin(admin.ModelAdmin):
    class Media:
        js = ("/static/js/script.js",)
        # css = {
        #     'all': ("/static/styles/css/styles.css",)
        # }
    readonly_fields = ('OID', 'EID', 'orderDate')
    list_display = ['OID', 'EID', 'CID', 'productName', 'total', 'orderDate', 'QID', 'isPending', 'isApproved', 'isDenied']

    def has_add_permission(self, request):
        return False

class QuoteAdmin(admin.ModelAdmin):
    list_display = ['QID', 'Supplier', 'QPrice', 'OID']
    readonly_fields = ['OID']
    def has_add_permission(self, request):
        return False

admin.site.register(Order, OrderAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Quote, QuoteAdmin)

admin.site.site_header = 'Allied Mountain Administration'