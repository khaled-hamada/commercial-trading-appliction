from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Sandwich, DaySandwich, Product, Day_Payment_Line, Acumulate_payment, Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings,Total_Point_Product,Month_Total_Calculation
from .models import Sandwich_Type,Bread_Type,Katchab,Packet, Customer_Bill, Customer_Payment

from django.utils import timezone
from django.db.models import Sum,Q



@login_required
def daily_reports(request):
        from_date = to_date = timezone.now().date()
        if request.method == "POST":
            from_date = request.POST['from_date']
            to_date = request.POST['to_date']
        ## 1. withdrawings
        transactions = withdrawings.objects.filter(day__date__gte = from_date , day__date__lte = to_date).order_by('-id')
        total_tr_money = 0
        if transactions != None :
            total_tr_money =round(sum( t.money_amount for t in transactions),2)

        ## todaty traders bills
        trader_bills = Trader_Product.objects.filter(date__date__gte = from_date , date__date__lte = to_date).order_by('-id')
        trader_all = 0
        if trader_bills != None:
            trader_all = round(sum( t.total_cost_old for t in trader_bills), 2)
        ## todaty traders payments
        trader_payments = Trader_Payment.objects.filter(date__date__gte = from_date , date__date__lte = to_date).order_by('-id')
        trader_payments_all = 0
        if trader_payments != None:
            trader_payments_all = round(sum( t.amount for t in trader_payments), 2)


        ## points bills out of store
        points_bills = Point_Product.objects.filter(date__date__gte = from_date , date__date__lte = to_date).order_by('-id')
        points_all = 0
        if points_bills != None:
            points_all =round(sum( t.money_quantity for t in points_bills if t.notes == ""),2)

        ## points payments
        points_sellings = Customer_Bill.objects.filter(date__date__gte = from_date , date__date__lte = to_date, bill_type = 0).order_by('-id')
        ## totals
        points_sellings_bd = points_sellings_ad = total_discounts = customers_depts =net_payments= 0
        if len(points_sellings) > 0 :
            points_sellings_bd = round(sum( (t.total_bill_cost_ar ) for t in points_sellings) , 2)
            points_sellings_ad = round(sum( t.required_amount for t in points_sellings) , 2)
            total_discounts = round(sum( t.total_discount for t in points_sellings) , 2)
            customers_depts = round(sum( t.remaining_amount for t in points_sellings) , 2)
            net_payments = points_sellings_ad - customers_depts

        ## safe data
        safe = Safe_data.objects.filter(day__date__gte = from_date , day__date__lte = to_date).order_by('-id')
        total_s = 0
        if safe != None:
            total_s  = round(sum( t.money_amount for t in safe) , 2)


        paid_given_bill = Customer_Payment.objects.filter(date__date__gte = from_date , date__date__lte = to_date, payment_type = 0).order_by('-date')
        total_amount_given = round( sum(bill.amount for bill in paid_given_bill))
        restored_paid_bills = Customer_Payment.objects.filter(date__date__gte = from_date , date__date__lte = to_date, payment_type = 1).order_by('-date')
        total_amount_restored = round( sum(bill.amount for bill in restored_paid_bills))


        context = {
            'transactions':transactions,
            'total_tr_money':total_tr_money,

            'trader_bills':trader_bills,
            'trader_all':trader_all,

            'trader_payments':trader_payments,
            'trader_payments_all':trader_payments_all,

            'points_bills':points_bills,
            'points_all':points_all,

            'points_sellings':points_sellings,
            'points_sellings_bd':points_sellings_bd,
            'points_sellings_ad':points_sellings_ad,
            'total_discounts':total_discounts,
            'customers_depts':customers_depts,
            'net_payments':net_payments,

            'safe':safe,
            'total_s':total_s,

            'paid_given_bill':paid_given_bill,
            'total_amount_given':total_amount_given,

            'restored_paid_bills':restored_paid_bills,
            'total_amount_restored':total_amount_restored,
        }
        return render(request, 'content/daily_reports.html',context = context)




