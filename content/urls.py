from django.urls import path
from .import views

app_name="content"


urlpatterns = [
    path('', views.home, name='login-page'),
    path('logout/', views.logout_view, name='logout-page'),
    path('login/', views.home, name='login-page'),
    path('change-password/', views.change_password, name='change-password'),
    path('search-canteen/', views.search_canteen, name='search-canteen'),

    path('store/', views.store, name='store'),
    # path('sandwitch/<int:sandwich_id>/', views.sandwitch, name='sandwitch'),
    path('sandwitch/', views.sandwitch, name='sandwitch'),
    path('add_sandwich_components/<int:type_id>', views.add_sandwich_components, name='add_sandwich_components'),
    path('add_sandwich_component_names/', views.add_sandwich_component_names, name='add_sandwich_component_names'),
    path('sand_current_materials/', views.sand_current_materials, name='sand_current_materials'),

    path('daily_transaction/', views.daily_transaction, name='daily_transaction'),
    path('Treasury_receipt/', views.Treasury_receipt, name='Treasury_receipt'),
    path('receipt_net/', views.receipt_net, name='receipt_net'),
    path('monthly_receipt/', views.monthly_receipt, name='monthly_receipt'),
    path('Debts/', views.Debts, name='Debts'),

    path('add_sandwitch/', views.add_sandwitch, name='add_sandwitch'),
    path('add_new_sandwitch/', views.add_new_sandwitch, name='add_new_sandwitch'),

    path('new_product_type/', views.new_product_type, name='new_product_type'),
    path('add_new_mu/', views.add_new_mu, name='add_new_mu'),
    path('delete_mu/', views.delete_mu, name='delete_mu'),
    path('reduce_product_amount_store/<int:product_id>', views.reduce_product_amount_store, name='reduce_product_amount_store'),
    path('update_product/<int:trader_id>', views.update_product, name='update_product'),
    path('withdrawings_all/', views.withdrawings_all, name='withdrawings_all'),
    path('add_new_sellings/', views.add_new_sellings, name='add_new_sellings'),
    path('trader_page/<int:trader_id>', views.trader_page, name='trader_page'),
    path('add_money_dept/<int:trader_id>', views.add_money_dept, name='add_money_dept'),
    path('restore_trader_product_store/<int:trader_id>', views.restore_trader_product_store, name='restore_trader_product_store'),



    path('product_page/<int:product_id>', views.product_page, name='product_page'),
    path('update_product_prices/<int:product_id>', views.update_product_prices, name='update_product_prices'),
    path('give_payment/<int:trader_id>', views.give_payment, name='give_payment'),
    path('restore_trader_given_bill/<int:trader_id>', views.restore_trader_given_bill, name='restore_trader_given_bill'),
    path('add_trader/<int:status>', views.add_trader, name='add_trader'),


    path('customers-page/', views.customers_page, name='customers-page'),
    path('customer-payment/<int:customer_id>', views.customer_payment, name='customer-payment'),
    path('customer-page/<int:customer_id>', views.customer_page, name='customer-page'),
    path('customer-bill-details/<int:bill_id>', views.customer_bill_details, name='customer-bill-details'),
    path('customers-bill-details-page/', views.customer_bill_details_page, name='customers-bill-details-page'),
    path('restore-customer-bill/<int:customer_id>', views.restore_customer_bill, name='restore-customer-bill'),
    path('confirm-restore-customer-bill/<int:customer_id>', views.confirm_restore_customer_bill, name='confirm-restore-customer-bill'),
    path('restore-customer-bill-line/<int:line_id>', views.restore_customer_bill_line, name='restore-customer-bill-line'),
    path('delete-restored-customer-bill-line/<int:line_id>', views.delete_restored_customer_bill_line, name='delete-restored-customer-bill-line'),
    path('customer_give_payment/<int:customer_id>', views.customer_give_payment, name='customer_give_payment'),
    path('customer_all_unpaid_bills/<int:customer_id>', views.customer_all_unpaid_bills, name='customer_all_unpaid_bills'),

    path('treasury_transactions/', views.treasury_transactions, name='treasury_transactions'),
    path('withdrawings_transactions/', views.withdrawings_transactions, name='withdrawings_transactions'),
    path('delete_single_withdrawing/', views.delete_single_withdrawing, name='delete_single_withdrawing'),


    path('points/', views.points, name='points'),
    path('point_page/<int:point_id>', views.point_page, name='point_page'),
    path('point_trader_page/<int:point_trader_id>', views.point_trader_page, name='point_trader_page'),
    path('add_new_point_bill/<int:product_id>', views.add_new_point_bill, name='add_new_point_bill'),
    path('add_new_point_seller/', views.add_new_point_seller, name='add_new_point_seller'),
    path('add_new_point_payments/<int:point_id>', views.add_new_point_payments, name='add_new_point_payments'),
    path('add_new_point_sellings/<int:point_id>', views.add_new_point_sellings, name='add_new_point_sellings'),
    path('restore_point_bill_sell/<int:bill_id>', views.restore_point_bill_sell, name='restore_point_bill_sell'),
    path('restore_point_product_store/<int:point_id>', views.restore_point_product_store, name='restore_point_product_store'),
    path('point_to_point_product/<int:point_id>', views.point_to_point_product, name='point_to_point_product'),
    path('point-total-product/<int:tpp>', views.point_total_product, name='point-total-product'),
    path('all-discount-bills/', views.all_discount_bills, name='all-discount-bills'),


    path('manager/<int:manager_id>', views.manager, name='manager'),
    path('daily_reports', views.daily_reports, name='daily_reports'),
    path('denied/', views.denied, name='denied_page'),
    # path('all_types/', views.all_types, name='all_types'),
]
