# from django.shortcuts import render,redirect
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib.auth.models import User
# from .models import Sandwich, DaySandwich, Product, Day_Payment_Line, Acumulate_payment, Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
# from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings,Total_Point_Product,Month_Total_Calculation
# from .models import Sandwich_Type,Bread_Type,Katchab,Packet
#
# from django.utils import timezone
# from django.db.models import Sum,Q
#
#
# @login_required
# def add_sandwich_components(request,type_id):
#     success = failed =0
#     ## i have 4 components
#     ## type_id = 1   ---->  sand_type
#     ## type_id = 2   ---->  packet
#     ## type_id = 3   ---->  katchab
#     ## type_id = 4   ---->  Bread_Type
#     type = None
#     if type_id == 1:
#         types = Sandwich_Type.objects.all()
#     elif type_id == 2:
#         types = Packet.objects.all()
#     elif type_id == 3:
#         types = Katchab.objects.all()
#     elif type_id == 4:
#         types = Bread_Type.objects.all()
#
#     if request.method == "POST":
#         type = types.filter(id = int(request.POST['type_n_id'])).first()
#         new_packet_q = int(request.POST['new_packet_q'])
#         packet_price = float(request.POST['packet_price'])
#         q_per_packet = int(request.POST['q_per_packet'])
#
#         if type == None :
#             failed = 1
#         elif check_validation_com(request, type, new_packet_q, packet_price, q_per_packet):
#             success = 1
#         else :
#             failed = 1
#
#     context = {
#         'success':success,
#         'failed':failed,
#         "types":types,
#
#     }
#     return render(request , "content/add_sandwich_components.html", context = context)
#
#
# def check_validation_com(request, type, npq, pp, qpp):
#     new_up = pp / qpp
#     bill_cost = npq * pp
#     total_new_amount = qpp * npq
#     m_safe = Safe_Month.objects.last()
#     mtc = Month_Total_Calculation.objects.last()
#
#     if bill_cost > m_safe.money:
#         return False
#
#
#
#     success = 0
#     if (type.amount_new + type.amount_old )== 0:
#         type.amount_new += (npq * qpp)
#         type.new_packet_cost = pp
#         type.new_quantity_per_packet =qpp
#         type.new_unit_buy_price =new_up
#         type.save()
#         success = 1
#
#     elif type.new_unit_buy_price == new_up:
#          type.amount_new += (npq * qpp)
#          type.new_packet_cost = pp
#          type.new_quantity_per_packet =qpp
#          type.new_unit_buy_price =new_up
#          type.save()
#          success = 1
#
#     elif type.old_unit_buy_price == new_up:
#          type.amount_old += (npq * qpp)
#          type.old_packet_cost = pp
#          type.old_quantity_per_packet =qpp
#          type.old_unit_buy_price =new_up
#          type.save()
#          success = 1
#
#     elif  type.new_unit_buy_price != new_up and type.amount_old ==0:
#          type.amount_old += type.amount_new
#          type.old_packet_cost = type.new_packet_cost
#          type.old_quantity_per_packet =  type.new_quantity_per_packet
#          type.old_unit_buy_price =   type.new_unit_buy_price
#
#
#          type.amount_new = (npq * qpp)
#          type.new_packet_cost = pp
#          type.new_quantity_per_packet =qpp
#          type.new_unit_buy_price =new_up
#          type.save()
#          success = 1
#     else :
#         return False
#
#
#
#     cur_m = Current_manager.objects.get(user = request.user)
#     notes = " ?????? ????????  " + str(total_new_amount) + " - ???????? " + str(type)
#     m_safe.money -= bill_cost
#     mtc.safe_current_money -=bill_cost
#     mtc.save()
#     m_safe.save()
#     Safe_data.objects.create(day = timezone.now().date(), money_amount = -bill_cost,notes = notes ,given_person = cur_m )
#     return success
#
#
#
#
#
#
# @login_required
# def add_new_sandwitch(request):
#     success = failed = 0
#     sands= Sandwich_Type.objects.all()
#     breads = Bread_Type.objects.all()
#     if request.method == "POST":
#         sand_type = Sandwich_Type.objects.get(id = int(request.POST['sand_type']))
#         bread_type = Bread_Type.objects.get(id = int(request.POST['bread_type']))
#         kat = int(request.POST['kat_amount'])
#         if kat== 1:
#             kat = Katchab.objects.last()
#         else:
#             kat = None
#
#         pack = int(request.POST['pak_amount'])
#         if pack == 1:
#             pack = Packet.objects.last()
#         else:
#             pack = None
#
#         price = float(request.POST['price'])
#         sand_check = Sandwich.objects.filter(sandwich_type =sand_type,  bread = bread_type  ).count()
#         if sand_check != 0 :
#             failed = 1
#         else:
#             Sandwich.objects.create(sandwich_type = sand_type , bread = bread_type , katchab = kat, packet = pack, unit_sell_price =price )
#             success = 1
#
#     context = {
#             'success':success,
#             'failed':failed,
#             'sands':sands,
#             'breads':breads,
#     }
#     return render(request, 'content/add_new_sandwitch.html', context = context)
#
# @login_required
# def sandwitch(request):
#     data = []
#     sands = Sandwich.objects.all()
#     today_date =  timezone.now().date()
#     user  = Current_manager.objects.filter(user = request.user).first()
#     for s in sands :
#         s_item = []
#         total = 0
#         days = DaySandwich.objects.filter(sandwich = s.id, date__gte = user.start_date ,date__lte = user.end_date )
#         for day in days:
#             total += day.profit
#         s_item.append(s) ## item.0
#         s_item.append(days)## item.1
#         s_item.append(total)## item.2
#         data.append(s_item)
#
#     context= {
#         'data':data
#     }
#     return render(request, 'content/sandwitch.html', context = context)
#
#
# @login_required
# def add_sandwitch(request):
#     sands = Sandwich.objects.all()
#     success = 0
#     if request.method == 'POST':
#         sand_id = int(request.POST['sand_id'])
#         date = timezone.now()
#
#         quantity = int(request.POST['quantity'])
#         sand = Sandwich.objects.get(id = sand_id)
#
#         if sand.sandwich_type :
#             sand.sandwich_type.subtract(quantity)
#         if sand.katchab :
#             sand.katchab.subtract(quantity)
#         if sand.bread :
#             sand.bread.subtract(quantity)
#         if sand.packet :
#             sand.packet.subtract(quantity)
#
#
#         ## CALCULATE RELEVANT DATA
#         total_cost = sand.unit_cost_price * quantity
#         total_return = sand.unit_sell_price * quantity
#         profit = total_return - total_cost
#         new_entry = DaySandwich(number = quantity, total_return = total_return,
#                         profit = profit , date = date , sandwich = sand   ,total_cost = total_cost     )
#
#         new_entry.save()
#         ## update mtc total profit
#         mtc = Month_Total_Calculation.objects.last()
#         mtc.total_profit_sandwiches += profit
#         mtc.safe_current_money +=total_return
#         mtc.save()
#
#         m_safe = Safe_Month.objects.last()
#         m_safe.money +=total_return
#         m_safe.save()
#         ## create bill to save
#         cur_m = Current_manager.objects.get(user = request.user)
#         notes = "??????????  " + str(quantity) +" ?????????????? " + str(sand)
#
#         Safe_data.objects.create(day = date.date(), money_amount = total_return,notes = notes ,given_person = cur_m )
#         success = 1
#
#     context = {
#         'sands':sands,
#         'success':success,
#     }
#     return render(request, 'content/add_sandwitch.html' ,context)
