from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Sandwich, DaySandwich, Product, Day_Payment_Line, Acumulate_payment, Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings,Total_Point_Product,Month_Total_Calculation
from .models import Point_Product_Store_Restore, Customer, Customer_Bill, Customer_Payment

from django.utils import timezone
from django.db.models import Sum,Q


@login_required
def points(request):
    points = Point.objects.all()
    points_data = []
    total_buy_points = 0.0
    total_sell_points = 0.0
    for point in points:
        tpps = Total_Point_Product.objects.filter(Point = point)
        total_cost_sell = 0
        total_cost_buy = 0
        p_d = []
        if tpps != None:
            total_cost_sell += round(sum(ttp.total_cost_sell for ttp in tpps) ,2)
            total_cost_buy += round(sum(ttp.total_cost for ttp in tpps) , 2)

        p_d.append(point)
        p_d.append( round(total_cost_sell, 2))
        p_d.append( round(total_cost_buy, 2))
        points_data.append(p_d)
        total_buy_points +=total_cost_buy
        total_sell_points +=total_cost_sell
    mtc = Month_Total_Calculation.objects.last()
    mtc.total_products_money_points = total_buy_points
    mtc.save()
    context = {
        'points':points_data,
        'total_buy_points':total_buy_points,
        'total_sell_points':total_sell_points,
    }
    return render(request, 'content/points.html',context)

@login_required
def point_page(request, point_id):
    from_date = to_date =  timezone.now().date()
    if request.method == "POST":
        from_date = request.POST['from_date']
        to_date = request.POST['to_date']
    date = timezone.now().date()
    point = Point.objects.get(id = point_id)
    today_date = timezone.now().date()

    bills = Point_Product_Sellings.objects.filter(Point = point,taken_status = 1 , date__date = today_date , line_type = 0)
    total_bills = 0.0
    if bills != None:
        total_bills =  round( sum((bill.required_amount)  for bill in bills) , 1)


    restored_bills = Point_Product_Sellings.objects.filter(Point = point,taken_status = 1 , date__date = today_date , line_type = 1)
    restored_total_bills = 0.0
    if restored_bills != None:
        restored_total_bills_sell =  round( sum((bill.restored_amount_cost_ad)  for bill in bills) , 1)
        restored_total_bills_buy =  round( sum((bill.restored_amount_cost_buy)  for bill in bills) , 1)

    ## withdrawing goods on this day
    today_point_products = Point_Product.objects.filter(date__date__gte = from_date,date__date__lte = to_date, Point = point).order_by('-date')
    today_dept = 0
    if today_point_products != None:
        today_dept = round(sum(tpp.money_quantity  for tpp in today_point_products) , 1)

    # all_products = Total_Point_Product.objects.filter( ~Q(total_product_quantity = 0)).filter(Point = point)
    all_products = Total_Point_Product.objects.filter(Point = point)
    all_products_count =len( all_products )
    total_dept = 0
    if all_products != None:
        total_dept = round(sum(p.total_cost for p in all_products) , 1)
    # for p in all_products:
    #     total_dept += p.total_cost

    ## current_manager date
    today_date =  timezone.now().date()
    user = Current_manager.objects.filter(user = request.user).first()
    all_bills = Point_User_Payment.objects.filter(g_user = point,date__date__gte = user.start_date ,date__date__lte = user.end_date).order_by('-date')
    bills_amount = 0
    if all_bills != None:
        bills_amount  = round(sum(p.amount for p in all_bills) , 1)
    context = {

        'bills':bills,
        'restored_bills':restored_bills,

        'total_sellings':total_bills,
        'restored_total_bills_sell':restored_total_bills_sell,
        'restored_total_bills_buy':restored_total_bills_buy,

        'point':point,
        'today_point_products':today_point_products,
        'today_dept':today_dept,
        'all_products':all_products,
        'all_products_count':all_products_count,
        'total_dept':total_dept,
        'all_bills':all_bills,
        'bills_amount':bills_amount,

    }
    return render(request, 'content/point_page.html',context)


@login_required
def point_total_product(request, tpp):
    tpp = Total_Point_Product.objects.get(id = tpp)

    context = {
        'tpp':tpp,
    }
    return render(request, 'content/point_total_product.html', context = context)


@login_required
def point_trader_page(request, point_trader_id):

    return render(request, 'content/point_trader_page.html')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_new_point_bill(request, product_id):
    failed = success = 0
    new_quantity = new_quantity_packet = last_quantity = last_quantity_packet = 0
    today_date = timezone.now().date()
    if request.method == "POST":
        # date = request.POST['date']
        date = timezone.now().date()
        product = Product.objects.get(id = int(request.POST['product_id']))
        point = Point.objects.get(id = int(request.POST['point_id']))
        if 'new_quantity' in request.POST:
            quantity = int(request.POST['new_quantity'])
            quantity_packet = int(request.POST['new_quantity_packet'])
        else :
            quantity = quantity_packet = 0
        if 'last_quantity' in request.POST:
            last_quantity_packet = int(request.POST['last_quantity_packet'])
            last_quantity = int(request.POST['last_quantity'])
        else :
            last_quantity_packet  = last_quantity =0
        # total_required_quantity = quantity + (quantity_packet * product.quantity_per_packet) +\
        #                          last_quantity + (quantity_packet * product.quantity_per_packet)

        if check_validation(quantity,quantity_packet,last_quantity,last_quantity_packet ,product,point):
            success = 1
        else:
            failed = 1


    product = Product.objects.get(id = product_id)
    points = Point.objects.all()
    old_p =  product.last_quantity +  product.last_quantity_packet
    new_p =  product.quantity +  product.quantity_packet
    context = {
        'failed':failed,
        'success':success,
        'product':product,
        'points':points,
        'old':old_p,
        'new':new_p,
    }
    return render(request, 'content/add_new_point_bill.html', context)

