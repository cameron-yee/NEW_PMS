from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.mail import send_mail
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
#DB design for Quote object
class Quote(models.Model):
    #Fields for db table: main_quote
    QID = models.AutoField(primary_key=True, verbose_name= 'quote ID')
        #related_name attribute is crucial for DB design, it's necessary because of multiple relations between quote and order tables (approved Quote)
    OID = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='quoteorder', verbose_name= 'order ID')
    QLink = models.CharField(max_length=1000, verbose_name= 'website Link')
    QPrice = models.DecimalField(max_digits=15, decimal_places=2, null=True, verbose_name= 'item Price')
    Supplier = models.CharField(max_length=30)
    def __str__(self):
        return '{}'.format(self.QID) #sets the object name as the QID number and supplier in the format for example: "QID: 2 Target"

#DB design for Contract object
class Contract(models.Model):
    #Fields for db table: main_contract
    CID = models.AutoField(primary_key=True, verbose_name= 'contract ID')
    CName = models.CharField(max_length=30, verbose_name= 'contract Name')
    CBudget = models.DecimalField(max_digits=10, decimal_places=2, verbose_name= 'budget')
    remainingBudget = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='remaining Budget') 
    CStart = models.DateField(verbose_name= 'contract Start Date')
    CEnd = models.DateField(null=True, verbose_name= 'contract End Date')

    def __init__(self, *args, **kwargs):
        super(Contract, self).__init__(*args, **kwargs)
        self.original_budget = self.CBudget
        self.original_remainingBudget = self.remainingBudget

    def save(self, *args, **kwargs):
        if self.remainingBudget is None:
            self.remainingBudget = self.CBudget
        elif self.CBudget != self.original_budget:
            total = self.original_budget - self.original_remainingBudget
            self.remainingBudget = self.CBudget - total
        super(Contract, self).save(*args, **kwargs)
    def __str__(self):
        return '{}'.format(self.CName) #sets the object name as the name of the Contract

#DB design for an Order object
class Order(models.Model):
    #Fields for db table: main_order
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
    comments = models.CharField(max_length=2500, blank=True)

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self.original_total = self.total
        self.original_approved = self.isApproved

    #Adjusts remaining budget if approved order is deleted
    def delete(self):
        contract_type = Contract.objects.get(CName=self.CID)
        if self.dateApproved != None: #if order is currently approved and is linked to a contract, before it is deleted, the amount of this order is taken out of this contract
            contract_type.remainingBudget = contract_type.remainingBudget + self.original_total #adds order amount back to the corresponding contracts remaining budget
            contract_type.save() #saves the contract model
        super(Order, self).delete()

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        req_user = User.objects.get(username=self.EID) #gets the users information that requested the order 
        contract_type = Contract.objects.get(CName=self.CID) #gets the contract that the order belongs to
        if self.QID != None:
            quote_price = Quote.objects.get(QID=str(self.QID)) #
            self.total = quote_price.QPrice * self.quantity
        if (self.isDenied == True) and (self.isApproved == False) and (self.isPending == False):
            if self.original_approved == True: #checks if model has an approved date, if it does, then it adds total back to contract remainingBudget
                contract_type.remainingBudget = contract_type.remainingBudget + self.original_total #readds the total that was previously taken away from contract remainingBudget
                contract_type.save() #saves the contract model and readds the total the was previously taken away
                self.dateApproved = None #resets the dateApproved field to empty
            send_mail(
                'PURCHASE ORDER #{} CONFIRMATION'.format(self.OID),
                'Hi {},\n\nYour recent purchase order #{} request for item: "{}" has been denied.\n\n\nAM Purchase Management System'.format(req_user.first_name, self.OID, self.productName),
                'yee.camero23@gmail.com', #Make info@system.com email
                [req_user.email], #gets the email from the user that requested the item
                fail_silently=False,
            )
        elif (self.isApproved == True) and (self.isDenied == False) and (self.isPending == False):
            if self.original_approved == True:
                if self.original_total != self.total:
                    contract_type.remainingBudget = contract_type.remainingBudget + self.original_total
                    contract_type.remainingBudget = contract_type.remainingBudget - self.total #subtracts the total from the remainingBudget
                    contract_type.save() #saves the contract model to show the new remainingBudget
            else:
                contract_type.remainingBudget = contract_type.remainingBudget - self.total #subtracts the total from the remainingBudget
                contract_type.save() #saves the contract model to show the new remainingBudget
            if self.dateApproved == None:
                self.dateApproved = datetime.now() #sets the approved date to now
            send_mail(
                'PURCHASE ORDER #{} CONFIRMATION'.format(self.OID),
                'Hi {},\n\nYour recent purchase order #{} request for item: "{}" has been approved.\n\n\nAM Purchase Management System'.format(req_user.first_name, self.OID, self.productName),
                'yee.camero23@gmail.com', #Make info@system.com email
                [req_user.email],
                fail_silently=False,
            )
        else:
            if self.original_approved == True:
                contract_type.remainingBudget = contract_type.remainingBudget + self.original_total #readds the total that was previously taken away from contract remainingBudget
                contract_type.save() #saves the contract model and readds the total the was previously taken away
                self.dateApproved = None #resets the dateApproved field to empty
            self.isApproved = False
            self.isDenied = False
            self.isPending = True
        super(Order, self).save(force_insert, force_update, *args, **kwargs)

    def __str__(self):
        return '#{}'.format(self.OID) #sets the object name as the Order number

#Allows for admin to limit contracts that users can order on
class UserContract(models.Model):
    CID = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='Contract')
    EID = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, verbose_name='employee ID')

    def __str__(self):
        contract_obj = Contract.objects.get(CName=str(self.CID))
        return '{}'.format(contract_obj.CName)