from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.mail import send_mail
from django.contrib.auth.models import User


# Create your models here.
class Quote(models.Model):
    QID = models.AutoField(primary_key=True, verbose_name= 'quote ID')
    OID = models.ForeignKey('OrderDetail', on_delete=models.CASCADE, related_name='+', verbose_name= 'order ID')
    QLink = models.CharField(max_length=1000, verbose_name= 'website Link')
    QPrice = models.DecimalField(max_digits=15, decimal_places=2, verbose_name= 'item Price')
    Supplier = models.CharField(max_length=30)
    def __str__(self):
        return 'QID: {} {}'.format(self.QID, self.Supplier)

class Contract(models.Model):
    CID = models.AutoField(primary_key=True, verbose_name= 'contract ID')
    CName = models.CharField(max_length=30, verbose_name= 'contract Name')
    CBudget = models.DecimalField(max_digits=20, decimal_places=2, verbose_name= 'budget') 
    CStart = models.DateField(verbose_name= 'contract Start Date')
    CEnd = models.DateField(null=True, verbose_name= 'contract End Date')
    def __str__(self):
        return '{}'.format(self.CName)


class OrderDetail(models.Model):
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
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name= 'order Total')
    orderDate = models.DateField(default=timezone.now, verbose_name= 'date of Request')
    dateApproved = models.DateField(null=True, blank=True, verbose_name= 'date Approved')
    dateReceived = models.DateField(null=True, blank=True, verbose_name= 'date Received')
    isPending = models.BooleanField(default=True, verbose_name= 'Pending')
    isDenied = models.BooleanField(default=False, verbose_name= 'Denied')
    isApproved = models.BooleanField(default=False, verbose_name= 'Approved')

    __original_denied_value = False #original link https://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed
    __original_approved_value = False
    def __init__(self, *args, **kwargs):
        super(OrderDetail, self).__init__(*args, **kwargs)
        #self.__original_denied_value = self.isDenied
       # self.__original_approved_value = self.isApproved
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        req_user = User.objects.get(username=self.EID)  
        if self.isDenied != self.__original_denied_value:
            send_mail(
                'PURCHASE ORDER CONFIRMATION',
                'Hi {},\n\nYou\'re recent purchase request for {} has been denied.\n\nPurchase Management System'.format(req_user.first_name, self.productName),
                'yee.camero23@gmail.com', #Make info@system.com email
                [req_user.email],
                fail_silently=False,
            )
        if self.isApproved != self.__original_approved_value:
            send_mail(
                'PURCHASE ORDER CONFIRMATION',
                'Hi {},\n\nYou\'re recent purchase request for {} has been Approved.\n\nPurchase Management System'.format(req_user.first_name, self.productName),
                'yee.camero23@gmail.com', #Make info@system.com email
                [req_user.email],
                fail_silently=False,
            )
        super(OrderDetail, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_denied_value = self.isDenied
        self.__original_approved_value = self.isApproved

    def __str__(self):
        return '#{}'.format(self.OID)
