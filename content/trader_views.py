from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Sandwich, DaySandwich, Product, Day_Payment_Line, Acumulate_payment, Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings,Total_Point_Product,Month_Total_Calculation
from .models import Sandwich_Type,Bread_Type,Katchab,Packet,Trader_Product_Restore, Customer

from django.utils import timezone
from django.db.models import Sum,Q


@login_required
def Debts(request):
    traders = Trader.objects.all()
    total_traders_money = total_traders_given = total_traders_remain = 0.0
    total_traders_money = sum(t.total_money for t in traders)
    total_traders_given = sum(t.given_money for t in traders)
    total_traders_remain = sum(t.remaining_money for t in traders)
    ## if it is not a manager user
    ## then remove manager trader
    if request.user.groups.filter(name = "managers").count() == 0:
        traders = traders.exclude(name="السيد مدير المنطقة")

    context = {
        'traders':traders,
        'total_traders_money':total_traders_money,
        'total_traders_given':total_traders_given,
        'total_traders_remain':total_traders_remain,
    }
    return render(request, 'content/Debts.html', context = context)

@login_required
def trader_page(request, trader_id):
    trader = Trader.objects.get(id = trader_id)
    trader_products_names = set()
    manager_money = 0.0
    if trader.name == "السيد مدير المنطقة":
            pass
    else:
        tps = Trader_Product.objects.filter(trader = trader).values_list('product').distinct()


        for tp in tps:
                trader_products_names.add(Product.objects.get(id = tp[0]))

    trader_pills = Trader_Payment.objects.filter(reciever = trader).order_by('-date')
    trader_transactions = Trader_Product.objects.filter(trader = trader).order_by('-date')
    trader_restores = Trader_Product_Restore.objects.filter(trader = trader).order_by('-date')
    # if trader.name == "السيد مدير المنطقة":
    #     manager_money = sum(t.total_cost for tt in trader_transactions )
    context = {
        'trader_pdata':trader,
        'trader_products':trader_products_names,
        'trader_pills':trader_pills,
        'trader_transactions':trader_transactions,
        'trader_restores':trader_restores,
        # 'manager_money':manager_money,
    }
    return render(request, 'content/trader_page.html', context)






