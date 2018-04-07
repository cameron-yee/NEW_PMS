from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, EmailMessage
from django import forms
from django.contrib.auth.decorators import login_required
from .forms import * 
from django.contrib.auth.models import User
from .models import Contract, Quote, Order
from django.db.models import Sum, Count
from datetime import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO

last_OID = None

#view to generate home page
@login_required
def home(request):
    return render(request, 'main/home.html')

#an example view for a contact page
@login_required
def email(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ContactForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            send_mail(
                'SUBJECT',
                'Hi joe, here is a message.',
                'yee.camero23@gmail.com',
                ['yee.camero23@gmail.com'],
                fail_silently=False,
            )

            # redirect to a new URL:
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ContactForm()

    return render(request, 'main/email.html', {'form': form})

#view to generate order page and run order request logic
@login_required
def order(request):
    if request.method == "POST":
        purchase_form = PurchaseOrderForm(request.POST)
        quote_form = QuoteForm(request.POST)
        quote_form_2 = QuoteForm(request.POST)
        quote_form_3 = QuoteForm(request.POST)
        price = 0
        quantity = 0.0
        saved_quote = 0

        if quote_form.is_valid():
            finished_quote_form = quote_form.save(commit=False)
            price = quote_form.cleaned_data['QPrice']

            if purchase_form.is_valid():
                finished_purchase_form = purchase_form.save(commit=False)

                quantity = purchase_form.cleaned_data['quantity']

                def calcTotal(price, quantity):
                    total = price * quantity
                    return total

                finished_purchase_form.total = calcTotal(price, quantity)
                finished_purchase_form.EID = request.user

                finished_purchase_form.save()
                last_OID = finished_purchase_form.OID

            finished_quote_form.OID = finished_purchase_form
            finished_quote_form.save()

            user_email = request.user.email

            if finished_purchase_form.total < 50:
                current_purchase_form = finished_purchase_form 
                current_quote = finished_quote_form

                def setChosenQuote(current_purchase_form, current_quote):
                    quote = current_quote
                    current_purchase_form.QID = quote
                    current_purchase_form.dateApproved = datetime.now()
                    current_purchase_form.isPending = False
                    current_purchase_form.isApproved = True
                    current_purchase_form.save()

                setChosenQuote(current_purchase_form, current_quote)
            elif finished_purchase_form.total >= 500:
                    request.session['selected_order'] = finished_purchase_form.OID
                    return HttpResponseRedirect('/main/quotes')
            else:
                send_mail(
                    'PURCHASE ORDER #{} CONFIRMATION'.format(self.OID),
                    'Hi {},\n\nYour purchase order #{} request for item: "{}" has been received. Management will get back to you after reviewing the quote.\n\n\nPurchase Management System'.format(request.user.first_name, self.OID, self.productName),
                    'yee.camero23@gmail.com', #Make info@system.com email
                    [user_email],
                    fail_silently=False,
                )

            return HttpResponseRedirect('/')
            
    else:
        purchase_form = PurchaseOrderForm()
        quote_form = QuoteForm()
    return render(request, 'main/order.html', {'purchase_form': purchase_form, 'quote_form': quote_form})

@login_required
def quote(request):
    selected_order = Order.objects.get(OID=request.session['selected_order'])
    #MIGHT NEED TO CLOSE SESSIONS

    if request.method == "POST":
        quote_form2 = QuoteForm(request.POST)
        quote_form3 = QuoteForm(request.POST)
        user_email = request.user.email
        if quote_form2.is_valid():
            finished_quote_form2 = quote_form2.save(commit=False)
            finished_quote_form2.OID = selected_order
            saved_quote2 = finished_quote_form2.save()
        
        if quote_form3.is_valid():
            finished_quote_form3 = quote_form3.save(commit=False)
            finished_quote_form3.OID = selected_order
            saved_quote3 = finished_quote_form3.save()

            send_mail(
                'PURCHASE ORDER CONFIRMATION',
                'Hi {}, you\'re purchase order form has been received. Since the order is over $500, it may take longer to review. Management will get back to you after reviewing the provided quotes.\n\nPurchase Management System'.format(request.user.first_name),
                'yee.camero23@gmail.com', #Make info@system.com email
                [user_email],
                fail_silently=False,
            )
        return HttpResponseRedirect('/')
            
    else:
        quote_form2 = QuoteForm()
        quote_form3 = QuoteForm()        
    return render(request, 'main/quotes.html', {'quote_form2': quote_form2, 'quote_form3': quote_form3})
    

@login_required
def contract(request):
    contracts = Contract.objects.all()
    return render(request, 'main/contract.html', {'contracts': contracts})


@login_required
def employee_spending(request):
    records = {}
    employee_spending = Order.objects.values('EID', 'CID').annotate(Sum('total'))
    count = 0
    for queryset in employee_spending:
        # for key, value in queryset.items():
        EID = queryset['EID']
        user_info = User.objects.values('first_name', 'last_name').filter(id=EID)
        CID = queryset['CID']
        contract_name = Contract.objects.values('CName').filter(CID=CID)
        records[str(count)] = EID, CID, user_info[0]['first_name'], user_info[0]['last_name'], contract_name[0]['CName'], queryset['total__sum']
        count += 1
    return render(request, 'main/employee-spending.html', {'records': records})


@login_required
def myorders(request):
    user_id = request.user.id
    myorders = Order.objects.filter(EID=user_id)
    myquotes = Quote.objects.all()
    return render(request, 'main/myorders.html', {'myorders': myorders, 'myquotes': myquotes})

# @login_required
# def allorders(request):
#     allorders = Order.objects.all()
#     #allorders = Order.objects.all().order_by('isDenied')
#     #allorders = Order.objects.all().order_by('isPending')
#     #allorders = Order.objects.all().order_by('isApproved')
#     #order_ids = [Order.OID for item in myorders]
#     #myquotes = Quote.objects.filter(OID=[Order.OID for item in myorders])
#     #might need to add EID to each quote unless Cameron can get the query working

#     return render(request, 'main/allorders.html', {'allorders': allorders})


@login_required
def reports(request):
    if request.method == 'POST': 
        dates = DateForm(request.POST)
        return HttpResponseRedirect('/')
    else:
        dates = DateForm()
        return render(request, 'main/reports.html', {'dates': dates})

@login_required
def generateorderreport(request):
    if request.method == 'POST': 
        dates_form = DateForm(request.POST)
        start_Date = request.POST.get('startDate')
        end_Date = request.POST.get('endDate')

        contracts = Contract.objects.all()
        orders = Order.objects.filter(isApproved=True)
        user = str(request.user.first_name + ' ' + request.user.last_name)

        filename = 'OrdersReport--{}'.format(datetime.today().strftime('%m-%d-%Y'))
        # Make your response and prep to attach
        response = HttpResponse(content_type='application/pdf')
        # Specifies file should be downloaded as web attachment
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % (filename)
        tmp = BytesIO()

        def PDFGen(contracts, orders):
            def writePDF(contracts, orders, c):
                x = 100
                y = 685
                z = 670
                c.setFont("Helvetica", 28)
                c.drawString(150, 780, 'Monthly Spending Report')
                c.setFont("Helvetica", 16)
                c.drawString(175, 755, 'For dates ' + start_Date + ' - ' + end_Date)

                date = str(datetime.today().strftime('%m-%d-%Y'))
                c.drawString(485, 820, date)
                c.drawString(100, 700, user)

                for contract in contracts:
                    c.setFont("Helvetica", 16)
                    c.drawString(x, y, 'Contract: ' + contract.CName)
                    c.setFont("Helvetica", 12)
                    for order in orders.filter(CID=contract.CID, dateApproved__range=(start_Date, end_Date)):
                        c.drawString(x + 10, z, str(order.dateApproved) + ' ' + order.productName + ' ' + str(order.quantity) + ' ' + str(order.total/order.quantity) + ' ' + str(order.total))
                        z -= 15
                    y = z - 10
                    z = y - 15

                # c.drawString(100,100, "Hello World")

            # c = canvas.Canvas('/Users/cameronyee/Desktop/test.pdf')
            c = canvas.Canvas(tmp)
            writePDF(contracts, orders, c)
            c.showPage()
            c.save()

            pdf = tmp.getvalue()
            tmp.close()

            # user_first_name = request.user.first_name
            # user_email = request.user.email
            # message = EmailMessage(
            #     'PMS Order Report', #subject
            #     'Hello {}'.format(user_first_name), #message body
            #     'yee.camero23@gmail.com', #sender
            #     [user_email,], #list of recipients
            # )
            # # message.attach('Order Report', '/Users/cameronyee/Desktop/test.pdf', 'application/pdf')
            # # message.attach_file('/Users/cameronyee/Desktop/test.pdf')
            # message.send()
            return pdf

        pdf = PDFGen(contracts, orders)
        # request.session['pdf'] = pdf NOT WORKING, JSON error

        response.write(pdf)
        return response #HttpResponseRedirect('/main/report') #, response #HttpResponseRedirect('/')
    else:
        form = DateForm()
        response #HttpResponseRedirect('/')


# def report(request):
#     pdf = request.session['pdf']
#     pdf.decode('utf-8')
#     return render(request, 'main/report.html', {'pdf': pdf})