## check if product pass validation process
def check_validation(nq, nqp, lq, lqp, p, point):
    phase_1 = phase_2 = phase_3= 0
    ## map store product to point product
    old_p_old_tpp = old_p_new_tpp = new_p_new_tpp = 0
    ## take mod for nq and lq then update both nqp and lqp
    if p.quantity_per_packet:
        q,nq = divmod(nq , p.quantity_per_packet)
        nqp += q
    ## i.e this is not a new product
    if  p.last_quantity_per_packet :
        q,lq = divmod(lq , p.last_quantity_per_packet)
        lqp += q

    if p.quantity < nq and p.quantity_packet > nqp :
        p.quantity += p.quantity_per_packet
        p.quantity_packet -= 1
        p.save()
    if p.last_quantity < lq and p.last_quantity_packet > lqp:
        p.last_quantity += p.last_quantity_per_packet
        p.last_quantity_packet -= 1
        p.save()

    ## phase  1 i have enough quantity
    if p.quantity >= nq   and p.quantity_packet >= nqp and p.last_quantity >= lq and p.last_quantity_packet >=lqp:
        phase_1 = 1
    else :
        return False

    if phase_1 ==1 and point.name == "manager"  :
        bill_total_money = ((nq + (nqp * p.quantity_per_packet)) *  p.unit_buy_price )\
                            +((lq + (lqp * p.last_quantity_per_packet)) *  p.last_unit_buy_price)

        bill_total_money = round(bill_total_money, 2)
        total_q = (nq + (nqp * p.quantity_per_packet)) +(lq + (lqp * p.last_quantity_per_packet))
        mtc = Month_Total_Calculation.objects.last()

        # if point.name == "manager" :
        description = str(total_q) + " قطعة " + str(p)
        ## create new withdrwaing
        withdrawings.objects.create(money_amount = bill_total_money, day = timezone.now(), descreption = description , status = 1)
        mtc.total_withdrawings += bill_total_money

        # else :
        #     Point_Product.objects.create(money_quantity = bill_total_money ,date = timezone.now(), product = p,
        #         Point = point)

        mtc.total_products_money -= bill_total_money
        mtc.save()
        ## update store product

        p.quantity -=nq
        p.quantity_packet -=nqp
        p.last_quantity -=lq
        p.last_quantity_packet -=lqp

        # p.total_quantity -=total_q
        p.save()
        return True

    ## check phase 2
    ppt =Total_Point_Product.objects.filter(product = p , Point=point).first()
    if ppt == None:
        Total_Point_Product.objects.create(Point = point, product = p, quantity_per_packet = p.quantity_per_packet ,
                packet_price = p.packet_price, unit_buy_price = p.unit_buy_price, last_quantity_per_packet = p.last_quantity_per_packet,
                last_packet_price = p.last_packet_price, last_unit_buy_price = p.last_unit_buy_price)

    ppt =Total_Point_Product.objects.get(product = p , Point=point)

    ## if i have amount old come from store to point
    if ppt != None and (lq > 0 or lqp > 0) :
        print("ppt != None")
        if(ppt.last_quantity_per_packet == p.last_quantity_per_packet ) and (ppt.last_packet_price == p.last_packet_price ):
            phase_2 = 1
            old_p_old_tpp = 1
        ## move tpp new data to tpp old data
        # elif ppt.last_quantity ==0 and ppt.last_quantity_packet ==0:
        elif ppt.old_amount == 0 and ppt.new_amount == 0 :
            ppt.last_quantity_per_packet =  p.last_quantity_per_packet
            ppt.last_packet_price = p.last_packet_price
            ppt.last_unit_buy_price = p.last_unit_buy_price
            ppt.last_quantity = 0
            ppt.last_quantity_packet = 0
            ppt.save()
            phase_2 = 1
            old_p_old_tpp = 1
        ## move tpp new data to tpp old data
        # elif ppt.last_quantity ==0 and ppt.last_quantity_packet ==0:
        elif ppt.old_amount == 0  and ppt.new_amount > 0 :
            ppt.last_quantity_per_packet =  p.last_quantity_per_packet
            ppt.last_packet_price = p.last_packet_price
            ppt.last_unit_buy_price = p.last_unit_buy_price
            ppt.last_quantity = 0
            ppt.last_quantity_packet = 0
            ppt.save()
            phase_2 = 1
            old_p_old_tpp = 1

        ## special case old amount > 0 but we sold all new amount
        elif ppt.old_amount > 0 and ppt.new_amount == 0:
            ## make old product == new ppt
            # print("condiotn old != 0 and new =0 hold")
            ppt.quantity_per_packet =  p.last_quantity_per_packet
            ppt.packet_price = p.last_packet_price
            ppt.unit_buy_price = p.last_unit_buy_price
            ppt.quantity = 0
            ppt.quantity_packet = 0
            ppt.save()
            old_p_new_tpp = 1
            phase_2 = 1
        else:
            phase_2 = 0

    else:
        phase_2 = 1
    ## chek pahse 3
    ## if i have amount new  come from store to point
    if ppt != None and (nq > 0 or nqp > 0) :
        print("ppt != None 2")
        if(ppt.quantity_per_packet == p.quantity_per_packet ) and (ppt.packet_price == p.packet_price ):
            phase_3 = 1
            new_p_new_tpp = 1

        ## case 2 new store do not map to new point
        ## check new point to see if zero
        ## check if no old store product is coming
        elif lq == 0 and lqp == 0:
            ## move tpp new data to tpp old data
            # elif ppt.last_quantity ==0 and ppt.last_quantity_packet ==0:
            if ppt.old_amount == 0 and ppt.new_amount == 0 :
                ## make new product == new ppt
                new_store_to_new_point_without_Affecting_Old_Point(ppt, p)
                phase_3 = 1
                new_p_new_tpp = 1
            ## move tpp new data to tpp old data
            # elif ppt.last_quantity ==0 and ppt.last_quantity_packet ==0:
            elif ppt.old_amount > 0  and ppt.new_amount == 0 :
                new_store_to_new_point_without_Affecting_Old_Point(ppt, p)
                phase_3 = 1
                new_p_new_tpp = 1

            ## special case old amount > 0 but we sold all new amount
            elif ppt.old_amount == 0 and ppt.new_amount > 0:
                update_total_point_product_prices_new_to_new(ppt, p, 0)
                phase_3 = 1
                new_p_new_tpp = 1
            else:
                phase_3 = 0



        elif lq > 0 or lqp > 0 :
            if old_p_old_tpp == 1:
                if ppt.new_amount == 0 :
                    new_store_to_new_point_without_Affecting_Old_Point(ppt, p)
                    phase_3 = 1
                    new_p_new_tpp = 1
                else:
                    phase_3 = 0


            elif old_p_new_tpp == 1:
                phase_3 = 0
        #     ## case 2.a if i have any old prodcut come from store see if it maps to old point product , else failed
        #     if lq > 0 or lqp > 0 :
        #         if old_p_new_tpp == 1:
        #             ## failed
        #             phase_3 = 0
        #     ## i do not have any old store prodcut to move it to point
        #     else:
        #
        #     ## do not add both old and new
        #     phase_3= update_total_point_product_prices_new_to_new(ppt,p, 0)
        #     new_p_new_tpp = 1
        # ## move tpp new data to tpp old data
        # # elif ppt.last_quantity ==0 and old_p_new_ttp ==0 ie old store product do not map to new point product :
        # elif ppt.old_amount == 0 and old_p_new_tpp == 0 :
        #     ## do not add both old and new
        #     phase_3= update_total_point_product_prices_new_to_new(ppt,p, 0)
        #     new_p_new_tpp = 1
        #
        #
        #
        # ## special case old tpp == new tpp
        # ## add both old and new to old and update new
        # elif (ppt.quantity_per_packet == ppt.last_quantity_per_packet ) and (ppt.packet_price == ppt.last_packet_price ):
        #     ## add both old and new
        #     phase_3= update_total_point_product_prices_new_to_new(ppt, p, 1)
        #     new_p_new_tpp = 1
        #
        # else:
        #
        #     phase_3 = 0
    else :

        phase_3 = 1

    if (phase_1  and phase_2 and phase_3) :
        print("phase_1 and phase_2 and phase_3 hold ")
        create_new_bill(nq,nqp,lq,lqp,p,point, old_p_old_tpp, old_p_new_tpp, new_p_new_tpp)
    print("phase_1 %d, phase_2 %d, phase_3 %d,"%(phase_1, phase_2 , phase_3))
    return (phase_1 and phase_2 and phase_3)