@login_required
def daily_transaction(request):
    from_date = to_date = timezone.now().date()

    if request.method == "POST":
        from_date = request.POST['from_date']
        to_date = request.POST['to_date']
    today_date =  timezone.now().date()
    user = Current_manager.objects.filter(user = request.user ).first()
    ## daily sold products by points
    products = Product.objects.all()
    # tpp = Total_Point_Product.objects.all()
    transactions = []
    total_buy = total_sell = total_profit = total_discounts_all = total_required_all= 0.0
    for p in products :
        tr = []

        ## old quantity
        ## get all p transactions
        pps = Point_Product_Sellings.objects.filter(date__date__gte = from_date ,date__date__lte = to_date, taken_status = 1 , product=p , line_type = 0).exclude(Point__name__in =["stuff",'manager'])
        # tpp = Total_Point_Product.objects.filter(product=p).first()
        if len(pps) > 0 :

            tr.append(p.name)  ## item.0


            total_quantity_sold = sum( (pp.total_quantity_old + pp.total_quantity_new - pp.restored_amount) for pp in pps)
            tr.append(total_quantity_sold)  ## item.1
            # tr.append(p.unit_sell_price)  ## item.7

            total_money_buy =  sum( (pp.money_quantity_buy - pp.restored_amount_cost_buy) for pp in pps)
            total_money_buy = round(total_money_buy , 2)

            total_money_sold =  sum( (pp.money_quantity_sell - pp.restored_amount_cost ) for pp in pps)
            total_money_sold = round(total_money_sold , 2)

            total_discounts = sum( (b.total_discount - (b.restored_amount * b.discount_per_unit) ) for b in pps )
            total_discounts = round(total_discounts , 2)

            total_required = sum(b.required_amount for b in pps )
            total_required = round(total_required , 2)

            tr.append(total_money_buy)  ## item.2
            tr.append(total_money_sold)  ## item.3
            tr.append(total_discounts)  ## item.4
            tr.append(total_required)  ## item.5

            profit = round( total_required - total_money_buy , 2)

            tr.append(profit) ## item.6

            transactions.append(tr)

            total_buy += total_money_buy
            total_sell +=  total_money_sold
            total_discounts_all +=  total_discounts
            # total_required_all +=  total_required

    ## same for all sandwiches type
    all_sand =  Sandwich.objects.all()
    for s in all_sand :
        tr = []
        sand_sellings = DaySandwich.objects.filter(date__date__gte = from_date ,date__date__lte = to_date, sandwich=s)

        ## if any
        if len(sand_sellings) >0:
            tr.append(str(s))
            total_quantity_sold = sum( ss.number for ss in sand_sellings)
            tr.append(total_quantity_sold)  ## item.1
            # tr.append(p.unit_sell_price)  ## item.7

            total_money_buy =  sum( (pp.total_cost) for pp in sand_sellings)
            total_money_buy = round(total_money_buy , 2)

            total_money_sold =  sum( (pp.total_return) for pp in sand_sellings)
            total_money_sold = round(total_money_sold , 2)
            total_discounts = 0
            # total_discounts = round(total_discounts , 2)

            total_required = total_money_sold
            # total_required = round(total_required , 2)
            tr.append(total_money_buy)  ## item.2
            tr.append(total_money_sold)  ## item.3
            tr.append(total_discounts)  ## item.4
            tr.append(total_required)  ## item.5
            profit = round( total_money_sold - total_money_buy , 2)

            tr.append(profit) ## item.6

            transactions.append(tr)

            total_buy += total_money_buy
            total_sell +=  total_money_sold




    ###sort data depending on total profit
    transactions = sorted(transactions, key=lambda x:x[6], reverse = True)

    ## get all customers bills just for additional discounts
    cutomers_bills = Customer_Bill.objects.filter(date__date__gte = from_date ,date__date__lte = to_date, bill_type = 0)
    extra_discounts = round(sum(cb.discount for cb in cutomers_bills)  , 1)
    total_discounts_with_extra = total_discounts_all + extra_discounts

    total_profit = total_sell - total_buy - total_discounts_with_extra
    total_required_all = total_sell -  total_discounts_with_extra
    totals=[round(total_buy,2), round(total_sell,2), round(total_profit,2), total_discounts_all, total_required_all, extra_discounts , total_discounts_with_extra ]
    context = {
        'transactions':transactions,
        'totals':totals,
        # 'today_accumulator':today_accumulator,
        'mtc':Month_Total_Calculation.objects.last(),
    }
    return render(request, 'content/daily_transaction.html', context)
