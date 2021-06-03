from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Sandwich, DaySandwich, Product, Day_Payment_Line, Acumulate_payment, Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings,Total_Point_Product,Month_Total_Calculation
from .models import Trader_Product_Data, Customer, Customer_Bill
from datetime import datetime,date
# from django.db.models import Q
from django.utils import timezone
import decimal
from django.db.models import Sum,Q
# Create your views here.
from .sandwich_views import add_sandwich_components,add_new_sandwitch ,sandwitch,add_sandwitch,add_sandwich_component_names, sand_current_materials, sand_all_buy
from .trader_views import Debts, trader_page,add_trader,give_payment,restore_trader_product_store, add_money_dept, restore_trader_given_bill
from .points_views import points , point_page, point_trader_page, add_new_point_bill , add_new_point_sellings,add_new_point_payments, add_new_point_seller
from .points_views import  restore_point_bill_sell, restore_point_product_store, point_to_point_product, point_total_product, all_discount_bills,get_all_bills_with_discount

from .daily_views import daily_reports,daily_transaction
from .product_views import product_page, update_product, update_product_prices,new_product_type, reduce_product_amount_store, add_new_mu, delete_mu
from .customers_views import customers_page ,customer_page,customer_payment, customer_bill_details, restore_customer_bill,restore_customer_bill_line, confirm_restore_customer_bill
from .customers_views import delete_restored_customer_bill_line,customer_give_payment, customer_all_unpaid_bills, customer_bill_details_page

def home(request):
    failed = 0

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None :
            current_manager = Current_manager.objects.filter(user = user).first()
            if current_manager != None  and current_manager.active_status == 1:
                request.session.set_expiry(0)
                failed =0
                login(request, user)
                print('username: ' + request.user.username + ' has log in to system at ' + str(datetime.now()))
                return redirect("content:receipt_net")
            else :
                failed =1
        else:
            failed =1
    context = {'failed' : failed}
    return render(request, 'content/login.html', context = context)
    return render(request, 'content/login.html')

@login_required
def logout_view(request):

    if request.user != None:
            userna = request.user.username
            logout(request)
            print('username: ' + userna + ' has log out of system at ' + str(datetime.now()))

    return redirect('content:login-page')


@login_required
def manager(request,manager_id):

        context = {

        }
        return render(request, 'content/manager.html',context = context)


@login_required
def store(request):

        products = Product.objects.all()

        total = 0
        if products != None :
            total = sum(p.total_cost for p in products)
        context = {
            'products':products,
            'total':round(total,1),
        }
        # print( len(products))

        return render(request, 'content/store.html',context = context)




@login_required
def Treasury_receipt(request):
    current_manager = Current_manager.objects.filter(user = request.user).first()
    transactions = Safe_data.objects.filter(day__date__gte = current_manager.start_date , day__date__lte=  current_manager.end_date).order_by('-id')
    m_safe = Safe_Month.objects.last()
    context = {
        'transactions':transactions,
        'safe':m_safe,
    }
    return render(request, 'content/Treasury_receipt.html',context)

@login_required
def receipt_net(request):
    sand_buy = sand_all_buy()
    mtc = Month_Total_Calculation.objects.last()
    # next_manager_gmoney = mtc.traders_depts - (mtc.total_products_money + mtc.total_products_money_points +sand_buy )
    # next_manager_gmoney = round(next_manager_gmoney , 0)
    total_money_with_customers_d = mtc.total_products_money_points + mtc.total_products_money + sand_buy+mtc.customers_depts +mtc.safe_current_money
    total_money_with_customers_d = round(total_money_with_customers_d , 1)
    total_net = total_money_with_customers_d - mtc.traders_depts

    given_boss_gmoney = round(total_net - mtc.customers_depts   , 1 )

    ### totalt profit = total_net + total_withdrawings
    total_profit = total_net  + mtc.total_withdrawings
    three_percentage = round((total_profit) *.03 , 0)
    one_percentage = round((total_profit) *.01 , 0)
    cur_m = Current_manager.objects.get(user = request.user)


    bills_with_discount = get_all_bills_with_discount(request)

    total_discounts = sum(b.total_discount for b in bills_with_discount )

    context={
        'mtc':mtc,
        'sand_st':sand_buy,
        # 'next_manager_gmoney':next_manager_gmoney,
        'given_boss_gmoney':given_boss_gmoney,
        'three_percentage':three_percentage,
        'one_percentage':one_percentage,
        'total_discounts':total_discounts,
        'total_money_with_customers_d':total_money_with_customers_d,
        'total_net':total_net,

    }
    return render(request, 'content/receipt_net.html', context)