def new_store_to_new_point_without_Affecting_Old_Point(ppt, p):
    ppt.quantity_per_packet =  p.quantity_per_packet
    ppt.packet_price = p.packet_price
    ppt.unit_buy_price = p.unit_buy_price
    ppt.quantity = 0
    ppt.quantity_packet = 0
    ppt.save()
def update_total_point_product_prices_old_to_old(ppt,p):

    ppt.last_quantity_per_packet = ppt.quantity_per_packet
    ppt.last_packet_price = ppt.packet_price
    ppt.last_unit_buy_price = ppt.unit_buy_price
    ## amounts
    ppt.last_quantity = ppt.quantity
    ppt.last_quantity_packet = ppt.quantity_packet
    ppt.save()

    ## make old product == new ppt
    ppt.quantity_per_packet =  p.last_quantity_per_packet
    ppt.packet_price = p.last_packet_price
    ppt.unit_buy_price = p.last_unit_buy_price
    ppt.quantity = 0
    ppt.quantity_packet = 0
    ppt.save()

    return 1 ## success

def update_total_point_product_prices_new_to_new(ppt, p,  add_new_to_old):
    if add_new_to_old == 1:

        ## amounts
        ppt.last_quantity += ppt.quantity
        ppt.last_quantity_packet += ppt.quantity_packet
        ppt.save()

    else :
        ppt.last_quantity_per_packet = ppt.quantity_per_packet
        ppt.last_packet_price = ppt.packet_price
        ppt.last_unit_buy_price = ppt.unit_buy_price
        ## amounts
        ppt.last_quantity = ppt.quantity
        ppt.last_quantity_packet = ppt.quantity_packet
        ppt.save()

     ## make new product == new ppt
    ppt.quantity_per_packet =  p.quantity_per_packet
    ppt.packet_price = p.packet_price
    ppt.unit_buy_price = p.unit_buy_price
    ppt.quantity = 0
    ppt.quantity_packet = 0
    ppt.save()

    return 1 ## success

## crete new pill and update all
def create_new_bill(nq,nqp,lq,lqp,p,point, opto, optn, nptn):
    date = timezone.now()

    bill_total_money = ((nq + (nqp * p.quantity_per_packet)) *  p.unit_buy_price )\
                        +((lq + (lqp * p.last_quantity_per_packet)) *  p.last_unit_buy_price)

    bill_total_money = round(bill_total_money , 2)
    if bill_total_money > 0 :
        tpp =Total_Point_Product.objects.get(product = p , Point=point)
        Point_Product.objects.create(money_quantity = bill_total_money ,date = timezone.now(),quantity_new = nq,
            quantity_packet_new = nqp, quantity_old = lq , quantity_packet_old = lqp , product = p,
            Point = point ,quantity_per_packet = tpp.quantity_per_packet ,unit_buy_price = tpp.unit_buy_price,
            last_quantity_per_packet = tpp.last_quantity_per_packet, last_unit_buy_price = tpp.last_unit_buy_price )

        ## update Total_Point_Product
        if tpp == None:
            print("Tpp == None")

            # tpp = Total_Point_Product.objects.get(product = p , Point=point)
            return 0 ## failure
            print("new point product 1")


        print("new point product 2")
        tpp.total_product_quantity += (nq + (nqp * p.quantity_per_packet)) +(lq + (lqp * p.last_quantity_per_packet))

        if opto:
            tpp.last_quantity += lq
            tpp.last_quantity_packet += lqp
        if optn:
            tpp.quantity += lq
            tpp.quantity_packet += lqp
        if nptn:
            tpp.quantity += nq
            tpp.quantity_packet += nqp
        if opto == 0 and optn ==0 and  nptn == 0:
            tpp.last_quantity += lq
            tpp.last_quantity_packet += lqp

            tpp.quantity += nq
            tpp.quantity_packet += nqp


        tpp.save()
        tpp.normailze_product()

        ## update mtc data
        mtc = Month_Total_Calculation.objects.last()
        mtc.total_products_money -= bill_total_money
        mtc.total_products_money_points += bill_total_money
        mtc.save()
        ##update point total products raw cost
        point.total_money_raw +=bill_total_money
        point.save()

        ## update store product
        p.subtract_from_product(lq, lqp, nq, nqp)
    else:
        return False
    return True


