from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.mail import send_mail
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class Quote(models.Model):
    QID = models.AutoField(primary_key=True, verbose_name= 'quote ID')
    OID = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='+', verbose_name= 'order ID')
    QLink = models.CharField(max_length=1000, verbose_name= 'website Link')
    QPrice = models.DecimalField(max_digits=15, decimal_places=2, null=True, verbose_name= 'item Price')
    Supplier = models.CharField(max_length=30)
    def __str__(self):
        return 'QID: {} {}'.format(self.QID, self.Supplier)

class Contract(models.Model):
    CID = models.AutoField(primary_key=True, verbose_name= 'contract ID')
    CName = models.CharField(max_length=30, verbose_name= 'contract Name')
    CBudget = models.DecimalField(max_digits=10, decimal_places=2, verbose_name= 'budget')
    remainingBudget = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='remaining Budget') 
    CStart = models.DateField(verbose_name= 'contract Start Date')
    CEnd = models.DateField(null=True, verbose_name= 'contract End Date')
    def save(self, *args, **kwargs):
        if self.remainingBudget is None:
            self.remainingBudget = self.CBudget
        super(Contract, self).save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.CName)


class Order(models.Model):
    OID = models.AutoField(primary_key=True, verbose_name = 'order #')
    EID = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, verbose_name = 'employee ID')
    CID = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='Contract') #null allows blank entry to be stored as null, blank allows the form to be saved without QID
    QID = models.ForeignKey(Quote, on_delete=models.CASCADE, null=True, blank=True, verbose_name= 'quote')
    productName = models.CharField(max_length=25, verbose_name= 'item')
    productDescription = models.CharField(max_length=200, verbose_name= 'description')
    addressLine1 = models.CharField(max_length=40, verbose_name='address Line 1')
    addressLine2 = models.CharField(max_length=40, null=True, blank=True, verbose_name='address Line 2')
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=25)
    zipCode = models.CharField(max_length=5, verbose_name= 'zip Code')
    phoneNumber = models.CharField(max_length=15, blank=True, verbose_name='Phone Number') #Outputs error if you use regexvalidation, not sure what to do to validate this field
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name= 'order Total')
    orderDate = models.DateField(default=datetime.now, verbose_name= 'date of Request')
    dateApproved = models.DateField(null=True, blank=True, verbose_name= 'date Approved')
    dateReceived = models.DateField(null=True, blank=True, verbose_name= 'date Received')
    isPending = models.BooleanField(default=True, verbose_name= 'Pending')
    isDenied = models.BooleanField(default=False, verbose_name= 'Denied')
    isApproved = models.BooleanField(default=False, verbose_name= 'Approved')

    __original_denied_value = False
    __original_approved_value = False
    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
    def delete(self):
        contract_type = Contract.objects.get(CName=self.CID)
        if self.dateApproved != None:
            contract_type.remainingBudget = contract_type.remainingBudget + self.total
            contract_type.save()
        super(Order, self).delete()

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        req_user = User.objects.get(username=self.EID) #gets the users information that requested the order 
        contract_type = Contract.objects.get(CName=self.CID) #gets the contract that the order belongs to
        if self.isDenied != self.__original_denied_value:
            if self.dateApproved != None: #checks if model has an approved date, if it does, then it adds total back to contract remainingBudget
                contract_type.remainingBudget = contract_type.remainingBudget + self.total #readds the total that was previously taken away from contract remainingBudget
                contract_type.save() #saves the contract model and readds the total the was previously taken away
                self.dateApproved = None #resets the dateApproved field to empty
            send_mail(
                'PURCHASE ORDER #{} CONFIRMATION'.format(self.OID),
                'Hi {},\n\nYour recent purchase order #{} request for item: "{}" has been denied.\n\n\nAM Purchase Management System'.format(req_user.first_name, self.OID, self.productName),
                'yee.camero23@gmail.com', #Make info@system.com email
                [req_user.email], #gets the email from the user that requested the item
                fail_silently=False,
            )
        if self.isApproved != self.__original_approved_value:
            contract_type.remainingBudget = contract_type.remainingBudget - self.total #subtracts the total from the remainingBudget
            contract_type.save() #saves the contract model to show the new remainingBudget
            self.dateApproved = datetime.now() #sets the approved date to now
            send_mail(
                'PURCHASE ORDER #{} CONFIRMATION'.format(self.OID),
                'Hi {},\n\nYour recent purchase order #{} request for item: "{}" has been approved.\n\n\nAM Purchase Management System'.format(req_user.first_name, self.OID, self.productName),
                'yee.camero23@gmail.com', #Make info@system.com email
                [req_user.email],
                fail_silently=False,
            )
        super(Order, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_denied_value = self.isDenied
        self.__original_approved_value = self.isApproved

    def __str__(self):
        return '#{}'.format(self.OID)
