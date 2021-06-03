from django.contrib import admin
from .models import Sandwich, DaySandwich, Product, Day_Payment_Line, Acumulate_payment, Safe_data, withdrawings,Current_manager, Trader, Trader_Product, Point_User, Point_Product, Point, Point_User_Payment,Trader_Payment
# Register your models here.
from .models import Safe_Month,Total_Point_Product,Point_Product_Sellings,Month_Total_Calculation,Trader_Product_Data,Sandwich_Type,Bread_Type,Katchab,Packet
from .models import Customer,Customer_Bill,Customer_Payment,Trader_Product_Restore, Sub_Product, Measurement_Unit

admin.site.register(Sandwich)
admin.site.register(DaySandwich)
admin.site.register(Product)
admin.site.register(Day_Payment_Line)
admin.site.register(Acumulate_payment)
admin.site.register(Safe_data)
admin.site.register(Safe_Month)
admin.site.register(withdrawings)
admin.site.register(Current_manager)
admin.site.register(Trader)
admin.site.register(Trader_Product)
admin.site.register(Point)
admin.site.register(Point_User)
admin.site.register(Point_Product)
admin.site.register(Point_User_Payment)
admin.site.register(Total_Point_Product)
admin.site.register(Point_Product_Sellings)
admin.site.register(Trader_Payment)
admin.site.register(Trader_Product_Restore)
admin.site.register(Month_Total_Calculation)
admin.site.register(Trader_Product_Data)
admin.site.register(Sandwich_Type)
admin.site.register(Bread_Type)
admin.site.register(Katchab)
admin.site.register(Packet)


admin.site.register(Customer)
admin.site.register(Customer_Bill)
admin.site.register(Customer_Payment)
admin.site.register(Sub_Product)
admin.site.register(Measurement_Unit)
