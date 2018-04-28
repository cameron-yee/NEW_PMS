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
from django.forms import ValidationError, ModelForm

#Custom form for Contract view on admin.  This allows data validation for the form.
class ContractAdminForm(ModelForm):
    class Meta:
        model = Contract
        fields = ['CName', 'CBudget', 'remainingBudget', 'CStart', 'CEnd']
        
    def clean(self):
        CName = self.cleaned_data['CName']
        CStart = self.cleaned_data['CStart']
        CEnd = self.cleaned_data['CEnd']
        CBudget = self.cleaned_data['CBudget']
        contracts = Contract.objects.all().values_list('CName')
        print(contracts)
        if CName in contracts:
            raise ValidationError('Name already exists.')
        if CStart > CEnd:
            raise ValidationError('End Date cannot be before start datex.')
        if CBudget <= 0:
            raise ValidationError('Budget cannot be 0 or negative.')
        return self.cleaned_data



class ContractAdmin(admin.ModelAdmin):
    #allows for custom js scripts and css stylesheet for admin view
    class Media:
        js = ("/static/js/script.js",)
        # css = {
        #     'all': ("/static/styles/css/styles.css",)
        # }

    form = ContractAdminForm
    list_display = ['CName', 'CBudget', 'remainingBudget', 'CStart', 'CEnd']
    exclude = ['remainingBudget',] #list of fields to exclude from the Django add function
    def get_readonly_fields(self, request, obj=None):
        if obj: #This is the case when obj is already created i.e. it's an edit
            return ['remainingBudget']
        else:
            return []


class OrderAdmin(admin.ModelAdmin):
    #allows for custom js scripts and css stylesheet for admin view
    class Media:
        js = ("/static/js/script.js",)
        # css = {
        #     'all': ("/static/styles/css/styles.css",)
        # }
    readonly_fields = ('OID', 'EID', 'orderDate')
    list_display = ['OID', 'EID', 'CID', 'productName', 'total', 'orderDate', 'QID', 'isPending', 'isApproved', 'isDenied']

    def has_add_permission(self, request):
        return False

    form_OID = None
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form_OID = obj.OID
        return super(OrderAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "QID":
            kwargs["queryset"] = Quote.objects.filter(OID=self.form_OID)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class QuoteAdmin(admin.ModelAdmin):
    list_display = ['QID', 'Supplier', 'QPrice', 'OID']
    readonly_fields = ['OID']
    def has_add_permission(self, request):
        return False

#Sets the models as viewable 
admin.site.register(Order, OrderAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Quote, QuoteAdmin)

admin.site.site_header = 'Allied Mountain Administration'