## update point payments
@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_new_point_sellings(request, point_id):
    failed = success = 0
    point = Point.objects.get(id = point_id)
    quantity = quantity_packet = last_quantity = last_quantity_packet = 0
    today_date = timezone.now().date()
    discount_per_unit = 0.0
    selected_customer = None
    if request.method == "POST":
        print(request.POST)
        # date = request.POST['date']
        date = timezone.now().date()
        product_id = request.POST['product_id']
        product = Product.objects.get(id = int(request.POST['product_id']))
        # point = Point.objects.get(id = int(request.POST['point_id']))
        if ('new_quantity'+str(product_id)) in  request.POST and request.POST['new_quantity'+str(product_id)]!=''   :
            quantity = int(request.POST['new_quantity'+str(product_id)])

        if  ('new_quantity_packet'+str(product_id)) in  request.POST and request.POST['new_quantity_packet'+str(product_id)]!='' :
            quantity_packet = int(request.POST['new_quantity_packet'+str(product_id)])

        if ('last_quantity_packet'+str(product_id)) in  request.POST and request.POST['last_quantity_packet'+str(product_id)]!='' :
            last_quantity_packet = int(request.POST['last_quantity_packet'+str(product_id)])

        if ('last_quantity'+str(product_id)) in  request.POST and request.POST['last_quantity'+str(product_id)]!='' :
            last_quantity = int(request.POST['last_quantity'+str(product_id)])

        if  request.POST["discount_per_unit"] != "" :
            discount_per_unit = float(request.POST['discount_per_unit'])

        cust_id =  int(request.POST['customer_id'])
        selected_customer = Customer.objects.get(id = int(request.POST['customer_id']))

        print(" quantity :%d quantity_packet: %d  last_quantity:%d last_quantity_packet : %d"%(quantity,quantity_packet,last_quantity,last_quantity_packet ))
        ttp = Total_Point_Product.objects.get(Point = point, product= product)

        if check_validation_sell(request, quantity,quantity_packet,last_quantity,last_quantity_packet ,ttp,point,product, discount_per_unit, cust_id):
            success = 1
        else:
            failed = 1



    product = Product.objects.all()
    ## get all point products
    total_point_products = []
    products=[]
    for p in product:
        ttps = Total_Point_Product.objects.filter(product = p , Point = point).first()
        if ttps != None:
            total_point_products.append(ttps)
            products.append(ttps.product)
    customers = Customer.objects.all()
    context = {
        'point':point,
        'failed':failed,
        'success':success,
        'products':products,
        'total_point_products':total_point_products,
        'customers':customers,
        'selected_customer':selected_customer,



    }
    return render(request, 'content/add_new_point_sellings.html', context)

## check if product pass validation process
def check_validation_sell(request , nq, nqp, lq, lqp, p, point,product, discount_per_unit, cust_id):
    phase_1 = phase_2 = phase_3= 0
    ## take mod for nq and lq then update both nqp and lqp
    if p.quantity_per_packet:
        q,nq = divmod(nq , p.quantity_per_packet)
        nqp += q
        print('q %d , nq %d , p.quantity %d, q.quantity_packet%d' %(q,nq,p.quantity,p.quantity_packet))
    ## i.e this is not a new product
    if  p.last_quantity_per_packet :
        q,lq = divmod(lq , p.last_quantity_per_packet)
        lqp += q
        print('2')

    if p.quantity < nq and p.quantity_packet > nqp :
        p.quantity += p.quantity_per_packet
        p.quantity_packet -= 1
        p.save()
        print('3')
    if p.last_quantity < lq and p.last_quantity_packet > lqp:
        p.last_quantity += p.last_quantity_per_packet
        p.last_quantity_packet -= 1
        p.save()
        print('4')
    if p.quantity >= nq   and p.quantity_packet >= nqp and p.last_quantity >= lq and p.last_quantity_packet >=lqp:
        phase_1 = 1
        print('4')
    else :
        return False

    if discount_per_unit > product.unit_sell_price:
        return False
    if  phase_1:
         create_new_bill_sell(request, nq,nqp,lq,lqp,p,point,product, discount_per_unit, cust_id)
        # create_new_bill(nq,nqp,lq,lqp,p,point)

    return True
