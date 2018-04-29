from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User
from .models import Contract, Quote, Order
from django.db.models import Sum, Count
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.shortcuts import render
from datetime import datetime
from django.contrib import messages
from django import forms
from io import BytesIO
from .forms import * 
import os

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
    purchase_form = None
    quote_form = None
    if request.method == "POST":
        purchase_form = PurchaseOrderForm(request.POST or None, user=request.user)
        quote_form = QuoteForm(request.POST or None)
        price = 0
        quantity = 0.0
        saved_quote = 0

        if quote_form.is_valid():
            finished_quote_form = quote_form.save(commit=False)
            price = quote_form.cleaned_data['QPrice'] #grabs the price from the first quote and sets it as 'price'
            finished_purchase_form = None
            if purchase_form.is_valid(): #checks to see if the form fields are valid
                finished_purchase_form = purchase_form.save(commit=False) #changes the finished purchase form object name
                contractName = str(purchase_form.cleaned_data['CID']) #gets the contract name from the order
                order_contract = Contract.objects.get(CName=contractName) #gets the contract information that the order belongs to
                contract_budget = order_contract.remainingBudget #sets contract_budget with the remaining budget from the contract related to this order
                quantity = purchase_form.cleaned_data['quantity'] #sets 'quantity' variable as the quantity user requested

                def calcTotal(price, quantity): #function calculates a total price
                    total = price * quantity
                    return total #returns the 'total' variable with a numeric value

                finished_purchase_form.total = calcTotal(price, quantity) #sets the total price into the order
                finished_purchase_form.EID = request.user #sets the user EID into the order

                if contract_budget < finished_purchase_form.total: #checks if order will exeed the remaining balance
                    messages.info(request, 'Your order cannot be submitted because the order total is over the remaining budget for Contract: {}.'.format(contractName))
                    return render(request, 'main/order.html', {'purchase_form': purchase_form, 'quote_form': quote_form}) #redirects to other page and does not save the order or quote entered.
            
                finished_purchase_form.save() #saves the order form
                finished_quote_form.OID = finished_purchase_form #sets the OID in the first quote
                finished_quote_form.save() #saves the first quote that was given
            else:
                messages.info(request, 'You do not have access to contract: {}'.format(purchase_form.cleaned_data['CID']))
                render(request, 'main/order.html', {'purchase_form': purchase_form, 'quote_form': quote_form})

            user_email = request.user.email #grabs the requesting users email

            if finished_purchase_form is not None:
                if finished_purchase_form.total < 50:
                    current_purchase_form = finished_purchase_form #gets the order form instance and sets the variable as current_purchase_form
                    current_quote = finished_quote_form #gets the quote form instance and sets the variable as current_quote

                    def setChosenQuote(current_purchase_form, current_quote): #sets the QID into the Order form
                        quote = current_quote #sets the quote variable as the current_quote instance
                        current_purchase_form.QID = quote #places the QID into the order form
                        current_purchase_form.dateApproved = datetime.now() #sets the date approved as todays date into the order
                        current_purchase_form.isPending = False #sets the isPending value in the order to false
                        current_purchase_form.isApproved = True #sets the isApproved value in the order as approved
                        current_purchase_form.save() #saves the order form
                    setChosenQuote(current_purchase_form, current_quote) #calls the setChosenQuote def
                    messages.info(request, 'Your order was successfully submitted and approved.') #sets the on screen message to the user
                elif finished_purchase_form.total >= 500:
                    request.session['selected_order'] = finished_purchase_form.OID #grabs the OID to transfer it to the quotes class below
                    return HttpResponseRedirect('/main/quotes') #sends the user to the quotes page for the two extra quotes
                else:
                    current_purchase_form = finished_purchase_form #gets the order form instance and sets the variable as current_purchase_form
                    current_quote = finished_quote_form #gets the quote form instance and sets the variable as current_quote
                    current_purchase_form.QID = current_quote #places the QID into the order form
                    current_purchase_form.save() #saves the order form
                    send_mail(
                        'PURCHASE ORDER #{} CONFIRMATION'.format(finished_purchase_form.OID),
                        'Hi {},\n\nYour purchase order #{} request for item: "{}" has been received. Management will get back to you after reviewing the quote.\n\n\nPurchase Management System'.format(request.user.first_name, finished_purchase_form.OID, finished_purchase_form.productName),
                        'yee.camero23@gmail.com', #Make info@system.com email
                        [user_email],
                        fail_silently=False,
                    )
                    messages.info(request, 'Your order was successfully submitted.') #sets the on screen message for the user
                return HttpResponseRedirect('/')    
                
    else:
        purchase_form = PurchaseOrderForm(user=request.user.id)
        quote_form = QuoteForm()
    return render(request, 'main/order.html', {'purchase_form': purchase_form, 'quote_form': quote_form})

