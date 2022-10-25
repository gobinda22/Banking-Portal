from django.conf.urls import url
from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path(r"dashboard", views.display_menu, name = "dashboard"),
    path(r'redirect_from_dashboard',views.get_function_chosen, name="get_fuction_chosen"),
    path(r"account_management", views.account_management, name='account_management'),
    path(r"withdraw", views.withdraw, name='withdraw'),
    path(r"deposit", views.deposit, name='deposit'),
    path(r"process_account_action", views.get_account_action, name='get_account_action'),
    path(r"account_number",views.create,name='account_number'),
    path(r"stat_gen", views.stat_gen, name='stat_gen'),
    path(r"get_stat_gen", views.get_transaction_action, name='get_transaction_action'),
]
