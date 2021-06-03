from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import  Customer, Customer_Bill,Current_manager,Customer_Payment, Safe_data, Safe_Month, Month_Total_Calculation, Point_Product_Sellings
from .models import  Point, Total_Point_Product
from django.utils import timezone

@login_required
def customers_page(request):
    customers = Customer.objects.all()
    total_traders_money = total_traders_given = total_traders_remain = 0.0
    total_traders_money = sum(t.total_money for t in customers)
    total_traders_given = sum(t.given_money for t in customers)
    total_traders_remain = sum(t.remaining_money for t in customers)


    context = {
        'customers':customers,
        'total_customers_money':total_traders_money,
        'total_customers_given':total_traders_given,
        'total_customers_remain':total_traders_remain,
    }
    return render(request, 'content/customers.html', context = context)


@login_required
def customer_page(request,customer_id):
    customer = Customer.objects.get(id = customer_id)

    un_paid_bills = Customer_Bill.objects.filter(customer = customer ,paid_status = 0 , given_status = 1 , bill_type = 0).order_by('-date')
    paid_bills = Customer_Bill.objects.filter(customer = customer ,paid_status = 1 , given_status = 1, bill_type = 0).order_by('-date')
    retunred_bills = Customer_Bill.objects.filter(customer = customer ,paid_status__in=[0,1] , given_status__in = [0,1], bill_type = 1).order_by('-date')

    paid_given_bill = Customer_Payment.objects.filter(g_user = customer, payment_type = 0).order_by('-date')
    restored_paid_bills = Customer_Payment.objects.filter(g_user = customer, payment_type = 1).order_by('-date')

    context = {
        'customer':customer,
        'un_paid_bills':un_paid_bills,
        'paid_bills':paid_bills,
        'retunred_bills':retunred_bills,

        'paid_given_bill':paid_given_bill,
        'restored_paid_bills':restored_paid_bills,

    }
    return render(request, 'content/customer_page.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def customer_all_unpaid_bills(request,customer_id):
    customer = Customer.objects.get(id = customer_id)

    un_paid_bills = Customer_Bill.objects.filter(customer = customer ,paid_status = 0 , given_status = 1 , bill_type = 0).order_by('date')

    total_bills_cost = round( sum( t.total_bill_cost for t in un_paid_bills), 1 ) ### 0
    bills_restored_amount_cost = round( sum( t.restored_amount_cost for t in un_paid_bills), 1 )  ### 1

    bills_main_discount = round( sum( t.main_discount for t in un_paid_bills), 1 )  ### 2
    bills_add_discount = round( sum( t.discount for t in un_paid_bills), 1 )     ### 3
    bills_total_discount = round( sum( t.total_discount for t in un_paid_bills), 1 )     ### 4


    bills_required_amount = round( sum( t.required_amount for t in un_paid_bills), 1 )  ### 5
    bills_restored_amount_cost_ad = round( sum( t.restored_amount_cost_ad for t in un_paid_bills), 1 )  ### 6

    bills_given_amount = round( sum( t.given_amount for t in un_paid_bills), 1 )     ### 7
    bills_remaining_amount = round( sum( t.remaining_amount for t in un_paid_bills), 1 )     ### 8

    totals = [total_bills_cost, bills_restored_amount_cost, bills_main_discount,  bills_add_discount, bills_total_discount, bills_required_amount, ]

    totals.append(bills_restored_amount_cost_ad)
    totals.append(bills_given_amount)
    totals.append(bills_remaining_amount)

    context = {
        'customer':customer,
        'un_paid_bills':un_paid_bills,
        'totals':totals,


    }
    return render(request, 'content/customer_all_unpaid_bills.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def customer_payment(request,customer_id):
    customer = Customer.objects.get(id = customer_id)
    un_paid_bills = Customer_Bill.objects.filter(customer = customer ,paid_status = 0 , given_status = 1)
    failed = success = 0
    if request.method == "POST":
        amount = float(request.POST['total_money'])
        discount = float(request.POST['discount'])
        # customer = Customer.objects.get(id = int(request.POST['customer_id']))
        amount_loop = amount

        if amount <= customer.remaining_money and  discount <= customer.remaining_money and amount >= 0 \
                        and (amount + discount ) <= customer.remaining_money and len(un_paid_bills) > 0 :
            if discount > 0  :
                remove_discount_from_bills(un_paid_bills,discount )

            ## update bills with the given amount
            un_paid_bills = Customer_Bill.objects.filter(customer = customer ,paid_status = 0 , given_status = 1)
            if amount > 0  :
                add_amount_to_bills(un_paid_bills, amount )
                ## create new customer  payment
                manager = Current_manager.objects.get(user = request.user)
                Customer_Payment.objects.create(g_user = customer, t_user=manager, date= timezone.now(), amount = amount
                                ,discount = discount, previos_amount =customer.remaining_money , current_amount = customer.remaining_money  - ( discount + amount)   )

                ## 2. safe_date
                notes = " فاتورة نقدية محصلة من " + customer.name
                Safe_data.objects.create(day =  timezone.now(), money_amount = amount, given_person =manager, notes=notes , safe_line_status = 6 )

                m_safe = Safe_Month.objects.last()
                ## m_safe
                m_safe.money +=amount
                m_safe.save()

            ## update customer given - remaining_money
            customer.given_money += amount
            customer.total_money -= discount
            customer.normalize()

            mtc = Month_Total_Calculation.objects.last()
            mtc.safe_current_money += amount
            mtc.total_profit -= discount
            mtc.save()

            success = 1

        else :
            failed =1
    context = {
        'customer':customer,
        'un_paid_bills':un_paid_bills,
        'failed':failed ,
        'success':success ,

    }
    return render(request, 'content/customer_payment.html', context)


def remove_discount_from_bills(un_paid_bills, discount ):
    for bill in un_paid_bills:
        ## case 1
        if discount >= bill.remaining_amount:
            temp = bill.remaining_amount
            bill.discount += bill.remaining_amount
            bill.paid_status = 1
            bill.save()

            discount  -= temp
        elif discount > 0 :  ## discount not greater than bill.remaining_money and discount != 0
            bill.discount += discount
            bill.save()

            discount = 0

def add_amount_to_bills(un_paid_bills, amount ):
    for bill in un_paid_bills:
        ## case 1
        if amount >= bill.remaining_amount:
            temp = bill.remaining_amount
            bill.given_amount += bill.remaining_amount
            bill.paid_status = 1
            bill.save()

            amount  -= temp
        elif amount > 0 :  ## discount not greater than bill.remaining_money and discount != 0
            bill.given_amount += amount
            bill.save()

            amount = 0
        if bill.remaining_amount <= .01:
            bill.paid_status = 1
            bill.save()




@login_required
def customer_bill_details(request, bill_id):
    bill = Customer_Bill.objects.get(id = bill_id)
    context = {

        'bill':bill ,

    }

    return render(request, 'content/customer_bill_details.html', context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def restore_customer_bill(request, customer_id):
    customer = Customer.objects.get(id = customer_id)
    customer_bill = None
    if request.method == "POST":
        try :
            customer_bill = Customer_Bill.objects.get(id = int(request.POST['bill_id']) , customer =customer )
        except :
            customer_bill = None
    context = {

        'customer':customer ,
        'bill':customer_bill ,

    }

    return render(request, 'content/restore_customer_bill.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def restore_customer_bill_line(request, line_id):
    bill_line = Point_Product_Sellings.objects.get(id = line_id)
    customer_bill = Customer_Bill.objects.get(id = bill_line.bill.id)
    customer = customer_bill.customer
    success = failed = 0


    if request.method == "POST":
        amount = int(request.POST['amount'])
        if amount <= (bill_line.total_quantity - bill_line.restored_amount)  :
            restored_bill = create_new_restore_customer_bill(request, customer)
            restore_line   = create_new_restore_line(amount, bill_line, customer_bill , customer, restored_bill)
            success = 1


        else :
            failed = 1





    context = {

        'customer':customer_bill.customer ,
        'bill':customer_bill ,
        'success':success ,
        'failed':failed ,

    }

    return render(request, 'content/restore_customer_bill.html', context)


def create_new_restore_customer_bill(request, customer):
    ## create new restore bill
    cust_cur_bill = Customer_Bill.objects.filter(given_status = 0, customer = customer,bill_type = 1 ).last()
    if cust_cur_bill == None:
        ## create new one
        print("create new restore bill")
        cur_m = Current_manager.objects.get(user = request.user)
        Customer_Bill.objects.create(customer = customer, manager = cur_m, bill_type = 1)
        cust_cur_bill =  Customer_Bill.objects.filter(given_status = 0, customer = customer, bill_type = 1).last()

    return cust_cur_bill



def create_new_restore_line(amount, bill_line, customer_bill, customer, restored_bill):
    bill_total_money_sell = round(bill_line.unit_sell_price * amount , 1)
    new_restore = old_restore = 0
    ### if bill has both old and new product items

    if bill_line.total_quantity_new > 0 and bill_line.total_quantity_old > 0 :
        ## check to restore old only
        #########NOtE => Big Note Here !!
        ## bugs will occur here if i have both new and old product in the same line
        ### Notes
        if amount >=  bill_line.total_quantity_old and bill_line.total_quantity_old > 0  :
            old_restore =  bill_line.total_quantity_old
            amount -=  bill_line.total_quantity_old

        elif amount < bill_line.total_quantity_old:
            old_restore =  amount
            amount = 0

        ### if amount > total_old then amount > 0
        if amount > 0 :
            if amount ==  bill_line.total_quantity_new :
                new_restore =  bill_line.total_quantity_new
                amount =  0

            elif amount < bill_line.total_quantity_new:
                new_restore =  amount
                amount = 0



    elif bill_line.total_quantity_new > 0 :
        new_restore = amount
        amount = 0


    elif bill_line.total_quantity_old > 0 :
        old_restore = amount





    bill_total_money_buy = round((old_restore * bill_line.unit_buy_price_old ) + (new_restore * bill_line.unit_buy_price_new ) , 1)

    bill_line.restored_amount += (old_restore + new_restore)
    bill_line.restored_amount_cost += bill_total_money_sell
    bill_line.restored_amount_cost_ad +=  ( bill_total_money_sell -  (amount * bill_line.discount_per_unit) )
    bill_line.restored_amount_cost_buy +=  bill_total_money_buy

    bill_line.save()
    # create new restore bill line with both new and old bills
    # Point_Product_Sellings.objects.create(money_quantity_sell = bill_total_money_sell ,date = timezone.now(),quantity_new = new_restore, quantity_old = old_restore ,
    #                                         product = bill_line.product, Point = bill_line.Point, money_quantity_buy = bill_total_money_buy, total_quantity_new = new_restore , total_quantity_old = old_restore,
    #                                         unit_sell_price = bill_line.unit_sell_price ,unit_buy_price_new = bill_line.unit_buy_price_new ,unit_buy_price_old =bill_line.unit_buy_price_old ,
    #                                         discount_per_unit = bill_line.discount_per_unit , bill = customer_bill , line_type = 1)


    ## create new restore bill line with both new and old bills
    Point_Product_Sellings.objects.create(money_quantity_sell = bill_total_money_sell ,date = timezone.now(),quantity_new = new_restore, quantity_old = old_restore ,
                                            product = bill_line.product, Point = bill_line.Point, money_quantity_buy = bill_total_money_buy, total_quantity_new = new_restore , total_quantity_old = old_restore,
                                            unit_sell_price = bill_line.unit_sell_price ,unit_buy_price_new = bill_line.unit_buy_price_new ,unit_buy_price_old =bill_line.unit_buy_price_old ,
                                            discount_per_unit = bill_line.discount_per_unit , bill = restored_bill , line_type = 1, come_from_line_id = bill_line.id)


    return 1



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def confirm_restore_customer_bill(request, customer_id):
    customer = Customer.objects.get(id = customer_id)
    customer_bill = None
    try :
        customer_bill =  Customer_Bill.objects.filter(given_status = 0, customer = customer,bill_type = 1 ).last()
    except :
        customer_bill = None
    if request.method == "POST":
        restore_product_to_points(customer_bill)
        customer_bill.given_status = 1
        customer_bill.all_lines.update(taken_status = 1)
        customer_bill.paid_status = 1
        customer_bill.save()
        customer_bill =  Customer_Bill.objects.filter(given_status = 0, customer = customer,bill_type = 1 ).last()
    context = {

        'customer':customer ,
        'bill':customer_bill ,

    }

    return render(request, 'content/confirm_restore_customer_bill.html', context)

def restore_product_to_points(customer_bill):
    bill_lines = customer_bill.all_lines

    for line in bill_lines:
        ttp = Total_Point_Product.objects.get(product = line.product,Point = line.Point )
        print("total_quantity before restore %d" %(ttp.total_product_quantity) )
        ttp.add_to_product(line.quantity_old , 0, line.quantity_new , 0)
        ttp.total_product_quantity += (line.quantity_old + line.quantity_new)
        ttp.save()
        print("total_quantity after restore %d" %(ttp.total_product_quantity) )
        ##get point
        point = Point.objects.get(id = line.Point.id)
        point.total_money_raw += line.money_quantity_buy
        point.save()


    ## get bills cost buy
    customer_bill_cost_buy = sum(line.money_quantity_buy for line in bill_lines)
    total_bill_required = sum(line.required_amount for line in bill_lines)
    ##get month_tc
    mtc = Month_Total_Calculation.objects.last()
    mtc.total_products_money_points += customer_bill_cost_buy
    mtc.total_profit -= (total_bill_required - customer_bill_cost_buy )

    mtc.save()

    ## get bills cost sell
    customer_bill_cost_sell = sum(line.required_amount for line in bill_lines)
    ##get month_tc
    customer = customer_bill.customer
    customer.total_money -= customer_bill_cost_sell
    customer.save()





@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_restored_customer_bill_line(request, line_id):
    ## restored bill line
    bill_line = Point_Product_Sellings.objects.get(id = line_id)
    customer_bill = Customer_Bill.objects.get(id = bill_line.bill.id)
    customer = customer_bill.customer
    success = failed = 0


    ###  sold bill line created in the sold bill,  delete it
    come_from_bill_line = Point_Product_Sellings.objects.get(id = bill_line.come_from_line_id)
    come_from_bill_line.restored_amount -= (bill_line.quantity_new + bill_line.quantity_old)

    res_amount = (bill_line.quantity_new + bill_line.quantity_old)

    come_from_bill_line.restored_amount_cost -= bill_line.money_quantity_sell
    come_from_bill_line.restored_amount_cost_ad -=  ( bill_line.money_quantity_sell -  (res_amount * bill_line.discount_per_unit) )
    come_from_bill_line.restored_amount_cost_buy -=  bill_line.money_quantity_buy


    come_from_bill_line.save()

    bill_line.delete()



    return redirect('content:confirm-restore-customer-bill', customer.id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def customer_give_payment(request, customer_id):
    customer = Customer.objects.get(id = customer_id)
    failed = success = 0
    if request.method == "POST":
        amount = float(request.POST['total_money'])
        discount = float(request.POST['discount'])
        # customer = Customer.objects.get(id = int(request.POST['customer_id']))
        amount_loop = amount
        m_safe = Safe_Month.objects.last()
        if  (amount + discount ) <= (customer.remaining_money * -1) and  m_safe.money >= amount :
            restored_bills = get_customer_restored_bills(customer)
            if discount > 0 :
                remove_discount_from_restored_bills(restored_bills, discount)

            restored_bills = get_customer_restored_bills(customer)
            if amount > 0  :
                remove_given_amount_from_restored_bills(restored_bills, amount )
                ## create new customer  payment
                manager = Current_manager.objects.get(user = request.user)
                Customer_Payment.objects.create(g_user = customer, t_user=manager, date= timezone.now(), amount = amount
                                ,discount = discount, previos_amount = customer.remaining_money , current_amount = customer.remaining_money +( discount + amount)  , payment_type = 1)

                ## 2. safe_date
                notes = " فاتورة نقدية مدفوعة لصالح العميل : " + customer.name
                Safe_data.objects.create(day =  timezone.now(), money_amount = -amount, given_person =manager, notes=notes , safe_line_status = 7 )

                m_safe = Safe_Month.objects.last()
                ## m_safe
                m_safe.money -= amount
                m_safe.save()

            #

            ## update customer given - remaining_money
            customer.given_money -= amount
            customer.total_money += discount
            customer.normalize()

            #
            mtc = Month_Total_Calculation.objects.last()
            mtc.safe_current_money -= amount
            mtc.save()

            success = 1

        else :
            failed =1

    context = {
        'customer':customer,
        'success':success ,
        'failed':failed ,
    }
    return render(request, 'content/customer_give_payment.html', context)


def get_customer_restored_bills(customer):
    un_paid_bills = Customer_Bill.objects.filter(customer = customer ,bill_type = 0, given_status = 1)
    result = []
    # result.append(bill for bill in un_paid_bills if bill.remaining_amount < 0 )
    for bill in un_paid_bills:
        if bill.remaining_amount < 0:
            result.append(bill)

    # for bill in result :
    #     print(" unpaind  id %d" %(bill.id) )
    return result

def remove_discount_from_restored_bills(un_paid_bills, discount ):
    for bill in un_paid_bills:
        ## case 1
        if discount >= (bill.remaining_amount * -1):
            temp = bill.remaining_amount
            bill.given_amount += bill.remaining_amount ## here reaming amount is negative
            bill.paid_status = 1
            bill.save()

            discount  -= (temp * -1)
        elif discount > 0 :  ## discount not greater than bill.remaining_money and discount != 0
            bill.given_amount -= discount
            bill.save()

            discount = 0

def remove_given_amount_from_restored_bills(un_paid_bills, amount ):
    for bill in un_paid_bills:
        ## case 1
        if amount >= (-1 * bill.remaining_amount ):
            temp = bill.remaining_amount
            bill.given_amount += bill.remaining_amount  ## here reaming amount is negative
            bill.paid_status = 1
            bill.save()

            amount  -= ( temp * -1)
        elif amount > 0 :  ## discount not greater than bill.remaining_money and discount != 0
            bill.given_amount += amount
            bill.save()

            amount = 0
        if bill.remaining_amount <= .01:
            bill.paid_status = 1
            bill.save()





@login_required
def customer_bill_details_page(request):
    bill = None
    if request.method == "POST":
        try:
            bill = Customer_Bill.objects.get(id = int(request.POST['bill_id']) )
        except :
            bill = None

    context = {
        'bill' : bill,
    }
    return render(request,"content/customer_bill_details_page.html", context = context)



#########################
