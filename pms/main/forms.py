from django import forms
from django.forms import ModelForm
from . import models
from .models import Order, Contract
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)

class MyModelChoiceField(forms.ModelChoiceField): #gets the Contract name for the ChoiceFields in the form
    def label_from_instance(self, obj):
        return obj.CName

class PurchaseOrderForm(ModelForm):
    CID = MyModelChoiceField(queryset=Contract.objects.all()) #inserts the names of the contracts in the Contract choice fields
    class Meta: 
        model = models.Order
        fields = ['orderDate', 'CID', 'productName', 'productDescription', 'addressLine1', 'addressLine2', 'city', 'state', 'zipCode','quantity']

    def __init__(self, *args, **kwargs):
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)
        self.fields['CID'].label = 'Contract' #sets the label of the contracts as 'Contract"
        self.fields['quantity'].widget.attrs['min'] = 1 #sets the minimum quanitity to 1
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['orderDate'].widget.attrs['readonly'] = True #sets the orderDate field as readonly

    def __unicode__(self):
        return self.fields['productName'] #returns the product name as the object
            
class QuoteForm(ModelForm):
    class Meta:
        model = models.Quote
        fields = ('Supplier', 'QPrice', 'QLink')

    def __init__(self, *args, **kwargs): 
        super(QuoteForm, self).__init__(*args, **kwargs)
        self.fields['QPrice'].widget.attrs['min'] = 0.01 #sets the minimum allowable price to 0.01

class DateForm(forms.Form):
    startDate = forms.DateField(label='Start Date')
    endDate = forms.DateField(label='End Date')
    