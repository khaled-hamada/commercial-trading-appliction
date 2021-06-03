from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Sandwich, DaySandwich, Product, Day_Payment_Line, Acumulate_payment, Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings,Total_Point_Product,Month_Total_Calculation
from .models import Sandwich_Type,Bread_Type,Katchab,Packet, Measurement_Unit, Sub_Product

from django.utils import timezone
from django.db.models import Sum,Q




@login_required
def product_page(request, product_id):
    product = Product.objects.get(id = product_id)
    ##
    tpps = Total_Point_Product.objects.filter(product = product)
    tpp_q = tpp_c = 0
    for tpp in tpps:
        tpp_q += tpp.total_product_quantity
        tpp_c += tpp.total_cost


    if request.method == "POST":
        trader = Trader.objects.get(id = int(request.POST['trader_id']))
        try :
            product_trader =  Trader_Product.objects.filter(product = product, trader = trader)
            if len(product_trader) > 0 : ## ie this trader is already mapped to this product previously
                print("trader already exists")
            else :
                # tp = Trader_Product.objects.get(product = product)
                # tp.add(trader)
                # tp.save()
                # Trader_Product.objects.create(product = product, trader = trader)
                print("add a new trader")
                product.trader.add(trader)
                # Trader_Product.objects.filter(quantity = 0, quantity_packet=0).last().delete()

        except :
            print("errors occurs")
    product_sellers = Trader_Product.objects.filter(product = product).values_list('trader').distinct()
    product_sellers_names = set()
    for tp in product_sellers:
        product_sellers_names.add(Trader.objects.get(id = tp[0]))

    # print(product_sellers)
    # print(product_sellers_names)
    product_transactions = Trader_Product.objects.filter(product = product).order_by('-date')
    traders = Trader.objects.all()
    context = {
        'p':product,
        'point_product':product,
        'tpp_q':tpp_q,
        'tpp_c':tpp_c,
        'product_sellers':product_sellers_names,
        'product_transactions':product_transactions,
        'traders':traders,

    }
    return render(request, 'content/product_page.html',context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def update_product(request, trader_id):
    failed = success = 0
    trader = Trader.objects.get( id = trader_id)
    if request.method == "POST":
        product_id = int(request.POST['product_id'])
        product = Product.objects.get(id = product_id)
        if product != None:
            # date = request.POST['date']
            date = timezone.now()
            new_amount =  int(request.POST['quantity'])
            quantity_packet =  int(request.POST['quantity_packet'])
            packet_price =  float(request.POST['packet_price'])
            quantity_per_packet =  int(request.POST['quantity_per_packet'])
            bill_file = request.FILES['bill_file']

            ## check validation that both old and new prices match : else go update product prices
            if product.packet_price == packet_price and product.quantity_per_packet == quantity_per_packet :
                # product.quantity +=new_amount
                # product.quantity_packet +=quantity_packet
                # ##update total ammount
                # # product.total_quantity +=(new_amount + (quantity_packet *  product.quantity_per_packet))
                # product.save()
                # ## make quantity always less than quantity per packet
                # q,r = divmod(product.quantity, product.quantity_per_packet)
                # if q > 0:
                #     product.quantity = r
                #     product.quantity_packet += q
                #     product.save()
                product.add_to_product(0, 0,new_amount, quantity_packet )
                ## update trader total money
                total_product_cost  = product.unit_buy_price * new_amount + product.packet_price * quantity_packet
                total_product_cost = round(total_product_cost , 2)
                trader.total_money += total_product_cost
                trader.save()
                ## update remaing money
                # trader.remaining_money = trader.total_money - trader.given_money
                trader.save()
                manager = Current_manager.objects.get(user= request.user)
                ## create new bill

                print("new trader product " )
                print((total_product_cost))
                Trader_Product.objects.create(manager = manager, trader = trader , product = product, date = date , quantity = new_amount ,quantity_packet = quantity_packet
                                                ,total_cost = total_product_cost, total_cost_old = total_product_cost, bill_file=bill_file)
                ## update mtc
                # Trader_Product.objects.create(manager = manager, trader = trader , product = product, date = date , quantity = new_amount ,quantity_packet = quantity_packet )
                ## update mtc
                mtc = Month_Total_Calculation.objects.last()
                mtc.traders_depts +=total_product_cost
                mtc.total_products_money +=total_product_cost
                mtc.save()
                success = 1
            else:
                failed = 1
        else:
             failed = 1

    products = Product.objects.filter(trader = trader).distinct()
    # traders = Trader.objects.all()
    context = {'products':products , 'failed':failed, 'success':success, "trader":trader}
    # print( len(products))
    return render(request, 'content/update_product.html',context = context)


## update product prices
@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def update_product_prices(request, product_id):
    failed = success = 0

    if request.method == "POST":
        product = update_prices_cases(request,product_id)
        if product == None:
            failed = 1
        elif product != None:
            success = 1

    product = Product.objects.get(id = product_id)
    context = {'product':product , 'failed':failed, 'success':success}
    # print( len(products))
    return render(request, 'content/update_product_prices.html',context = context)




def make_sure_a_correct_product(p):
    if '.' in p and len(p.split('.',1)) == 2:
        products = Product.objects.all()
        p_name = p.split('.',1)[1]
        p_id = p.split('.',1)[0]
        for p in products:
            if p_name == p.name:
                if p_id.isdigit():
                    return True
                else:
                    return False
    return False


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def new_product_type(request):
    traders = Trader.objects.all()
    mus= Measurement_Unit.objects.all()
    failed = 0
    if request.method == "POST":
        product_name = request.POST['product_name']
        quantity_packet = int(request.POST['quantity_packet'])
        quantity_per_packet = int(request.POST['quantity'])
        if 'quantity_per_unit' in request.POST:
            try:
                quantity_per_unit = int(request.POST['quantity_per_unit'])
                mu_id = int(request.POST['mu_id'])
                sub_product_price = float(request.POST['sub_product_prices'])
            except :
                quantity_per_unit = 0

        packet_price = float(request.POST['packet_price'])
        unit_buy_price = round(packet_price / quantity_per_packet , 3)
        unit_sell_price = float(request.POST['unit_sell_price'])
        descreption = request.POST['descreption']
        bill_file = request.FILES['bill_file']
        ## create and save new product
        trader = Trader.objects.filter(id = int(request.POST['trader_id'])).first()

        ## check tyhat product is not in the database i.e not in the store  ---> a new product really
        try:
            prod = Product.objects.get(name = product_name)
            ## if success failed = 1
            failed = 1
            print("existing product")

        except :
            failed = 0
            print("new product")

        if failed ==0 :
                p = Product(name = product_name, quantity_per_packet = quantity_per_packet, unit_buy_price =unit_buy_price, unit_sell_price = unit_sell_price,
                    descreption = descreption, quantity_packet= quantity_packet , packet_price = packet_price)

                p.save()
                # p.total_quantity +=((quantity_packet *  p.quantity_per_packet))
                p.save()
                p.trader.add(trader)
                ## if it has a subproduct
                if quantity_per_unit > 0 :
                    print('create sub product')
                    mu = Measurement_Unit.objects.get(id = mu_id)
                    Sub_Product.objects.create(product = p, measurement_unit = mu, quantity_per_unit = quantity_per_unit ,unit_sell_price = round((sub_product_price / quantity_per_unit) , 3) )
                ##add sub_product data



                ## update trader total money
                bill_price = round((p.packet_price *  quantity_packet), 2)
                trader.total_money +=bill_price
                trader.save()
                # ## update remaing money
                # trader.remaining_money = trader.total_money - trader.given_money
                # trader.save()
                ## update mtc
                mtc = Month_Total_Calculation.objects.last()
                mtc.traders_depts += bill_price
                mtc.total_products_money += bill_price

                mtc.save()
                ## create new trader bill
                manager = Current_manager.objects.get(user= request.user)
                total_product_cost  =  bill_price
                Trader_Product.objects.create(manager = manager,trader = trader , product = p, date = timezone.now() , quantity = 0,quantity_packet = quantity_packet
                                                ,total_cost = total_product_cost , total_cost_old = total_product_cost, bill_file = bill_file)
                Trader_Product.objects.filter(quantity = 0, quantity_packet=0).last().delete()
                return redirect('content:store')

    context = {
        'traders':traders,
        'failed':failed,
        'mus':mus,
    }
    return render(request, 'content/new_product_type.html',context = context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_new_mu(request):
    Measurement_Unit.objects.create(name = request.POST['unit_name'])
    return redirect('content:new_product_type')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_mu(request):
    Measurement_Unit.objects.get(id = int(request.POST['mu_id'])).delete()
    return redirect('content:new_product_type')




#
# 8 update cases from 0 0 0 to 1 1 1
#i need to handle them all
# 1                     2                       3
#new_packet_price       new_packet_quanatity    new_unit_sell_price
##
# return updates product
def update_prices_cases(request,product_id):
        failed = 0
        new_packet_price = float(request.POST['new_packet_price'])
        new_packet_quantity = int(request.POST['new_packet_quantity'])
        new_unit_sell_price = float(request.POST['new_unit_sell_price'])
        product = Product.objects.get(id = product_id)
        ## first case all 1 case 2   1 and 2 only
        if (new_packet_price and new_packet_quantity and new_unit_sell_price) or (new_packet_price  and new_packet_quantity) :
            if new_unit_sell_price != 0 and new_unit_sell_price >= product.unit_sell_price:
                ## update price
                product.unit_sell_price = new_unit_sell_price

            elif new_unit_sell_price == 0 and new_packet_price != 0 :
                failed = 0
            else :
                failed = 1
            ## update last data , check first to see that old product has been completely sold
            if product.last_quantity ==0 and product.last_quantity_packet==0 :
                update_product_helper(product= product, case = 1, new_packet_quantity= new_packet_quantity, new_packet_price = new_packet_price , request = request )
            elif product.quantity == 0 and product.quantity_packet == 0:
                update_product_helper(product = product, case = 0, new_packet_quantity= new_packet_quantity, new_packet_price = new_packet_price,request = request )
            else :
                failed = 1

            ## return none in case of failed = 1 and wh have new packet quantity and new packet price
            if failed :
                return None
            product.save()
            return product
        ## case 3 and 4   1 and 3 only or 1 only
        elif (new_packet_price  and new_unit_sell_price) or new_packet_price:
            if new_unit_sell_price !=0 and new_unit_sell_price >= product.unit_sell_price :
                product.unit_sell_price = new_unit_sell_price

            elif new_unit_sell_price == 0 and new_packet_price != 0 :
                failed = 0
            else :
                failed = 1
            ## update last data , check first to see that old product has been completely sold
            if product.last_quantity ==0 and product.last_quantity_packet==0 :
                update_product_helper(product = product, case = 2, new_packet_quantity= new_packet_quantity, new_packet_price = new_packet_price,request = request )

            elif product.quantity == 0 and product.quantity_packet == 0:
                update_product_helper(product = product, case = 4, new_packet_quantity= new_packet_quantity, new_packet_price = new_packet_price,request = request )

            else :
                failed = 1

            ## return none in case of failed = 1 and wh have new packet quantity and new packet price
            if failed :
                return None
            product.save()
            return product
        ## case 5,6 and 7   2 and 3 only or 2 only or 3 only
        elif (new_packet_quantity  and new_unit_sell_price) or new_unit_sell_price or new_packet_quantity:
            if new_unit_sell_price !=0 and new_unit_sell_price >= product.unit_sell_price :
                product.unit_sell_price = new_unit_sell_price
                ## update last data
            elif new_unit_sell_price == 0 and new_packet_quantity!=0 :
                failed = 0
            else:
                failed = 1
            if new_packet_quantity :
                ## update last data , check first to see that old product has been completely sold
                if product.last_quantity ==0 and product.last_quantity_packet==0 :
                    update_product_helper(product = product, case = 3, new_packet_quantity= new_packet_quantity, new_packet_price = new_packet_price,request = request )


                elif product.quantity == 0 and product.quantity_packet == 0:
                        update_product_helper(product = product, case = 5, new_packet_quantity= new_packet_quantity, new_packet_price = new_packet_price,request = request )

                else :
                    failed = 1

            ## return none in case of failed = 1 and wh have new packet quantity and new packet price
            if failed :
                return None
            product.save()
            return product

        return None





def update_product_helper(product, case, new_packet_quantity, new_packet_price, request ):
    ## case 1 ,2,3  move new to old
    ## case 1,0 do not move just update new , both packet price and quantity per packet
    ## case 2,4 update new data, update only packe price
    if case == 1 or case == 2 or case ==3:
        print("inside case 1 or 2 or 3")
        product.last_quantity = product.quantity
        product.last_quantity_packet = product.quantity_packet
        product.last_quantity_per_packet = product.quantity_per_packet
        product.last_packet_price = product.packet_price
        product.last_unit_buy_price = product.unit_buy_price

    if case == 0 or case == 1:

        product.quantity_per_packet = new_packet_quantity
        product.packet_price = new_packet_price
        product.unit_buy_price =round( (new_packet_price / new_packet_quantity), 3)

    if case == 2 or case == 4 :

        # product.last_quantity_per_packet = product.quantity_per_packet
        product.packet_price = new_packet_price
        product.unit_buy_price = round((new_packet_price / product.quantity_per_packet), 3)
    if case ==3 or case == 5:

        product.quantity_per_packet =new_packet_quantity
        # product.packet_price = new_packet_price
        product.unit_buy_price = round((product.packet_price / new_packet_quantity))


    ## update new data
    product.quantity = 0
    product.quantity_packet = 0
    product.descreption = request.POST['descreption']
    product.save()

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def reduce_product_amount_store(request, product_id):
    product = Product.objects.get(id =product_id )
    if request.method == "POST":
        try :
            quantity = int(request.POST['new_quantity'])
            quantity_packet = int(request.POST['new_quantity_packet'])
        except :
            quantity = quantity_packet = 0
        try :
            last_quantity_packet = int(request.POST['last_quantity_packet'])
            last_quantity = int(request.POST['last_quantity'])
        except :
            last_quantity_packet  = last_quantity =0


        ##  check validation
        new_amount = quantity + (quantity_packet * product.quantity_per_packet)
        old_amount = last_quantity + (last_quantity_packet * product.last_quantity_per_packet)
        if new_amount <= product.amount_new and old_amount <= product.amount_old :
            product.subtract_from_product(last_quantity,last_quantity_packet, quantity, quantity_packet )
            ## reduced amount cost
            total_cost = product.calculate_cost(last_quantity, last_quantity_packet, quantity, quantity_packet )

            mtc = Month_Total_Calculation.objects.last()
            mtc.total_products_money -= total_cost
            mtc.save()

    context ={
        'product' : product,
    }
    return render(request, "content/reduce_product_amount_store.html", context = context)