@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_trader(request, status):
    success = failed = 0

    if request.method == "POST":
        date = request.POST['date']
        name = request.POST['name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        if status == 0 : ## add trader
            Trader.objects.create(name = name , date = date, address = address,phone_number  = phone_number )
        elif status == 1:  ## add customer
            Customer.objects.create(name = name , date = date, address = address,phone_number  = phone_number )

        success = 1


    context = {
            'success':success,
            'failed':failed,
            'status':status,

        }
    return render(request, 'content/add_trader.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def give_payment(request,trader_id):
    success = failed =total_safe =trader_remainings=  0
    trader = Trader.objects.get(id = trader_id)
    trader_bills = Trader_Product.objects.filter(trader = trader,given_status = 0).order_by('-id')
    total_bill = 0
    for bill in trader_bills :
        total_bill += bill.total_cost
    if request.method == "POST":
        # date = request.POST['date']
        date = timezone.now()
        amount = float(request.POST['total_money'])
        discount = float(request.POST['discount'])
        amount_loop = amount
        manager = Current_manager.objects.get(user = request.user)
        notes = request.POST['notes']
        bill_file = request.FILES['bill_file']
        ## get current manager safe
        m_safe = Safe_Month.objects.last()
        ## test amount against trader remaining_money
        mtc = Month_Total_Calculation.objects.last()
        #print("trader reaming money %f amount %f   safe %f"%(trader.remaining_money,amount,m_safe.money))

        if trader.remaining_money >= (amount + discount) and m_safe.money >= amount  and (amount + discount) > 0 :
            if discount > 0:
                remove_discount_from_bills(trader_bills, discount)
            if amount > 0:
                trader_bills = Trader_Product.objects.filter(trader = trader,given_status = 0).order_by('-id')
                for bill in trader_bills :
                    if amount_loop >= bill.total_cost:
                        amount_loop -=  bill.total_cost
                        bill.total_cost = 0
                        bill.given_status = 1
                        bill.save()
                    ## amount < bill.cost or amount = 0
                    ## create new bill with the remaing money and make old given =1
                    elif amount_loop != 0:
                        ## create new one
                        # Trader_Product.objects.create(product = bill.product ,manager =bill.manager ,trader = trader, total_cost = amount_loop, total_cost_old = amount_loop, date=date,given_status =1)
                        bill.total_cost -= amount_loop
                        bill.given_status =0
                        bill.save()
                        amount_loop = 0
                        break

            ## update trader , safe _ total safe
            trader.total_money -= discount
            trader.given_money += amount

            ### zeroing trader money
            # if trader.remaining_money == 0:
            #     trader.remaining_money = 0
            #     trader.given_money= 0
            #     trader.total_money = 0


            trader.save()
            ## this is a special case , occurring when we restore products to trader again
            ## we do not subtract from old bills  , and we create new return back bills so this extra amount of money occurs
            ## this is caused due to returned bills
            if trader.remaining_money == 0:
                trader_bills = Trader_Product.objects.filter(trader = trader,given_status = 0).update(given_status = 1)
            m_safe.money -= amount
            m_safe.save()
            ## create new bill
            notes +=" -- اسم التاجر -- "+trader.name
            Trader_Payment.objects.create(date = date, discount = discount, amount = amount, reciever = trader , sender= manager, notes=notes,bill_file = bill_file
                                            )
            ## create new treasure entry
            if amount > 0:
                Safe_data.objects.create(day = date, money_amount = -amount, given_person =manager, notes=notes, safe_line_status = 3 )

            mtc.safe_current_money = m_safe.money
            mtc.traders_depts -= (amount + discount)
            mtc.save()



            success = 1
        else:
            failed = 1
            if trader.remaining_money < amount:
                trader_remainings = trader.remaining_money
            elif m_safe.money < amount:
                total_safe = m_safe.money

    today_date =  timezone.now().date()
    managers = Current_manager.objects.filter(end_date__gte = today_date )

    trader_bills = Trader_Product.objects.filter(trader = trader,given_status = 0).order_by('-id')
    total_bill = 0
    for bill in trader_bills :
        total_bill += bill.total_cost
    context = {
            'success':success,
            'failed':failed,
            'bills':trader_bills,
            # 'managers':managers,
            'total_safe':total_safe,
            'trader_remainings':trader_remainings,
            'total_bill':total_bill,
            'trader':trader,
    }
    return render(request, 'content/give_payment.html',context)

def remove_discount_from_bills(bills,  discount):
    for bill in bills :
        if discount >= bill.total_cost:
            discount -=  bill.total_cost
            bill.discount += bill.total_cost
            bill.total_cost = 0
            bill.given_status = 1
            bill.save()
        ## amount < bill.cost or amount = 0
        ## create new bill with the remaing money and make old given =1
        elif discount != 0:
            ## create new one
            # Trader_Product.objects.create(product = bill.product ,manager =bill.manager ,trader = trader, total_cost = amount_loop, total_cost_old = amount_loop, date=date,given_status =1)
            bill.total_cost -= discount
            bill.given_status =0
            bill.discount += discount
            bill.save()
            discount = 0
            break

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def restore_trader_product_store(request , trader_id):
    trader = Trader.objects.get(id = trader_id)
    products = Product.objects.filter(trader = trader).distinct()
    last_quantity_packet = last_quantity = new_quantity_packet =  new_quantity = 0
    failed = success = 0
    if request.method == "POST":
        print(request.POST)
        if "last_quantity_packet" in request.POST:
            last_quantity_packet = int( request.POST['last_quantity_packet'] )
            last_quantity = int( request.POST['last_quantity'] )
        if "new_quantity" in request.POST:
            new_quantity_packet = int( request.POST['new_quantity_packet'] )
            new_quantity = int( request.POST['new_quantity'] )
        product = Product.objects.get(id = int(request.POST['product_id']))

        if check_validation_trader_restore(request, last_quantity_packet, last_quantity, new_quantity_packet, new_quantity, trader, product):
            success = 1
        else :
            failed = 1


    context = {
            'trader':trader,
            'products':products,
            'success':success,
            'failed':failed,
        }
    return render(request, 'content/restore_trader_product_store.html',context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def check_validation_trader_restore(request, lqp , lq, nqp, nq, trader, product):
    manager = Current_manager.objects.get(user = request.user)
    ## check product quantity less than or equal product in store
    last_q =(lq + (lqp * product.last_quantity_per_packet))
    new_q =(nq + (nqp * product.quantity_per_packet))
    ## check
    if last_q > product.amount_old or new_q > product.amount_new:
        return False

    ## create new restore bill
    total_bill_amount = (last_q * product.last_unit_buy_price) + (new_q * product.unit_buy_price)
    total_bill_amount = round(total_bill_amount, 2)

    ## create new bill
    Trader_Product_Restore.objects.create(quantity_new = nq, quantity_packet_new = nqp , unit_buy_price_new = product.unit_buy_price, quantity_old = lq,
                                    quantity_packet_old =  lqp, unit_buy_price_old = product.last_unit_buy_price, date = timezone.now(), total_cost = total_bill_amount,
                                    product = product, trader = trader ,  manager = manager , given_status = 0  , total_quantity_pieces = last_q + new_q  )


    ## update product in store
    product.subtract_from_product(lq, lqp, nq, nqp)

    ## update trader money
    # trader.total_money -=total_bill_amount
    # trader.remaining_money -=total_bill_amount
    # trader.save()

    ## update mtc
    mtc = Month_Total_Calculation.objects.last()
    # mtc.traders_depts -=total_bill_amount
    mtc.total_products_money -=total_bill_amount
    mtc.save()

    return True




@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_money_dept(request,trader_id):
    failed = success = 0
    trader = Trader.objects.get(id = trader_id)
    cur_m = Current_manager.objects.get(user = request.user)
    if request.method == "POST":
        amount = float(request.POST['amount'])
        notes  = request.POST['notes']
        Trader_Product.objects.create(total_cost = amount , total_cost_old = amount,given_status = 0,trader = trader,
                manager = cur_m  ,notes =notes   )

        trader.total_money += amount
        trader.remaining_money += amount
        trader.save()

        ## update mtc
        mtc = Month_Total_Calculation.objects.last()
        mtc.traders_depts += amount
        mtc.safe_current_money += amount
        mtc.save()

        ## update safe and safe data
        sfm = Safe_Month.objects.last()
        sfm.money += amount
        sfm.save()
        Safe_data.objects.create(day = timezone.now(), money_amount = amount ,given_person =cur_m ,
                notes = notes, safe_line_status =6)
        success = 1






    context = {
        "trader":trader,
        "success":success,
    }
    return render(request, 'content/add_money_dept.html',context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def restore_trader_given_bill(request, trader_id):
    trader = Trader.objects.get(id = trader_id)
    failed = success = 0

    if request.method == "POST":
        total_cost, restored_bills = get_trader_restored_bills(trader)
        amount = float(request.POST['total_money'])
        discount = float(request.POST['discount'])
        # customer = Customer.objects.get(id = int(request.POST['customer_id']))
        amount_loop = amount
        m_safe = Safe_Month.objects.last()
        if  (amount + discount ) <= total_cost :


            if discount > 0 :
                remove_discount_from_trader_restored_bills(restored_bills, discount)
                total_cost, restored_bills = get_trader_restored_bills(trader)

            trader_payment =  (amount - trader.remaining_money)
            if amount > 0  :
                remove_given_amount_from_trader_restored_bills(restored_bills, amount )
                # ## create new customer  payment
                # manager = Current_manager.objects.get(user = request.user)
                # Trader_Payment.objects.create(reciever = trader, sender=manager, date= timezone.now(), amount = amount
                #                 ,discount = discount, previos_amount = trader.remaining_money , current_amount = trader.remaining_money +( discount + amount)  , payment_type = 1)
                #
                # ## 2. safe_date
                # notes = " فاتورة نقدية مدفوعة لصالح التاجر : => " + trader.name
                # Safe_data.objects.create(day =  timezone.now(), money_amount = -amount, given_person =manager, notes=notes , safe_line_status = 8 )
                #
                # m_safe = Safe_Month.objects.last()
                # ## m_safe
                # m_safe.money -= amount
                # m_safe.save()

            #

            ## update customer given - remaining_money
            ### Big Note Here
            ### see restore_trader_product_store function in trader views for more details abount trader and mtc traders depts
            ###
            # trader.remaining_money -= amount
            trader.total_money -= amount
            trader.save()

            #
            mtc = Month_Total_Calculation.objects.last()
            # mtc.safe_current_money -= amount
            mtc.traders_depts -= amount
            mtc.save()

            success = 1

        else :
            failed =1
    total_cost, restored_bills = get_trader_restored_bills(trader)
    context = {
        'trader':trader,
        'total_cost':total_cost,

        'restored_bills':restored_bills,
    }
    return render(request, 'content/restore_trader_given_bill.html',context)



def get_trader_restored_bills(trader):
    un_paid_bills = Trader_Product_Restore.objects.filter(trader = trader , given_status = 0 , paid_status = 0)
    result = []
    total_cost = round( sum(b.remaining_amount for b in un_paid_bills) )
    # result.append(bill for bill in un_paid_bills if bill.remaining_amount < 0 )
    for bill in un_paid_bills:
        if bill.remaining_amount > 0:
            result.append(bill)

    # for bill in result :
    #     print(" unpaind  id %d" %(bill.id) )
    return (total_cost, result)


def remove_discount_from_trader_restored_bills(un_paid_bills, discount ):
    for bill in un_paid_bills:
        ## case 1
        print("discount = %f  bill.reaming_amount = %f" %(discount ,  bill.remaining_amount))
        if discount >= bill.remaining_amount :
            temp = bill.remaining_amount
            bill.discount += bill.remaining_amount ## here reaming amount is negative
            bill.paid_status = 1
            bill.given_status = 1
            bill.save()

            discount  -=  temp
        elif discount > 0 :  ## discount not greater than bill.remaining_money and discount != 0
            bill.discount += discount
            bill.save()

            discount = 0

def remove_given_amount_from_trader_restored_bills(un_paid_bills, amount ):
    for bill in un_paid_bills:
        ## case 1
        print("amount = %f  bill.reaming_amount = %f" %(amount ,  bill.remaining_amount))
        if amount >=  bill.remaining_amount :
            temp = bill.remaining_amount
            bill.given_amount += bill.remaining_amount  ## here reaming amount is negative
            bill.paid_status = 1
            bill.given_status = 1
            bill.save()

            amount  -=  temp
        elif amount > 0 :  ## discount not greater than bill.remaining_money and discount != 0
            bill.given_amount += amount
            bill.save()

            amount = 0
        if bill.remaining_amount <= .01:
            bill.paid_status = 1
            bill.given_status = 1
            bill.save()