## crete new pill and update all
def create_new_bill_sell(request, nq,nqp,lq,lqp,tpp,point,p, discount_per_unit, cust_id):
    date = timezone.now().date()
    bill_total_money_sell = ((nq + (nqp * tpp.quantity_per_packet)) *  p.unit_sell_price )\
                        +((lq + (lqp * tpp.last_quantity_per_packet)) *  p.unit_sell_price)

    bill_total_money_sell = round(bill_total_money_sell , 2)


    bill_total_money_buy = ((nq + (nqp * tpp.quantity_per_packet)) *  tpp.unit_buy_price )\
                        +((lq + (lqp * tpp.last_quantity_per_packet)) *  tpp.last_unit_buy_price)

    bill_total_money_buy = round(bill_total_money_buy, 2)
    ## create new selling bill
    if point.name == "stuff":
        bill_total_money_sell = bill_total_money_buy

    total_quantity_new = (nq + (nqp * tpp.quantity_per_packet))
    total_quantity_old = (lq + (lqp * tpp.last_quantity_per_packet))
    ## get last un paid bill for this customer , =>  if null create a new one
    customer = Customer.objects.get(id = cust_id)
    cust_cur_bill = Customer_Bill.objects.filter(given_status = 0, customer = customer,bill_type = 0 ).last()
    if cust_cur_bill == None:
        ## create new one
        cur_m = Current_manager.objects.get(user = request.user)
        Customer_Bill.objects.create(customer = customer, manager = cur_m)
        cust_cur_bill =  Customer_Bill.objects.filter(given_status = 0, customer = customer).last()

    Point_Product_Sellings.objects.create(money_quantity_sell = bill_total_money_sell ,date = timezone.now(),quantity_new = nq,
                                            quantity_packet_new = nqp, quantity_old = lq , quantity_packet_old = lqp , product = p,
                                            Point = point, money_quantity_buy = bill_total_money_buy, total_quantity_new = total_quantity_new , total_quantity_old = total_quantity_old,
                                            unit_sell_price = p.unit_sell_price ,unit_buy_price_new = tpp.unit_buy_price ,unit_buy_price_old =tpp.last_unit_buy_price ,
                                            discount_per_unit = discount_per_unit , bill = cust_cur_bill)

    ## update customer total money
    total_sold_quantity = ( total_quantity_new + total_quantity_old )
    required_amount = round( (bill_total_money_sell - ( total_sold_quantity * discount_per_unit) ), 2)

    customer.total_money +=  required_amount
    # customer.save()
    customer.normalize()


    tpp.total_product_quantity -= total_sold_quantity
    tpp.quantity -= nq
    tpp.quantity_packet -= nqp

    tpp.last_quantity -= lq
    tpp.last_quantity_packet -= lqp

    tpp.save()
    tpp.normailze_product()
    # when getting point total bill add them to safe
    # # update mtc data
    # mtc = Month_Total_Calculation.objects.last()
    # mtc.total_products_money_points -= bill_total_money_buy
    # mtc.total_profit += (bill_total_money_sell- bill_total_money_buy)
    # mtc.safe_current_money += bill_total_money_sell
    # mtc.save()
    # ##update point total products raw cost
    # point.total_money_raw -=bill_total_money_buy
    # point.save()
    #
    # ## update store product
    # p.quantity -=nq
    # p.quantity_packet -=nqp
    # p.last_quantity -=lq
    # p.last_quantity_packet -=lqp
    # p.save()

    return True

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_new_point_payments(request,point_id):
    failed = success = 0
    point = Point.objects.get(id = point_id)
    today_date = timezone.now()
    ## get all bills give status = 0 and relate to this point
    bills = Customer_Bill.objects.filter(point_product_sellings__Point = point,given_status = 0).distinct()

    if request.method == "POST":
        amount = float(request.POST['total_money'])
        customer = Customer.objects.get(id = int(request.POST['customer_id']))
        # amount_loop = amount
        if amount <= customer.remaining_money and amount >= 0 :
            bill = Customer_Bill.objects.get(id = int(request.POST['bill_id']) )
            ## update bill lines
            bill.all_lines.update(taken_status = 1)

            if bill.required_amount == amount  or (bill.required_amount - amount) <= .01:
                bill.paid_status = 1

            bill.given_amount += amount
            ##3. update all bills taken status = 1
            bill.given_status = 1
            bill.save()


            ## update customer given - remaining_money
            ## create customer payment
            manager = Current_manager.objects.get(user = request.user)
            Customer_Payment.objects.create(g_user = customer, t_user=manager, date= timezone.now(), amount = amount
                            ,discount = bill.main_discount, previos_amount = customer.remaining_money + bill.main_discount , current_amount = customer.remaining_money - amount  , payment_type = 0)

            customer.given_money += amount
            customer.normalize()


            m_safe = Safe_Month.objects.last()
            mtc = Month_Total_Calculation.objects.last()


            ## total bill cost buying
            total_mony_quantity_buy = round(sum(line.money_quantity_buy for line in bill.all_lines), 2)
            total = round(sum(line.required_amount for line in bill.all_lines), 2)
            ## m_safe
            m_safe.money +=amount

            mtc.total_products_money_points -=total_mony_quantity_buy
            mtc.safe_current_money +=amount
            mtc.total_profit += (total - total_mony_quantity_buy)

            point.total_money_raw -=total_mony_quantity_buy
            point.given_money +=amount
            ## create new bill given
            Point_User_Payment.objects.create(g_user = point, t_user=manager, date= today_date, amount = amount )
            ## 2. safe_date
            notes = " مبيعات نقطة " + point.name
            Safe_data.objects.create(day = today_date, money_amount = amount, given_person =manager, notes=notes , safe_line_status = 6 )


            mtc.save()
            point.save()
            m_safe.save()
            success = 1

        else :
            failed =1


    managers = Current_manager.objects.filter(end_date__gte = today_date.date() )

    context = {
        'failed':failed,
        'success':success,
        'managers':managers,
        'point':point,

        'bills':bills,
        # 'total':total,
    }
    return render(request, 'content/add_new_point_payments.html',context)


