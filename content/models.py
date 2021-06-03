from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
# Create your models here.


class Current_manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    month_tc = models.ForeignKey('Month_Total_Calculation', on_delete=models.CASCADE, null = True,blank=True)
    active_status = models.IntegerField(default=0)
    start_date =  models.DateField(default = now)
    end_date =  models.DateField(default = now)
    safe = models.ForeignKey('Safe_Month',on_delete=models.CASCADE, blank=True ,null = True)
    def __str__(self):
        return self.user.first_name

class Point_User(models.Model):
    active_status = models.IntegerField(default = 0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date =  models.DateField(default = now)
    end_date =  models.DateField(default = now)
    total_money_required = models.FloatField(default=0.0)
    total_money_given = models.FloatField(default=0.0)
    total_money_remaining= models.FloatField(default=0.0)
    point = models.ForeignKey('Point',on_delete = models.CASCADE,blank= True,null = True)
    def __str__(self):
        return self.user.first_name

## فواتير النقاط
class Point_User_Payment(models.Model):
    g_user = models.ForeignKey('Point', on_delete=models.CASCADE)
    t_user = models.ForeignKey('Current_manager', on_delete=models.CASCADE)
    date = models.DateTimeField(default = now)
    amount= models.FloatField(default=0.0)

    def __str__(self):
        return self.g_user.name

## لسماء النقاط
class Point(models.Model):
    name = models.CharField(max_length = 264)
    remaining_money = models.FloatField(default=0.0)
    given_money =models.FloatField(default=0.0)
    total_money = models.FloatField(default=0.0)
    total_money_raw = models.FloatField(default=0.0)
    def __str__(self):
        return self.name

## بضائع النقاط create point new bills
class Point_Product(models.Model):
    objects = models.Manager()
    ## cost of buying this materials
    money_quantity = models.FloatField(default = 0)
    ## not used to avoid errors we calculate points total products units
    quantity_packet = models.IntegerField(default = 0)

    date = models.DateTimeField(default=now, null=True)

    quantity_new = models.IntegerField(default = 0)
    quantity_packet_new = models.IntegerField(default = 0)
    quantity_per_packet =  models.IntegerField(default = 0)
    unit_buy_price = models.FloatField(default = 0)

    quantity_old =  models.IntegerField(default = 0)
    quantity_packet_old =  models.IntegerField(default = 0)
    last_quantity_per_packet =  models.IntegerField(default = 0)
    last_unit_buy_price = models.FloatField(default = 0)

    given_status =  models.IntegerField(default = 0)

    product = models.ForeignKey('Product', on_delete = models.CASCADE, null = True)
    Point = models.ForeignKey('Point', on_delete = models.CASCADE, null = True)
    notes = models.TextField(default="", null=True)

    def __str__(self):
        return self.product.name +  "  --  trader name :-> " + self.Point.name


    @property
    def total_q_old(self):
            return   ( self.quantity_old  + (self.last_quantity_per_packet *self.quantity_packet_old ))

    @property
    def total_q_old_price(self):
        # tpp = Total_Point_Product.objects.get(Point = self.Point, product = self.product)
        cost =  self.total_q_old  * self.last_unit_buy_price
        return round(cost , 2)


    @property
    def total_q_new(self):
        # tpp = Total_Point_Product.objects.get(Point = self.Point, product = self.product)
        return   ( self.quantity_new  + (self.quantity_per_packet *self.quantity_packet_new ))


    @property
    def total_q_new_price(self):
        # tpp = Total_Point_Product.objects.get(Point = self.Point, product = self.product)
        cost =  self.total_q_new   * self.unit_buy_price
        # print("tpp get data to front end total_q %d , cost%f" %(self.total_q_new, cost))
        return round(cost , 2)

## بضائع النقاط المتبقية
class Total_Point_Product(models.Model):
    objects = models.Manager()
    total_product_quantity =models.IntegerField(default = 0)
    ##current prices and units per packet
    quantity = models.IntegerField(default = 0)
    quantity_packet = models.IntegerField(default = 0)

    quantity_per_packet = models.IntegerField(default = 0)
    packet_price = models.FloatField(default=0.0)
    unit_buy_price =models.FloatField(default=0.0)
    ##last prices and units per packet
    last_quantity = models.IntegerField(default = 0)
    last_quantity_packet = models.IntegerField(default = 0)

    last_quantity_per_packet = models.IntegerField(default = 0)
    last_packet_price = models.FloatField(default=0.0)
    last_unit_buy_price =models.FloatField(default=0.0)

    sub_p_current_quantity = models.IntegerField(default = 0 )

    last_update = models.DateTimeField(default=now, null=True)

    product = models.ForeignKey('Product', on_delete = models.CASCADE, null = True)
    sub_product = models.ForeignKey('Sub_Product', on_delete = models.CASCADE, null = True)
    Point = models.ForeignKey('Point', on_delete = models.CASCADE, null = True)

    def __str__(self):
        return self.product.name +  "  --  point name :-> " + self.Point.name

    @property
    def total_cost(self):
        total =    ( self.quantity * self.unit_buy_price)  + ( self.quantity_packet * self.packet_price) +\
                ( self.last_quantity * self.last_unit_buy_price)  + ( self.last_quantity_packet * self.last_packet_price)
        return round(total , 2)

    @property
    def total_cost_sell(self):
        return   ( self.total_product_quantity * self.product.unit_sell_price)

    @property
    def old_amount_cost(self):
        return round((self.last_quantity + (self.last_quantity_packet * self.last_quantity_per_packet)) *self.last_unit_buy_price  , 2)

    @property
    def new_amount_cost(self):
         return round((self.quantity + (self.quantity_packet * self.quantity_per_packet) ) * self.unit_buy_price, 2)

    @property
    def old_amount(self):
        return self.last_quantity + (self.last_quantity_packet * self.last_quantity_per_packet)

    @property
    def new_amount(self):
         return self.quantity + (self.quantity_packet * self.quantity_per_packet)

    def normailze_product(self):
        ## normalize product
        if self.quantity_per_packet :
            quo , rem = divmod(self.quantity , self.quantity_per_packet)
            self.quantity = rem
            self.quantity_packet += quo

        if self.last_quantity_per_packet :
            quo , rem = divmod(self.last_quantity , self.last_quantity_per_packet)
            self.last_quantity = rem
            self.last_quantity_packet += quo

        self.save()


    def subtract_from_product(self, lq , lqp, nq, nqp):
        ##normalize subtracted quantities
        if lq:
            quo, rem = divmod(lq, self.last_quantity_per_packet)
            lq = rem
            lqp += quo
        if nq:
            quo, rem = divmod(nq, self.quantity_per_packet)
            nq = rem
            nqp += quo

        if lq > self.last_quantity:
            self.last_quantity += self.last_quantity_per_packet
            self.last_quantity_packet -= 1
        if nq > self.quantity:
            self.quantity += self.quantity_per_packet
            self.quantity_packet -= 1

        ##subtract from product
        self.last_quantity -= lq
        self.last_quantity_packet -= lqp
        self.quantity -= nq
        self.quantity_packet -= nqp
        # self.total_quantity -=()
        self.save()
        ## normailze again
        self.normailze_product()
    def add_to_product(self, lq , lqp, nq, nqp):

        ##add to product
        self.last_quantity += lq
        self.last_quantity_packet += lqp
        self.quantity += nq
        self.quantity_packet += nqp
        # self.total_quantity -=()
        self.save()
        ## normailze again
        self.normailze_product()

## بضائع النقاط المباعة   === bill line
class Point_Product_Sellings(models.Model):
    objects = models.Manager()
    ## cost of buying this materials
    money_quantity_sell = models.FloatField(default = 0)
    money_quantity_buy = models.FloatField(default = 0)

    unit_sell_price = models.FloatField(default = 0)
    discount_per_unit = models.FloatField(default = 0)
    date = models.DateTimeField(default=now)

    quantity_new = models.IntegerField(default = 0)
    quantity_packet_new = models.IntegerField(default = 0)
    total_quantity_new = models.IntegerField(default = 0)
    unit_buy_price_new = models.FloatField(default = 0)

    quantity_old =  models.IntegerField(default = 0)
    quantity_packet_old =  models.IntegerField(default = 0)
    total_quantity_old = models.IntegerField(default = 0)
    unit_buy_price_old = models.FloatField(default = 0)

    ## 0 for sold ,   1 for restored
    line_type = models.IntegerField(default = 0)
    come_from_line_id = models.IntegerField(default = 0)
    taken_status =  models.IntegerField(default = 0)


    ## if restord any amount
    restored_amount =  models.IntegerField(default = 0)
    ## selling cost withot discount
    restored_amount_cost = models.FloatField(default = 0)
    ##restored_amount_cost_discount after discount
    restored_amount_cost_ad = models.FloatField(default = 0)
    ##restored_amount_cost_discount after discount
    restored_amount_cost_buy = models.FloatField(default = 0)

    product = models.ForeignKey('Product', on_delete = models.CASCADE, null = True)
    Point = models.ForeignKey('Point', on_delete = models.CASCADE, null = True)
    bill = models.ForeignKey('Customer_Bill', on_delete = models.CASCADE, null = True)


    def __str__(self):
        # ttp = Total_Point_Product.objects.get(Point = self.Point , product = self.product)
        return self.product.name +  "  --  trader name :-> " + self.Point.name

    @property
    def total_quantity(self):
        return self.total_quantity_old + self.total_quantity_new

    ### in case of restored product amount
    ## need that in many conditions
    @property
    def remaining_quantity(self):
            return self.total_quantity - self.restored_amount
    # @property
    # def remaining_quantity_old(self):
    #         if  self.total_quantity_old > 0:
    #             return self.total_quantity_old - self.restored_amount
    #         else :
    #             return 0
    # @property
    # def remaining_quantity_new(self):
    #         if self.total_quantity_new > 0   :
    #             return self.total_quantity_new - self.restored_amount
    #         else :
    #             return 0

    @property
    def total_quantity_sold(self):
        return self.total_quantity - self.restored_amount


    @property
    def total_discount(self):
        return round( self.total_quantity * self.discount_per_unit, 2)

    @property
    def line_discount(self):
        return self.total_quantity_sold * self.discount_per_unit


    @property
    def total_discount_after_restore(self):
        return round( (self.total_quantity - self.restored_amount) * self.discount_per_unit, 2)

    @property
    def line_net_cost(self):
        return self.money_quantity_sell  - self.restored_amount_cost


    @property
    def required_amount(self):
        return round( self.money_quantity_sell - self.line_discount - self.restored_amount_cost_ad, 2)

class Point_Product_Store_Restore(models.Model):
    objects = models.Manager()
    money_quantity = models.FloatField(default = 0)
    ## not used to avoid errors we calculate points total products units


    date = models.DateTimeField(default=now)

    quantity_new = models.IntegerField(default = 0)
    quantity_packet_new = models.IntegerField(default = 0)
    quantity_old =  models.IntegerField(default = 0)
    quantity_packet_old =  models.IntegerField(default = 0)

    return_status =  models.IntegerField(default = 0)

    product = models.ForeignKey('Product', on_delete = models.CASCADE, null = True)
    Point = models.ForeignKey('Point', on_delete = models.CASCADE, null = True)

    def __str__(self):
        return self.product.name +  "  --  trader name :-> " + self.Point.name

## البضاعة
class Product(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length = 264)

    ##current prices and units per packet
    quantity = models.IntegerField(default = 0)
    quantity_packet = models.IntegerField(default = 0)
    quantity_per_packet = models.IntegerField(default = 0)
    packet_price = models.FloatField(default=0.0)
    unit_buy_price =models.FloatField(default=0.0)
    ##last prices and units per packet
    last_quantity = models.IntegerField(default = 0)
    last_quantity_packet = models.IntegerField(default = 0)
    last_quantity_per_packet = models.IntegerField(default = 0)
    last_packet_price = models.FloatField(default=0.0)
    last_unit_buy_price =models.FloatField(default=0.0)

    total_quantity_unused =  models.IntegerField(default = 0)
    unit_sell_price = models.FloatField(default=0.0)
    descreption = models.TextField(default = "")
    trader = models.ManyToManyField('Trader', through ='Trader_Product',  blank=True)
    # point = models.ManyToManyField('Point', through ='Point_Product', )


    @property
    def total_cost(self):
        total =    ( self.quantity * self.unit_buy_price)  + ( self.quantity_packet * self.packet_price) +\
                ( self.last_quantity * self.last_unit_buy_price)  + ( self.last_quantity_packet * self.last_packet_price)
        return round(total , 2)

    @property
    def total_cost_sell(self):
        return   ( self.total_quantity * self.unit_sell_price)


    @property
    def amount_old(self):
        return (self.last_quantity + (self.last_quantity_packet *self.last_quantity_per_packet ))

    @property
    def amount_new(self):
        return (self.quantity + (self.quantity_packet * self.quantity_per_packet ))

    @property
    def total_quantity(self):
        return self.amount_new + self.amount_old
    def __str__(self):
        return self.name


    def normailze_product(self):
        ## normalize product
        if self.quantity_per_packet :
            quo , rem = divmod(self.quantity , self.quantity_per_packet)
            self.quantity = rem
            self.quantity_packet += quo

        if self.last_quantity_per_packet :
            quo , rem = divmod(self.last_quantity , self.last_quantity_per_packet)
            self.last_quantity = rem
            self.last_quantity_packet += quo

        self.save()


    def subtract_from_product(self, lq , lqp, nq, nqp):
        ##normalize subtracted quantities
        if lq:
            quo, rem = divmod(lq, self.last_quantity_per_packet)
            lq = rem
            lqp += quo
        if nq:
            quo, rem = divmod(nq, self.quantity_per_packet)
            nq = rem
            nqp += quo

        if lq > self.last_quantity:
            self.last_quantity += self.last_quantity_per_packet
            self.last_quantity_packet -= 1
        if nq > self.quantity:
            self.quantity += self.quantity_per_packet
            self.quantity_packet -= 1

        ##subtract from product
        self.last_quantity -= lq
        self.last_quantity_packet -= lqp
        self.quantity -= nq
        self.quantity_packet -= nqp
        # self.total_quantity -=()
        self.save()
        ## normailze again
        self.normailze_product()
    def add_to_product(self, lq , lqp, nq, nqp):

        ##add to product
        self.last_quantity += lq
        self.last_quantity_packet += lqp
        self.quantity += nq
        self.quantity_packet += nqp
        # self.total_quantity -=()
        self.save()
        ## normailze again
        self.normailze_product()


    def calculate_cost(self, lq , lqp, nq, nqp):
        total =    (nq * self.unit_buy_price)  + ( nqp * self.packet_price) + ( lq * self.last_unit_buy_price)  + ( lqp * self.last_packet_price)
        return round(total , 2)


### in case of sellings products in parts of units Not in a complete one
### i.e selling in unit parts of parts
class Sub_Product(models.Model):
    product = models.OneToOneField('Product', on_delete = models.CASCADE)
    measurement_unit = models.ForeignKey('Measurement_Unit', on_delete = models.CASCADE)

    quantity_per_unit = models.IntegerField(default = 0 )
    unit_sell_price = models.FloatField(default = 0 )

    def __str__(self):
        return  " اسم الصنف : " + self.product.name +",  سعر بيع ال " + self.measurement_unit.name +\
                " الواحد ب " + str(self.unit_sell_price * 10 ) +" قرش "



## names of measurement units ie kilogram - gram - liter and so on
class Measurement_Unit(models.Model):
    name = models.CharField(max_length = 64)

    def __str__(self):
        return self.name




## التجار
class Trader(models.Model):
    name = models.CharField(max_length = 264)
    address = models.CharField(max_length = 264)
    phone_number = models.CharField(max_length = 264, default = "")
    date = models.DateTimeField(default=now)

    given_money =models.FloatField(default=0.0)
    total_money = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

    @property
    def remaining_money(self):
        return round(self.total_money - self.given_money)

## trader bills
class Trader_Payment(models.Model):
    amount = models.FloatField(default=0.0)
    date = models.DateTimeField(default=now)
    sender = models.ForeignKey(Current_manager, on_delete = models.CASCADE, null = True)
    reciever = models.ForeignKey('Trader', on_delete = models.CASCADE, null = True)
    notes = models.TextField(default="")
    bill_file = models.FileField(upload_to="upload_to='canteen_bills/%Y/%m/%d'" , null=True)
    discount = models.FloatField(default = 0.0)
    previos_amount = models.FloatField(default = 0.0)
    current_amount = models.FloatField(default = 0.0)
    payment_type = models.IntegerField(default = 0)
    def __str__(self):
        return self.sender.user.first_name +  "  --  trader name :-> " + self.reciever.name + " -- date -> " + str(self.date) + " -- money: " + str(self.amount)



## بضائع التجار bills
class Trader_Product(models.Model):
    objects = models.Manager()
    quantity = models.IntegerField(default = 0)
    quantity_packet = models.IntegerField(default = 0)
    date = models.DateTimeField(default=now)
    total_cost = models.FloatField(default=0.0)
    total_cost_old = models.FloatField(default=0.0)
    given_status = models.IntegerField(default = 0)
    bill_file = models.FileField(upload_to="canteen_bills/%Y/%m/%d" , null=True)
    product = models.ForeignKey(Product, on_delete = models.CASCADE, null = True)
    trader = models.ForeignKey(Trader, on_delete = models.CASCADE, null = True)
    manager = models.ForeignKey(Current_manager, on_delete = models.CASCADE, null = True)
    notes = models.TextField(default="", null=True)
    discount = models.FloatField(default = 0.0)
    def __str__(self):
        if self.product != None:
            return self.product.name +  "  --  trader name :-> " + self.trader.name
        else:
            return self.trader.name

    @property
    def give_cost(self):
        return   ( self.total_cost_old)  - ( self.total_cost) - self.discount



class Trader_Product_Restore(models.Model):
    objects = models.Manager()

    quantity_new = models.IntegerField(default = 0)
    quantity_packet_new = models.IntegerField(default = 0)
    unit_buy_price_new = models.FloatField(default= 0.0)

    quantity_old = models.IntegerField(default = 0)
    quantity_packet_old = models.IntegerField(default = 0)
    unit_buy_price_old = models.FloatField(default= 0.0)

    total_quantity_pieces = models.IntegerField(default = 0)

    date = models.DateTimeField(default=now)
    total_cost = models.FloatField(default=0.0)
    given_status = models.IntegerField(default = 0)
    bill_file = models.FileField(upload_to="canteen_bills/%Y/%m/%d" , null=True)

    ## new fields related to restored bills
    given_amount = models.FloatField(default=0.0)
    discount = models.FloatField(default=0.0)
    paid_status = models.FloatField(default=0.0)
    product = models.ForeignKey(Product, on_delete = models.CASCADE, null = True)
    trader = models.ForeignKey(Trader, on_delete = models.CASCADE, null = True)
    manager = models.ForeignKey(Current_manager, on_delete = models.CASCADE, null = True)

    def __str__(self):
        return self.product.name +  "  --  trader name :-> " + self.trader.name


    @property
    def remaining_amount(self):
        return round( self.total_cost - self.given_amount - self.discount )

### الحسابات اليومية
class Day_Payment_Line(models.Model):
    objects = models.Manager()
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    sold_quantity = models.IntegerField(default = 0)
    sold_quantity_packet = models.IntegerField(default = 0)
    total_cost = models.FloatField(default=0.0)
    total_payment = models.FloatField(default=0.0)
    profit = models.FloatField(default=0.0)
    day = models.DateField(default = now)

    def __str__(self):
        return self.product.name +  "  -- amount :-> " + str(self.sold_quantity) +  "  -- date :-> " + str(self.day)







### التراكم اليومى للتوريدات والمبيعات
class Acumulate_payment(models.Model):
    objects = models.Manager()
    date =  models.DateField(default = now)
    # end_date =  models.DateField(default = now)
    ## اجمالى المبيعات حتى اليوم
    payment_until_now =models.FloatField(default=0.0)
    ## اجمالى توريدات الخزينة تى اليوم
    comings_until_now =models.FloatField(default=0.0)
    ## الوارد اليومى
    comings_today = models.FloatField(default=0.0)
    ## سعر البضاعة المرحلة للليوم التالى
    next_day_goods_price = models.FloatField(default=0.0)

    total_profit_until_now = models.FloatField(default=0.0)

    def __str__(self):
        return  "  -- date :-> " + str(self.date)



### بيانات الخزنة
class Safe_data(models.Model):
    objects = models.Manager()
    day =  models.DateTimeField(default = now)
    money_amount = models.FloatField(default=0.0)
    given_person = models.ForeignKey(Current_manager, on_delete = models.CASCADE, null = True)
    notes = models.TextField(default = "")
    ### status takes values fom 1 - 6
    ### 1- withdraw money    2- point_product_bill  3. trader_products_bill  4. sandwiches cost
    ## 5. sandwich sellings    6. generics ,   7. customer payment   8. trader payment
    safe_line_status = models.IntegerField(default = 0)
    def __str__(self):
        return self.notes


## safe montly
class Safe_Month(models.Model):
    name = models.CharField(max_length = 264 , default="")
    money = models.FloatField(default= 0.0)

    def __str__(self):
        return self.name

## النثريات
class withdrawings(models.Model):

    descreption =  models.TextField(default = "")
    day =  models.DateTimeField(default = now)
    money_amount =models.FloatField(default=0.0)
    ## 1. store product
    ##2. safe money withdraw
    status = models.IntegerField(default = 0)

    def __str__(self):
        return self.descreption




## month Total Calculations
class Month_Total_Calculation(models.Model):
    start_date = models.DateField(default = now)
    end_date = models.DateField(default = now)
    canteen_base = models.FloatField(default=0.0)
    traders_depts = models.FloatField(default=0.0)
    # store products
    total_products_money = models.FloatField(default=0.0)
    total_products_money_points = models.FloatField(default=0.0)
    next_manager_gmoney = models.FloatField(default=0.0)
    total_withdrawings = models.FloatField(default=0.0)
    safe_current_money = models.FloatField(default=0.0)
    total_profit = models.FloatField(default=0.0)
    total_profit_sandwiches = models.FloatField(default=0.0)
    manager = models.ForeignKey(Current_manager, on_delete = models.CASCADE, null = True)

    def __str__(self):
        return str(self.start_date) +" -- " +str(self.end_date)

    @property
    def difference_depts_manteka(self):
        diff =  (self.total_products_money + self.total_products_money_points + self.total_withdrawings + self.safe_current_money) - (self.traders_depts)

        return round(diff, 2)
    @property
    def customers_depts(self):
        customers = Customer.objects.all()
        depts = sum(c.remaining_money for c in customers)
        return round(depts, 2)
## بضائع التجار  realtion between product and trader
class Trader_Product_Data(models.Model):
    objects = models.Manager()
    price_per_packet = models.IntegerField(default = 0)
    product = models.ForeignKey(Product, on_delete = models.CASCADE, null = True)
    trader = models.ForeignKey(Trader, on_delete = models.CASCADE, null = True)
    def __str__(self):
        return self.product.name +  "  --  trader name :-> " + self.trader.name






##################### define models for the sandwich itself

## اسماء السنتدوتشات
class Sandwich(models.Model):
    objects = models.Manager()
    # name = models.CharField(default="", max_length=64)
    sandwich_type = models.ForeignKey('Sandwich_Type' , on_delete = models.SET_NULL, null =True)
    katchab = models.ForeignKey('Katchab' , on_delete = models.SET_NULL, null =True)
    bread = models.ForeignKey('Bread_Type' , on_delete = models.SET_NULL, null =True)
    packet = models.ForeignKey('Packet' , on_delete = models.SET_NULL, null =True)
    unit_sell_price = models.FloatField(default = 0.0)

    @property
    def unit_cost_price(self):
        stup = kup = bup = pup = 0
        if self.sandwich_type != None:
            stup = self.sandwich_type.old_unit_buy_price if self.sandwich_type.amount_old != 0 else self.sandwich_type.new_unit_buy_price

        if self.katchab != None:
            kup = self.katchab.old_unit_buy_price if self.katchab.amount_old != 0 else self.katchab.new_unit_buy_price

        if self.bread != None:
            bup = self.bread.old_unit_buy_price if self.bread.amount_old != 0 else self.bread.new_unit_buy_price

        if self.packet != None:
            pup = self.packet.old_unit_buy_price if self.packet.amount_old != 0 else self.packet.new_unit_buy_price

        return  round(( stup + kup + bup + pup) , 3)




    def __str__(self):
        if self.sandwich_type != None:
            return self.sandwich_type.name

## السنتدوتشات اليومية
class DaySandwich(models.Model):
    objects = models.Manager()
    number = models.IntegerField()
    total_cost = models.FloatField(default=0.0)
    total_return = models.FloatField(default=0.0)
    profit = models.FloatField(default=0.0)
    date = models.DateTimeField(default = now)
    sandwich = models.ForeignKey('Sandwich' , on_delete = models.SET_NULL, null =True)


    def __str__(self):
        return  self.sandwich.sandwich_type.name + " -- " + str(self.number) +" -- date: " +str(self.date)



### 1. bread type
class Bread_Type(models.Model):
    name = models.CharField(max_length = 264)


    new_packet_cost = models.IntegerField(default = 0.0)
    new_quantity_per_packet = models.IntegerField(default = 0.0)
    new_unit_buy_price = models.FloatField(default = 0)


    old_packet_cost = models.IntegerField(default = 0.0)
    old_quantity_per_packet = models.IntegerField(default = 0.0)
    old_unit_buy_price = models.FloatField(default = 0)
    amount_new = models.IntegerField(default=0)
    amount_old = models.IntegerField(default=0)


    @property
    def total_cost(self):
        if self.total_quantity > 0:
            return   ( self.amount_new * self.new_unit_buy_price)  +  ( self.amount_old * self.old_unit_buy_price)
        else:
            return 0


    @property
    def total_quantity(self):
        return  self.amount_old + self.amount_new

    def subtract(self, amount):
        r = 0
        ## check enough amount :
        if self.total_quantity >= amount :
            if self.amount_old >= amount:
                self.amount_old -= amount
                amount = 0
            elif self.amount_old != 0 :
                self.amount_old -=0
                amount = amount-r
            else:
                self.amount_new -= amount
                amount = 0
            if amount !=0 :
                self.amount_new -= amount
            self.save()

            return True
        else :
            return False

    def __str__(self):
        return self.name



### 2. packet type
class Packet(models.Model):
    name = models.CharField(max_length = 264)

    new_packet_cost = models.IntegerField(default = 0.0)
    new_quantity_per_packet = models.IntegerField(default = 0.0)
    new_unit_buy_price = models.FloatField(default = 0)


    old_packet_cost = models.IntegerField(default = 0.0)
    old_quantity_per_packet = models.IntegerField(default = 0.0)
    old_unit_buy_price = models.FloatField(default = 0)
    amount_new = models.IntegerField(default=0)
    amount_old = models.IntegerField(default=0)


    @property
    def total_cost(self):
        if self.total_quantity > 0:
            return   ( self.amount_new * self.new_unit_buy_price)  +  ( self.amount_old * self.old_unit_buy_price)
        else:
            return 0



    @property
    def total_quantity(self):
        return  self.amount_old + self.amount_new

    def subtract(self, amount):
        r = 0
        if self.total_quantity >= amount :
            if self.amount_old >= amount:
                self.amount_old -= amount
                amount = 0
            elif self.amount_old != 0 :
                self.amount_old -=0
                amount = amount-r
            else:
                self.amount_new -= amount
                amount = 0
            if amount !=0 :
                self.amount_new -= amount
            self.save()

            ##success
            return True
        else:
            return False

    def __str__(self):
        return self.name


### 3. sandwich type -  name
class Sandwich_Type(models.Model):
    name = models.CharField(max_length = 264)

    new_packet_cost = models.IntegerField(default = 0.0)
    new_quantity_per_packet = models.IntegerField(default = 0.0)
    new_unit_buy_price = models.FloatField(default = 0)


    old_packet_cost = models.IntegerField(default = 0.0)
    old_quantity_per_packet = models.IntegerField(default = 0.0)
    old_unit_buy_price = models.FloatField(default = 0)
    amount_new = models.IntegerField(default=0)
    amount_old = models.IntegerField(default=0)


    @property
    def total_cost(self):
        if self.total_quantity > 0:
            return   ( self.amount_new * self.new_unit_buy_price)  +  ( self.amount_old * self.old_unit_buy_price)
        else:
            return 0



    @property
    def total_quantity(self):
        return  self.amount_old + self.amount_new

    def subtract(self, amount):
        r = 0
        ## check enough amount :
        if self.total_quantity >= amount :
            if self.amount_old >= amount:
                self.amount_old -= amount
                amount = 0
            elif self.amount_old != 0 :
                self.amount_old -=0
                amount = amount-r
            else:
                self.amount_new -= amount
                amount = 0
            if amount !=0 :
                self.amount_new -= amount
            self.save()
            return True
        else :
            return False


    def __str__(self):

        return self.name


### 4. katchab type
class Katchab(models.Model):
    name = models.CharField(max_length = 264)

    new_packet_cost = models.IntegerField(default = 0.0)
    new_quantity_per_packet = models.IntegerField(default = 0.0)
    new_unit_buy_price = models.FloatField(default = 0)


    old_packet_cost = models.IntegerField(default = 0.0)
    old_quantity_per_packet = models.IntegerField(default = 0.0)
    old_unit_buy_price = models.FloatField(default = 0)
    amount_new = models.IntegerField(default=0)
    amount_old = models.IntegerField(default=0)


    @property
    def total_cost(self):
        if self.total_quantity > 0:
            return   ( self.amount_new * self.new_unit_buy_price)  +  ( self.amount_old * self.old_unit_buy_price)
        else:
            return 0



    @property
    def total_quantity(self):
        return  self.amount_old + self.amount_new



    def subtract(self, amount):
        r = 0
        ## check enough amount :
        if self.total_quantity >= amount :
            if self.amount_old >= amount:
                self.amount_old -= amount
                amount = 0
            elif self.amount_old != 0 :
                self.amount_old -=0
                amount = amount-r
            else:
                self.amount_new -= amount
                amount = 0
            if amount !=0 :
                self.amount_new -= amount
            self.save()
            return True
        else :
            return False

    def __str__(self):
        return self.name









#############################################################
### customers tables
############################################################

### first

## التجار
class Customer(models.Model):
    name = models.CharField(max_length = 264)
    address = models.CharField(max_length = 264)
    phone_number = models.CharField(max_length = 264, default = "")
    date = models.DateTimeField(default=now)

    given_money =models.FloatField(default=0.0)
    total_money = models.FloatField(default=0.0)

    @property
    def remaining_money(self):
        return  round(self.total_money - self.given_money , 2 )


    def normalize(self):
        self.given_money = round(    self.given_money , 2)
        self.total_money = round(    self.total_money , 2)
        self.save()




    def __str__(self):
        return self.name


class Customer_Bill(models.Model):
    date = models.DateTimeField(default=now)
    given_status = models.IntegerField(default = 0)
    paid_status = models.IntegerField(default = 0)
    ## 0 for sold ,   1 for restored
    bill_type = models.IntegerField(default = 0)
    customer  = models.ForeignKey('Customer', on_delete = models.SET_NULL, null = True)
    manager  = models.ForeignKey('Current_manager', on_delete = models.SET_NULL, null = True)
    given_amount = models.FloatField(default=0.0)
    ## if we give customer more discounts in the upcoming bills
    discount = models.FloatField(default=0.0)


    @property
    def total_bill_cost(self):
        bill_lines = self.all_lines
        total_bill_cost = round( sum(b.money_quantity_sell for b in bill_lines), 2)
        return total_bill_cost

    ## bill cost without any discount
    @property
    def total_bill_cost_ar(self):
        return round(self.total_bill_cost - self.restored_amount_cost , 1)


    @property
    def remaining_amount(self):
        return self.required_amount -  self.given_amount

    @property
    def total_discount(self):
        return     self.main_discount + self.discount

    ## disount for the sold amount only =>   total_sold - total_restored
    @property
    def main_discount(self):
        bill_lines = self.all_lines
        total_discount =  round( sum( (b.total_discount_after_restore  for b in bill_lines ) ) , 2)
        return total_discount

    ## bill cost without with all discounts
    @property
    def required_amount(self):
        return self.total_bill_cost -  self.total_discount - self.restored_amount_cost


    @property
    def restored_amount_cost_ad(self):
        bill_lines = self.all_lines
        total = round( sum(b.restored_amount_cost_ad for b in bill_lines ), 2)
        return  total


    @property
    def restored_amount_cost(self):
        bill_lines = self.all_lines
        total = round( sum(b.restored_amount_cost for b in bill_lines ), 2)
        return  total


    @property
    def all_lines(self):
        bill_lines = Point_Product_Sellings.objects.filter(bill = self.id)
        return bill_lines

    @property
    def point(self):
        bill_line = Point_Product_Sellings.objects.filter(bill = self.id).first()
        try:
            return bill_line.Point
        except:
            return None



    def __str__(self):
        return  "   فاتورة رقم :  " +  str(self.id) + " ---- " + "  اسم العميل :  " +  self.customer.name




## فواتير العملاء
class Customer_Payment(models.Model):
    g_user = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True)
    t_user = models.ForeignKey('Current_manager', on_delete=models.SET_NULL , null=True)
    date = models.DateTimeField(default = now)
    amount= models.FloatField(default=0.0)
    previos_amount= models.FloatField(default=0.0)
    current_amount= models.FloatField(default=0.0)
    discount= models.FloatField(default=0.0)
    ## 0 from customer to company
    ## 1 opposite to 0
    payment_type  =  models.IntegerField(default = 0)

    def __str__(self):
        try :
            return self.g_user.name + " مدفوعة ل  " + self.t_user.user.first_name
        except :
            return "  "

##################################################################################################
