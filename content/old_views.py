from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Sandwich, DaySandwich, Product, Day_Payment_Line, Acumulate_payment, Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings,Total_Point_Product,Month_Total_Calculation
from .models import Sandwich_Type,Bread_Type,Katchab,Packet

from django.utils import timezone
from django.db.models import Sum,Q




def calculate_mqpp(product):
    mqpp = 0
    if (product.last_quantity + (product.last_quantity_packet * product.last_quantity_per_packet))  == 0:
        mqpp = product.quantity_per_packet
    elif (product.quantity + (product.quantity_packet * product.quantity_per_packet))  == 0 :
        mqpp = product.last_quantity_per_packet
    elif product.quantity_per_packet < product.last_quantity_per_packet and (product.last_quantity + (product.last_quantity_packet * product.last_quantity_per_packet))  > 0:
        mqpp =  product.quantity_per_packet
    else :
        mqpp = product.last_quantity_per_packet


    return mqpp

## helper function for the above function
def update_product_remaining_total_amount(product, total_required_quantity, point):
    new_total_prodcut_money = 0
    r=q=0
    have_old = 0
    ## create new point trader bill
    date = timezone.now().date()
    Point_Product.objects.create( date = timezone.now(), product = product,Point = point)
    current_bill_s = Point_Product.objects.filter( date = date, product = product,Point = point).last()
    ## for update to work wothout save
    current_bill = Point_Product.objects.filter(id = current_bill_s.id)
    ## first subtractfrom old product  single amount and i have any remaing old product parts
    if  (product.last_quantity + (product.last_quantity_packet * product.last_quantity_per_packet)) > 0:
        have_old = 1
        q,r = divmod(total_required_quantity, product.last_quantity_per_packet)
        if r > 0 :
            if product.last_quantity >= r:
                product.last_quantity -=r
                new_total_prodcut_money += r * product.last_unit_buy_price
                current_bill.update(quantity_old = r)
                r= 0
                product.save()
                print("1. %f" %(new_total_prodcut_money))
            ## last quantity < r  but i have complete packets
            elif product.last_quantity_packet > 0  :
                ## if a single packet is greater or equal r
                if product.last_quantity_per_packet >= r :
                    product.last_quantity_packet -=1
                    product.last_quantity += (product.last_quantity_per_packet - r)
                    new_total_prodcut_money += r * product.last_unit_buy_price
                    current_bill.update(quantity_old = r)
                    product.save()
                    r = 0
                    print("2. %f" %(new_total_prodcut_money))
            ## else i do not have complete packets and last_quantity < r :
            else :
                new_total_prodcut_money += (product.last_quantity* product.last_unit_buy_price)
                remain_r = r- product.last_quantity
                current_bill.update(quantity_old = product.last_quantity)
                product.last_quantity = 0
                r = remain_r
                product.save()
                print("3. %f" %(new_total_prodcut_money))


        print("4. %f" %(new_total_prodcut_money))
        ## in case of r = 0 but q not :
        if r == 0 and q != 0:
            if product.last_quantity_packet >= q  :
                new_total_prodcut_money += (q* product.last_packet_price)
                product.last_quantity_packet -= q
                current_bill.update(quantity_packet_old = q)
                product.save()
                q = 0
                print("5. %f" %(new_total_prodcut_money))
            elif product.last_quantity_packet != 0 :
                new_total_prodcut_money += (product.last_quantity_packet * product.last_packet_price)
                remain_q = q - product.last_quantity_packet
                current_bill.update(quantity_packet_old = product.last_quantity_packet)
                product.last_quantity_packet = 0
                q = remain_q
                product.save()
                print("6. %f , q=%d" %(new_total_prodcut_money, q))
        ## the old product is enough for the total_required_quantity
        if r == 0 and q == 0 :
            print("7. %f, q=%d" %(new_total_prodcut_money, q))
            current_bill.update(money_quantity = new_total_prodcut_money)

            return new_total_prodcut_money
        ## last case the old product does not suffice the required amount

    if (r !=0 or q != 0) and  have_old:
        print("7-1. r=%d, q=%d" %(r, q))
        total_required_quantity = r + product.last_quantity_per_packet * q


    ## if i do not have any old product then subtract all from the new amount
    ## second subtract from new product packets amount
    if not have_old:
        q,r = divmod(total_required_quantity, product.quantity_per_packet)
    if r !=0 or q != 0 :
        print("8. %f" %(new_total_prodcut_money))
        q,r = divmod(total_required_quantity, product.quantity_per_packet)
        if r > 0 :
            if product.quantity >= r:
                product.quantity -=r
                new_total_prodcut_money += r * product.unit_buy_price
                current_bill.update(quantity_new = r)
                r= 0
                product.save()
                print("9. %f" %(new_total_prodcut_money))
            ## last quantity <  r  but i have complete packets
            elif product.quantity_packet > 0  :
                ## if a single packet is greater or equal r
                if product.quantity_per_packet >= r :
                    product.quantity_packet -=1
                    product.quantity += (product.quantity_per_packet - r)
                    new_total_prodcut_money += r * product.unit_buy_price
                    product.save()
                    current_bill.update(quantity_new = r)
                    r = 0
                    print("10. %f" %(new_total_prodcut_money))



        ## in case of r = 0 but q not :
        if r == 0 and q != 0:
            if product.quantity_packet >= q  :
                new_total_prodcut_money += (q* product.packet_price)
                product.quantity_packet -= q
                product.save()
                current_bill.update(quantity_packet_new = q)
                q = 0
                print("11. %f" %(new_total_prodcut_money))
        ## the old product is enough for the total_required_quantity
        if r == 0 and q == 0 :
            print("12. %f" %(new_total_prodcut_money))
            current_bill.update(money_quantity = new_total_prodcut_money)
            return new_total_prodcut_money


        ## last case the old product does not suffice the required amount
        ## note we cannot fail cause we assume from the begining we have sufficient amount
        current_bill = current_bill.last()
        if r !=0 or q != 0 :
            ## incase of i have only singles without any remaing complete packet
            print("13-1. r=%d, q=%d" %(r, q))
            total_need_singles = r + (q *product.quantity_per_packet)
            ## take out all old singles first in this case i am sure that total_need_singles > r
            new_total_prodcut_money += (product.last_quantity* product.last_unit_buy_price)
            remain_r =  total_need_singles - product.last_quantity
            current_bill.quantity_old +=  product.last_quantity
            current_bill.save()
            product.last_quantity = 0
            product.save()

            ## then complete from new singles
            total_need_singles= remain_r
            if (product.quantity >= total_need_singles) and total_need_singles !=0:
                product.quantity -=total_need_singles
                new_total_prodcut_money += total_need_singles * product.unit_buy_price
                current_bill.quantity_new +=  total_need_singles
                current_bill.save()
                total_need_singles= 0
                product.save()

            print("13. %f" %(new_total_prodcut_money))
            # current_bill.delete()
            current_bill.update(money_quantity = new_total_prodcut_money)
            return new_total_prodcut_money    ## failrue

    ## complete failure
    current_bill.delete()
    return 0  ## complete failure