@login_required
def add_new_point_seller(request):

    return render(request, 'content/add_new_point_seller.html')



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def restore_point_bill_sell(request, bill_id):
    bill = Point_Product_Sellings.objects.get(id =bill_id )
    point = bill.Point
    cust_bill = Customer_Bill.objects.filter(point_product_sellings__Point = point,given_status = 0).first()
    customer = cust_bill.customer

    ###
    customer.total_money -= bill.required_amount
    # customer.save()
    customer.normalize()

    ttp = Total_Point_Product.objects.get(Point = point, product = bill.product)
    ## updte ttp with bill product data
    ttp.total_product_quantity += ( (bill.quantity_new + (bill.quantity_packet_new * ttp.quantity_per_packet)) +\
                                    (bill.quantity_old + (bill.quantity_packet_old * ttp.last_quantity_per_packet)) )
    ttp.quantity += bill.quantity_new
    ttp.quantity_packet += bill.quantity_packet_new
    ## normalize
    # if ttp.quantity_per_packet :
    #     quo,rem = divmod(ttp.quantity , ttp.quantity_per_packet )
    #     ttp.quantity = rem
    #     ttp.quantity_packet += quo


    ttp.last_quantity += bill.quantity_old
    ttp.last_quantity_packet += bill.quantity_packet_old
    ## normalize
    # if ttp.last_quantity_per_packet :
    #     quo,rem = divmod(ttp.last_quantity , ttp.last_quantity_per_packet )
    #     ttp.last_quantity = rem
    #     ttp.last_quantity_per_packet += quo


    ttp.save()
    ttp.normailze_product()
    ## remove this wrong bill
    bill.delete()
    return redirect('content:add_new_point_payments',point.id)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def restore_point_product_store(request , point_id):
    point = Point.objects.get(id = point_id)
    success = failed = old_quantity = new_quantity =  0
    point = Point.objects.get(id = point_id)

    if request.method == "POST":
        if 'old_quantity' in request.POST:
            old_quantity = int(request.POST['old_quantity'])
        if 'new_quantity' in request.POST:
            new_quantity = int(request.POST['new_quantity'])
        product = Product.objects.get(id = int(request.POST['product_id']))
        if( old_quantity or new_quantity)  :
            ## check validation restore
            if check_restore_validation(old_quantity , new_quantity , product,point ):
                success = 1
            else :
                failed = 1

        else:
            failed = 1



    product = Product.objects.all()
    ## get all point products
    total_point_products = []
    products=[]
    for p in product:
        ttps = Total_Point_Product.objects.filter(product = p , Point = point).first()
        if ttps != None:
            total_point_products.append(ttps)
            products.append(ttps.product)
    context = {
        'point':point,
        'failed':failed,
        'success':success,
        'products':products,
        'total_point_products':total_point_products,


    }
    return render(request, 'content/restore_point_product_store.html', context)





## check if product pass validation process
def check_restore_validation(old_q , new_q, product, point):
    phase_1 = phase_2 = phase_3= 0
    ## mapping betmeen store and point product object
    new_tpp_new_p =  new_tpp_old_p = old_tpp_old_p = 0
    ## take mod for nq and lq then update both nqp and lqp
    tpp = Total_Point_Product.objects.get(Point = point, product = product)
    ### 4 checks   -> 1. check old_q and new_q  less than ot equal to ttp amounts
    if old_q > tpp.old_amount or new_q > tpp.new_amount:
        return False
    else :
        phase_1 = 1

    print("pass phase 1")
    ### normailze old_q and new_q
    quo_new =  rem_new = 0
    if tpp.quantity_per_packet:
        quo_new, rem_new = divmod(new_q , tpp.quantity_per_packet)

    ## i.e this is not a new product
    quo_old =  rem_old = 0
    if  tpp.last_quantity_per_packet :
        quo_old, rem_old = divmod(old_q , tpp.last_quantity_per_packet)

    ## here were manager restore if any

    ## pahse_2
    ## if new_q != 0
    #2 cases   tpp.new == product.new    or tpp.new == product.old

    if new_q > 0:
        ## new tpp maps to new product
        if tpp.quantity_per_packet == product.quantity_per_packet and tpp.packet_price == product.packet_price:
            phase_2 = 1
            new_tpp_new_p = 1
        ## new tpp maps to old product
        elif tpp.quantity_per_packet == product.last_quantity_per_packet and tpp.packet_price == product.last_packet_price:
            phase_2 = 1
            new_tpp_old_p = 1
        ## else they do not amp each other completely :
        else:
            return False
    else:
        phase_2 = 1
    print("pass phase 2")
    ## phase 3
    ## 1. case  ->  tpp.old == product.old
    if old_q > 0:
        ## old tpp maps to old product
        if tpp.last_quantity_per_packet == product.last_quantity_per_packet and tpp.last_packet_price == product.last_packet_price:
            phase_3 = 1
            old_tpp_old_p = 1
        ## else they do not map to each other completely :
        else:
            return False

    else :
        phase_3 = 1


    print("pass phase 3")
    if (phase_1 and phase_2 and phase_3) :
        create_new_restore_bill(quo_old, rem_old ,quo_new, rem_new, new_tpp_new_p, new_tpp_old_p, old_tpp_old_p ,point, product, tpp)

    return (phase_1 and phase_2 and phase_3)