@login_required
def monthly_receipt(request):
    today_date = timezone.now().date()
    manager = Current_manager.objects.filter(user = request.user ).first()
    mtc = Month_Total_Calculation.objects.filter(current_manager = manager).last()

    context = {
        'mtc':mtc,
    }
    return render(request, 'content/monthly_receipt.html',context)


@login_required
def withdrawings_all(request):
    current_manager = Current_manager.objects.filter(user = request.user).first()
    transactions = withdrawings.objects.filter(day__date__gte = current_manager.start_date , day__date__lte=  current_manager.end_date).order_by('-id')
    total_tr_money = 0

    for t in transactions:
        total_tr_money += t.money_amount
    context = {
        'transactions':transactions,
        'total_tr_money':total_tr_money,
    }
    return render(request, 'content/withdrawings.html',context)




@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def treasury_transactions(request):
    success = failed =0

    if request.method == "POST":
        # date = request.POST['date']
        date = timezone.now()
        amount = float(request.POST['amount'])
        manager = Current_manager.objects.get(user = request.user)
        notes = request.POST['notes']
        ## get current manager safe
        m_safe = Safe_Month.objects.last()
        mtc = Month_Total_Calculation.objects.last()
        ## test amount against trader remaining_money
        if amount < 0:
            if  m_safe.money >= abs(amount)  :
                m_safe.money -= abs(amount)
                m_safe.save()
                mtc.safe_current_money = m_safe.money
                mtc.save()
                Safe_data.objects.create(day = date, money_amount = amount, given_person =manager, notes=notes ,safe_line_status = 6 )
                success = 1
            else:
                failed = 1

        elif amount > 0 : ## positive amount
            m_safe.money += amount
            m_safe.save()
            mtc.safe_current_money = m_safe.money
            mtc.save()
            Safe_data.objects.create(day = date, money_amount = amount, given_person =manager, notes=notes )
            success = 1



    today_date =  timezone.now().date()
    # managers = Current_manager.objects.filter(end_date__gte = today_date )
    # traders = Trader.objects.all()
    context = {
            'success':success,
            'failed':failed,
            # 'managers':managers,

    }
    return render(request, 'content/treasury_transactions.html',context)







@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def withdrawings_transactions(request):
    success = failed =0

    if request.method == "POST":
        # date = request.POST['date']
        date = timezone.now()
        amount = float(request.POST['amount'])
        notes = request.POST['notes']
        ## get current manager safe
        m_safe = Safe_Month.objects.last()
        ## test amount against trader remaining_money
        manager = Current_manager.objects.filter(user = request.user).first()
        mtc = Month_Total_Calculation.objects.last()
        if m_safe.money >= abs(amount)  :
            withdrawings.objects.create(day = date, money_amount = amount, descreption=notes , status = 2 )
            Safe_data.objects.create(day = date, money_amount = -amount, given_person =manager, notes=notes , safe_line_status = 1 )

            m_safe.money -= abs(amount)
            m_safe.save()
            ## update mtc
            mtc.total_withdrawings += abs(amount)
            mtc.safe_current_money -= abs(amount)
            mtc.save()
            success = 1
        else:
            failed = 1



    context = {
            'success':success,
            'failed':failed,


    }
    return render(request, 'content/withdrawings_transactions.html', context)