@login_required
def quotes(request):
    selected_order = Order.objects.get(OID=request.session['selected_order'])

    if request.method == "POST":
        quote_form2 = QuoteForm(request.POST, prefix="quote_form2")
        quote_form3 = QuoteForm(request.POST, prefix="quote_form3")
        user_email = request.user.email

        if quote_form2.is_valid() and quote_form3.is_valid():
            finished_quote_form2 = quote_form2.save(commit=False) 
            finished_quote_form3 = quote_form3.save(commit=False)
            finished_quote_form2.OID = selected_order #sets the OID variable into the quote
            finished_quote_form2.Supplier = quote_form2.cleaned_data['Supplier'] #sets the supplier information for quote 2
            finished_quote_form2.QPrice = quote_form2.cleaned_data['QPrice'] #sets the QPrice information for quote 2
            finished_quote_form2.QLink = quote_form2.cleaned_data['QLink'] #sets the QLink for quote 2
            saved_quote2 = finished_quote_form2.save() #saves the quote 2
            finished_quote_form3.OID = selected_order #sets the OID variable into the quote
            finished_quote_form3.Supplier = quote_form3.cleaned_data['Supplier'] #sets the supplier information for quote 3
            finished_quote_form3.QPrice = quote_form3.cleaned_data['QPrice'] #sets the QPrice information for quote 3
            finished_quote_form3.QLink = quote_form3.cleaned_data['QLink'] #sets the Qlink for quote 3
            saved_quote3 = finished_quote_form3.save() #saves the quote 3

            send_mail(
                'PURCHASE ORDER CONFIRMATION',
                'Hi {}, you\'re purchase order form has been received. Since the order is over $500, it may take longer to review. Management will get back to you after reviewing the provided quotes.\n\nPurchase Management System'.format(request.user.first_name),
                'yee.camero23@gmail.com', #Make info@system.com email
                [user_email],
                fail_silently=False,
            )
            messages.info(request, 'Your order was successfully submitted with the two extra quotes') #sets the on screen message for the user

        return HttpResponseRedirect('/')
    else:
        quote_form2 = QuoteForm(prefix="quote_form2")
        quote_form3 = QuoteForm(prefix="quote_form3")        
    return render(request, 'main/quotes.html', {'quote_form2': quote_form2, 'quote_form3': quote_form3})
    
@login_required
def contract(request):
    contracts = Contract.objects.all() #grabs all the information for all the contracts 
    return render(request, 'main/contract.html', {'contracts': contracts})

@login_required
def employee_spending(request):
    records = {}
    employee_spending = Order.objects.values('EID', 'CID').filter(isApproved=True).annotate(Sum('total'))
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
    orders = Order.objects.filter(EID = user_id)
    print(orders)
    myquoteorders = Order.objects.all().values('quoteorder__OID', 'quoteorder__QID','quoteorder__QLink', 'quoteorder__QPrice', 'quoteorder__Supplier', 'OID', 'productName', 'productDescription', 'quantity', 'total', 'dateApproved').filter(EID=user_id)
    print(myquoteorders)
    return render(request, 'main/myorders.html', {'orders': orders, 'myquoteorders': myquoteorders})

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
                x = 90
                y = 720
                z = 700
                c.setFont("Helvetica", 28)
                c.drawString(190, 780, 'Spending Report')
                c.setFont("Helvetica", 12)
                c.drawString(190, 755, 'For dates ' + start_Date + ' through ' + end_Date)

                date = str(datetime.today().strftime('%m-%d-%Y'))
                c.drawString(485, 820, date)
                c.drawString(30, 820, 'Allied Mountain')

                for contract in contracts:
                    if z < 70 or y < 70:
                        c.showPage()
                        z = 790
                        y = 810
                    running_total = 0
                    c.setFont("Helvetica", 20)
                    c.drawString(x - 50, y, 'Contract: ' + contract.CName)
                    c.setFont("Helvetica", 12)
                    c.drawString(x - 5, z, 'Budget: $' + str(contract.CBudget))
                    z -= 20
                    c.drawString(x - 5, z, 'Date Approved' + '     Item' + '                 Quantity ' + '             Price' + '                Order Total')
                    z -= 2
                    c.drawString(x - 9, z, '_______________________________________________________________')

                    z -= 15
                    for order in orders.filter(CID=contract.CID, dateApproved__range=(start_Date, end_Date)):
                        c.drawString(x, z, str(order.dateApproved.strftime('%m-%d-%Y')))
                        c.drawString(x + 91, z, order.productName)
                        c.drawString(x + 191, z, str(order.quantity))
                        c.drawString(x + 261, z, str(order.total/order.quantity))
                        c.drawString(x + 356, z, '$' + str(order.total))
                        z -= 20
                        running_total += order.total
                        if z <= 15:
                            c.showPage()
                            z = 810
                    y = z - 10
                    z = y - 10
                    if z < 15 or y < 15:
                        c.showPage()
                        z = 790
                        y = 810
                    c.drawString(x - 9, z + 25, '_______________________________________________________________')
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(342, z + 5, 'Spending Total: $' + str(running_total))
                    y = z - 30
                    z = y - 20


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