## crete new pill and update all
def create_new_restore_bill(packet_old, quantity_old, packet_new, quantity_new, ntn, nto, oto , point, product ,tpp):
    print("pass phase 4")
    date = timezone.now()

    bill_total_money = ((quantity_new + (packet_new * tpp.quantity_per_packet)) *  tpp.unit_buy_price )\
                        +((quantity_old + (packet_old * tpp.last_quantity_per_packet)) *  tpp.last_unit_buy_price)

    bill_total_money = round(bill_total_money , 2)
    if bill_total_money > 0 :
        print("pass phase 5")
        Point_Product_Store_Restore.objects.create(money_quantity = bill_total_money ,date = timezone.now(),quantity_new = quantity_new,
            quantity_packet_new = packet_new, quantity_old = quantity_old , quantity_packet_old = packet_old , product = product,
            Point = point , return_status = 1)



        tpp.total_product_quantity -= ( (quantity_new +(packet_new * tpp.quantity_per_packet)) +(quantity_old + (packet_old * tpp.last_quantity_per_packet) ) )
        # if quantity_new > tpp.quantity :
        #     tpp.quantity += tpp.quantity_per_packet
        #     tpp.quantity_packet -= 1
        #
        # tpp.quantity -= quantity_new
        # tpp.quantity_packet -= packet_new
        #
        #
        #
        #
        # if quantity_old > tpp.last_quantity :
        #     tpp.last_quantity += tpp.last_quantity_per_packet
        #     tpp.last_quantity_packet -= 1
        #
        # tpp.last_quantity -= quantity_old
        # tpp.last_quantity_packet -= packet_old
        #
        # tpp.last_update = date
        # tpp.save()
        ## this line replace all commented lines
        tpp.subtract_from_product(quantity_old, packet_old, quantity_new, packet_new)

        ## update store product
        if ntn:
            product.quantity += quantity_new
            product.quantity_packet += packet_new
        if nto:
             product.last_quantity += quantity_new
             product.last_quantity_packet += packet_new
        if oto :
             product.last_quantity += quantity_old
             product.last_quantity_packet += packet_old
        product.save()
        ## normalize product
        product.normailze_product()
        # if product.quantity_per_packet :
        #     quo , rem = divmod(product.quantity , product.quantity_per_packet)
        #     product.quantity = rem
        #     product.quantity_packet += quo
        #
        # if product.last_quantity_per_packet :
        #     quo , rem = divmod(product.last_quantity , product.last_quantity_per_packet)
        #     product.last_quantity = rem
        #     product.last_quantity_packet += quo
        #
        # product.save()
        ## update mtc data
        mtc = Month_Total_Calculation.objects.last()
        mtc.total_products_money += bill_total_money
        mtc.total_products_money_points -= bill_total_money
        mtc.save()
        ##update point total products raw cost
        point.total_money_raw -=bill_total_money
        point.save()
        print("pass phase 7")

    else:
        return False
    return True



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def point_to_point_product(request , point_id):
    point = Point.objects.get(id = point_id)
    success = failed = old_quantity = new_quantity =  0

    if request.method == "POST":
        if 'old_quantity' in request.POST:
            old_quantity = int(request.POST['old_quantity'])
        if 'new_quantity' in request.POST:
            new_quantity = int(request.POST['new_quantity'])
        product = Product.objects.get(id = int(request.POST['product_id']))
        to_point = Point.objects.get(id = int(request.POST['to_point']))

        if( old_quantity or new_quantity)  :
            ## check validation restore
            if check_point_to_point_validation(old_quantity , new_quantity , product, point , to_point ):
                success = 1
            else :
                failed = 1

        else:
            failed = 1



    product = Product.objects.all()
    ## get all point products
    total_point_products = []
    products=[]
    for p in product:
        ttps = Total_Point_Product.objects.filter(product = p , Point = point).first()
        if ttps != None:
            total_point_products.append(ttps)
            products.append(ttps.product)
    points = Point.objects.all().exclude(id = point.id).exclude(name__in = ['manager' , 'stuff'])
    context = {
        'point':point,
        'points':points,
        'failed':failed,
        'success':success,
        'products':products,
        'total_point_products':total_point_products,


    }
    return render(request, 'content/point_to_point_product.html', context)






## check if product pass validation process
def check_point_to_point_validation(old_q , new_q, product, point, to_point):
    phase_1 = phase_2 = phase_3= 0
    ## mapping betmeen store and point product object
    new_tpp_new_p =  new_tpp_old_p = old_tpp_old_p = old_tpp_new_p =  0
    ## take mod for nq and lq then update both nqp and lqp
    tpp = Total_Point_Product.objects.get(Point = point, product = product)

    if old_q > tpp.old_amount or new_q > tpp.new_amount:
        return False
    else :
        phase_1 = 1

    print("pass phase 1")

    ttp_to_point = Total_Point_Product.objects.filter(Point = to_point, product = product).first()
    if ttp_to_point == None:
        Total_Point_Product.objects.create(Point = to_point , product = product ,quantity_per_packet =tpp.quantity_per_packet,
                packet_price = tpp.packet_price ,last_quantity_per_packet = tpp.last_quantity_per_packet, last_packet_price = tpp.last_packet_price,
                unit_buy_price = tpp.unit_buy_price ,    last_unit_buy_price = tpp.last_unit_buy_price       )
        ttp_to_point = Total_Point_Product.objects.get(Point = to_point, product = product)
    ### 4 checks   -> 1. check old_q and new_q  less than ot equal to ttp amounts

    if new_q > 0:
        ## new tpp maps to new product
        if tpp.quantity_per_packet == ttp_to_point.quantity_per_packet and tpp.packet_price == ttp_to_point.packet_price:
            phase_2 = 1
            new_tpp_new_p = 1
        ## new tpp maps to old product
        elif tpp.quantity_per_packet == ttp_to_point.last_quantity_per_packet and tpp.packet_price == ttp_to_point.last_packet_price:
            phase_2 = 1
            new_tpp_old_p = 1
        ## make new from point equ. to old to point  new -> old
        ## this a sepcail case in this case its better to always maps new from_point to new to_point and move new to point to old to point
        elif ttp_to_point.old_amount == 0:
            # swap_tpps(tpp,ttp_to_point , 2)
            # phase_2 = 1
            # new_tpp_old_p = 1
            update_total_point_product_prices_new_to_new(ttp_to_point, tpp , 0 )
            phase_2 = 1
            new_tpp_new_p = 1
        ## make new from point equ. to new to point  new -> new
        elif ttp_to_point.new_amount == 0:
            swap_tpps(tpp,ttp_to_point, 4 )
            phase_2 = 1
            new_tpp_new_p = 1

        ## else they do not amp each other completely :
        else:
            return False
    else:
        phase_2 = 1
    print("pass phase 2")
    ## phase 3
    ## 1. case  ->  tpp.old == product.old
    if old_q > 0:
        ## old tpp maps to old product
        if tpp.last_quantity_per_packet == ttp_to_point.last_quantity_per_packet and tpp.last_packet_price == ttp_to_point.last_packet_price:
            phase_3 = 1
            old_tpp_old_p = 1
            print("pass phase 3")
        ## old tpp maps to new  product
        elif tpp.last_quantity_per_packet == ttp_to_point.quantity_per_packet and tpp.last_packet_price == ttp_to_point.packet_price:
            phase_3 = 1
            old_tpp_new_p = 1
        ## make new from point equ. to old to point  new -> old
        elif ttp_to_point.old_amount == 0 and new_tpp_old_p == 0:
                swap_tpps(tpp,ttp_to_point , 1)
                phase_3 = 1
                old_tpp_old_p = 1
            ## make new from point equ. to new to point  new -> new
        elif ttp_to_point.new_amount == 0 and new_tpp_new_p == 0:
                swap_tpps(tpp, ttp_to_point, 3 )
                phase_3 = 1
                old_tpp_new_p = 1
        ## else they do not map to each other completely :
        else:
            return False

    else :
        phase_3 = 1


    print("pass phase 3")
    if (phase_1 and phase_2 and phase_3) :
        return create_new_point_to_point_bill(old_q, new_q ,product, point, to_point, new_tpp_new_p, new_tpp_old_p ,old_tpp_old_p ,old_tpp_new_p ,  ttp_to_point, tpp)

    return (phase_1 and phase_2 and phase_3)