@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_new_sellings(request):
    failed = success =total_comings=  0

    if request.method == 'POST':
        sell_amount = int(request.POST['quantity'])
        if 'total_comings' in request.POST:
            try :
                total_comings = float(request.POST['total_comings'])
            except:
                total_comings = 0.0
        product = Product.objects.get(id = int(request.POST['product_id']))
        if product.quantity >= sell_amount:
            product.quantity -= sell_amount
            product.save()
            total_cost = sell_amount * product.unit_buy_price
            total_payment = sell_amount * product.unit_sell_price
            profit = total_payment - total_cost
            ## create new Day_Payment_Line
            if sell_amount != 0:
                Day_Payment_Line.objects.create(product = product , sold_quantity = sell_amount,total_payment = total_payment,
                                            day = timezone.now().date(), total_cost = total_cost, profit = profit)

            ## check to see if there is an existing today accumulator
            today_acc =Acumulate_payment.objects.filter(date = timezone.now().date()).first()
            if today_acc != None:
                today_acc.payment_until_now +=(total_payment)
                today_acc.total_profit_until_now += (profit)
                today_acc.comings_today += (total_comings)
                today_acc.comings_until_now += (total_comings)
                today_acc.save()
            else: ## create new today accumulator and accumulate to previos day
                user_start_date = Current_manager.objects.filter(end_date__gte = timezone.now().date() ).first().start_date
                if user_start_date < timezone.now().date():
                    last_acc =Acumulate_payment.objects.last()
                    today_acc = Acumulate_payment.objects.create(date = timezone.now().date())
                    today_acc.payment_until_now += (total_payment) + last_acc.payment_until_now
                    today_acc.total_profit_until_now += (profit)+ last_acc.total_profit_until_now
                    today_acc.comings_until_now += (total_comings)+ last_acc.comings_until_now
                    today_acc.comings_today += (total_comings)
                    today_acc.save()

                else: ## first day user
                    today_acc = Acumulate_payment.objects.create(date = timezone.now().date())
                    today_acc.payment_until_now += (total_payment)
                    today_acc.total_profit_until_now += (profit)
                    today_acc.comings_today += (total_comings)
                    today_acc.comings_until_now += (total_comings)
                    today_acc.save()

        else:
            failed = 1

    products = Product.objects.all()

    context = {'products':products , 'failed':failed, 'success':success,}
    return render(request, 'content/add_new_sellings.html',context = context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_single_withdrawing(request):
    success = failed = 0
    cur_m = Current_manager.objects.get(user = request.user)
    all_with = withdrawings.objects.filter(day__date__gte =cur_m.start_date , day__date__lte = cur_m.end_date  ,status = 2 )
    if request.method == "POST":
        money_amount = float(request.POST['money_amount'])
        w_data =  withdrawings.objects.get(id = int(request.POST['witd_id']))
        if money_amount == w_data.money_amount :
            success = 1
            ## update mtc
            mtc = Month_Total_Calculation.objects.last()
            mtc.total_withdrawings -= w_data.money_amount
            mtc.safe_current_money += w_data.money_amount
            mtc.save()
            ## update safe
            sm = Safe_Month.objects.last()
            sm.money += w_data.money_amount
            sm.save()

            ## create new safe data entry
            notes  = "نثرية مسترجعة " +  w_data.descreption
            Safe_data.objects.create(day = timezone.now(), money_amount =  w_data.money_amount , given_person = cur_m,
                            notes =notes ,safe_line_status = 1)
            w_data.delete()

        else :
            failed = 1


    context = {
            'all_with' :all_with,
            'success' :success,
            'failed' :failed,
    }
    return render(request, 'content/delete_single_withdrawing.html',context = context)


@login_required
def denied(request):
    return render(request, 'content/denied.html')



@login_required
def change_password(request):

    success = failed = 0
    if request.method == "POST" :
            cur_user = request.user
            userna=cur_user.username

            old_pass = request.POST['password_old']
            new_pass_1 = request.POST['password_new_1']
            new_pass_2 = request.POST['password_new_2']

            ## check old pass
            if cur_user.check_password(old_pass):
                ## check new pass match
                if new_pass_1 == new_pass_2 :
                    cur_user.set_password(new_pass_1)
                    cur_user.save()
                    logout(request)
                    print('username: ' + userna + ' has log out of system at ' + str(datetime.now()))
                    return redirect('content:login-page')
                else :
                    failed = 2
            else:
                failed = 1
    context = {
        'success':success,
        'failed':failed,
    }
    return render(request, "content/change_password.html", context = context)



@login_required
def search_canteen(request):
    products = Product.objects.all()
    # sandwich = Sandwich.objects.all()
    store_product = tpps = None
    data = []
    if request.method == "POST":
        # print(request.POST)
        ## store product
        store_product = Product.objects.get(id = int(request.POST['product_id']))
        ##point products
        tpps = Total_Point_Product.objects.filter(product = store_product)

    if store_product != None :
        data.append(store_product)
    if tpps != None :
        for tpp in tpps:
            data.append(tpp )
        print("# data %d" %(len(data)))

    context = {
        'products':products,
        'store_product':store_product,
        'tpps':tpps,
        'data':data,
    }
    return render(request, "content/search_canteen.html", context = context)