def swap_tpps(from_tpp , to_tpp, case):
    ## case 1.  old to old
    ## case 2.  new to old
    ## case 3.  old to new
    ## case 4.  new to new
    if case == 1 or case == 2:
        if case == 1:
            to_tpp.last_quantity_per_packet = from_tpp.last_quantity_per_packet
            to_tpp.last_packet_price = from_tpp.last_packet_price
            to_tpp.last_unit_buy_price = from_tpp.last_unit_buy_price
        elif case == 2:
            to_tpp.last_quantity_per_packet = from_tpp.quantity_per_packet
            to_tpp.last_packet_price = from_tpp.packet_price
            to_tpp.last_unit_buy_price = from_tpp.unit_buy_price
        ## amounts
        to_tpp.last_quantity = 0
        to_tpp.last_quantity_packet =0
        to_tpp.save()

    elif case == 3 or case == 4:
        if case == 3:
            to_tpp.quantity_per_packet = from_tpp.last_quantity_per_packet
            to_tpp.packet_price = from_tpp.last_packet_price
            to_tpp.unit_buy_price = from_tpp.last_unit_buy_price
        elif case == 4:
            to_tpp.quantity_per_packet = from_tpp.quantity_per_packet
            to_tpp.packet_price = from_tpp.packet_price
            to_tpp.unit_buy_price = from_tpp.unit_buy_price
        ## amounts
        to_tpp.quantity = 0
        to_tpp.quantity_packet =0
        to_tpp.save()

## crete new pill and update all
def create_new_point_to_point_bill(old_q, new_q ,product, point, to_point, new_tpp_new_p, new_tpp_old_p ,old_tpp_old_p,old_tpp_new_p, ttp_to_point, tpp):
    print("pass phase 4")
    date = timezone.now()

    quantity_old , packet_old, quantity_new, packet_new  = normalize_product_v(tpp, old_q, new_q)
    ## just to subtract from old
    lq, lqp, nq, nqp = quantity_old , packet_old, quantity_new, packet_new

    bill_total_money = ((quantity_new + (packet_new * tpp.quantity_per_packet)) *  tpp.unit_buy_price )\
                        +((quantity_old + (packet_old * tpp.last_quantity_per_packet)) *  tpp.last_unit_buy_price)

    bill_total_money = round(bill_total_money , 2)
    notes = " بضاعة منقولة من نقطة " +point.name + " الى نقطة " + to_point.name


    ##if transefering both new and old quantiteis
    if new_q and old_q:
        ##it is ok pass
        print("pass phase 5")
        if new_tpp_old_p :
            quantity_old += quantity_new
            packet_old += packet_new
            quantity_new = packet_new = 0

        elif old_tpp_new_p:
            quantity_new += quantity_old
            packet_new += packet_old
            quantity_old = packet_old = 0

    elif new_q :  ##new quantity only
        print("pass phase 6")
        if new_tpp_old_p :
            quantity_old = quantity_new
            packet_old = packet_new
            quantity_new = packet_new = 0
    elif old_q :
        print("pass phase 7")
        if old_tpp_new_p:
            quantity_new = quantity_old
            packet_new = packet_old
            quantity_old = packet_old = 0


    if bill_total_money > 0 :

        Point_Product.objects.create(money_quantity = bill_total_money ,date = date,quantity_new = quantity_new,
            quantity_packet_new = packet_new, quantity_old = quantity_old , quantity_packet_old = packet_old , product = product,
            Point = to_point , given_status = 1 , notes = notes,quantity_per_packet = tpp.quantity_per_packet ,unit_buy_price = tpp.unit_buy_price,
            last_quantity_per_packet = tpp.last_quantity_per_packet, last_unit_buy_price = tpp.last_unit_buy_price )

        print("pass phase 8")
        ## update old product in from point
        tpp.total_product_quantity -=(old_q + new_q)
        tpp.last_update = date
        tpp.save()
        tpp.subtract_from_product(lq,lqp,nq,nqp)

        ## update new product in to point
        ttp_to_point.total_product_quantity +=(old_q + new_q)
        ttp_to_point.last_update = date
        ttp_to_point.save()

        ttp_to_point.add_to_product(quantity_old, packet_old, quantity_new, packet_new)


        ##update point total products raw cost
        point.total_money_raw -=bill_total_money
        point.save()
        ##update point total products raw cost
        to_point.total_money_raw -=bill_total_money
        to_point.save()


    else:
        return False
    return True



@login_required
def all_discount_bills(request):
    bills_with_discount = get_all_bills_with_discount(request)

    total_discounts = sum(b.total_discount for b in bills_with_discount )
    context= {
        'bills':bills_with_discount,
        'total_discounts':total_discounts,

    }
    return render(request, 'content/all_discount_bills.html', context)

def get_all_bills_with_discount(request):
    cur_m = Current_manager.objects.get(user = request.user)
    bills_with_discount = Customer_Bill.objects.filter(given_status = 1, bill_type = 0, date__date__gte = cur_m.start_date, date__date__lte = cur_m.end_date)

    result = []
    # result.append(bill for bill in un_paid_bills if bill.remaining_amount < 0 )
    for bill in bills_with_discount:
        if bill.total_discount > 0:
            result.append(bill)

    return result

def normalize_product_v(product, old_q , new_q):
    ## normalize product
    lq,lqp,nq,nqp = (0,0,0,0)
    if product.quantity_per_packet :
        nqp , nq = divmod(new_q , product.quantity_per_packet)

    if product.last_quantity_per_packet :
        lqp , lq = divmod(old_q , product.last_quantity_per_packet)


    return (lq, lqp, nq, nqp)
