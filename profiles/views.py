from django.shortcuts import render,redirect
from profiles.models import *
import random
from datetime import date,datetime
from django.http import HttpResponse

cur_customer = None

# Create your views here.
def randomGen():
    return int(random.uniform(100000, 999999))

class Account:
    def __init__(self, account_details):
        self.account_no = account_details.Account_no 
        print("self.account_no:", self.account_no)
        self.account_details = account_details
        print("self.account_details:", self.account_details)
        self.transac = {}

        transaction_list = Transactions.objects.filter(Account_no = account_details)
        print("trans list:",transaction_list)
        for trans in transaction_list:
            self.transac[trans.T_ID] = Transaction(trans)

    def create_transaction(self,amt,type):
        new_trans = New_Transaction(self,date.today(),datetime.now(),amt,type)

    def get_transaction_log(self):
        for tr in self.transac:
            self.transac[tr].display()
        return self.transac

class New_Account(Account):
    def __init__(self,coustomer_obj):
         new_acc = Account_data()
         new_acc.Account_no = randomGen()
         new_acc.Balance = 0
         new_acc.owner = coustomer_obj.customer_data
         new_acc.save()
         super().__init__(new_acc)

class Login_Details:
    def __init__(self, user, passwd):
        self.username = user
        self.password = passwd  

    def get_customer(self):
        customer_data = Customer_Data.objects.get(Name = self.username)
        return customer #None returned if customer is new, not in DB yet
        
  
#For existing customer        
class Customer:
    def __init__(self, log_in_obj):
        self.customer_data = Customer_data.objects.get(Name = log_in_obj.username)
        self.login_credentials = log_in_obj
        #Take other details from DB
        self.accounts = {}
        account_data_list = Account_data.objects.filter(owner=self.customer_data)
        print(account_data_list)
        for account_data in account_data_list:
            self.accounts[account_data.Account_no] = Account(account_data)
        
    def create_account(self):
        new_account = New_Account(self)
        #Adding new account to dictionary of accounts owned by customer
        self.accounts[new_account.account_no] = new_account
        
    def close_account(self, accno):
        del_account = self.accounts[accno]
        del_account.account_details.delete()
        del self.accounts[accno]
        
                
            
        
class New_Customer(Customer):
    def __init__(self, log_in_obj, name, phone_no, email):
        #Insert details to DB
        cust_user=Customer_data()
        cust_user.Name = name
        cust_user.Phone_no = phone_no
        cust_user.Email = email
        cust_user.save()
        super().__init__(log_in_obj)
    
        
class Transaction:
    def __init__(self, trans_data):
        #Read existing transaction details from DB
        self.trans_id=trans_data.T_ID
        self.trans_details=trans_data
        
    def display(self):
        #Display transaction details

        print("self.trans_id: ",self.trans_id)
        print("self.trans_details: ",self.trans_details.Type)
   
  
        
class New_Transaction(Transaction):
    def __init__(self, account_obj, date, time, amount, tran_type):  
        #trans_id will be got by auto-increment  
        trans_details=Transactions()
        trans_details.Amount=amount
        trans_details.Type=tran_type
        trans_details.Account_no=account_obj.account_details
        trans_details.save()
        super().__init__(trans_details)

cur_customer = None

def display_menu(request):
    global cur_customer
    user_log_in = Login_Details(request.user.username, request.user.password)
    cust_details = Customer_data.objects.filter(Name = user_log_in.username)
    print("cust_details:", cust_details)
    if(cust_details):
        print("Existing Customer")
        customer = Customer(user_log_in)
        print("customer obj :", customer)
    else:
        print("making new customer")
        customer = New_Customer(user_log_in, user_log_in.username, '8888888' , 'gobinda@gmail.com') 
    print("Customer name :", customer.customer_data.Name)
    cur_customer = customer
    return render(request, 'user_account.html')
    {'customer':customer}

def account_management(request):
    accounts = cur_customer.accounts
    user_accnos = list(accounts.keys())
    print("user_accnos", user_accnos)
    return render(request, 'account_details.html', 
    {'customer':cur_customer, 'accounts':accounts, 'can_close_accnos':user_accnos})


def withdraw(request):
    accounts = cur_customer.accounts
    msg="<br>Enter a valid account no. and also check for your balance!</p><br>"
    if request.method == "POST":
        acc_num=int(request.POST.get('acc_no'))
        amount=int(request.POST.get('amount'))
        print('requestPOST=',acc_num,type(acc_num))
        #print('account dict:',accounts.keys())
        if acc_num in accounts:
            #acc_obj= accounts[acc_num]
            acc_q=Account_data.objects.get(Account_no=acc_num)
            balance=acc_q.Balance
            print("balance:",balance)
            if(balance >= amount):
                trans=Account(acc_q)
                trans.create_transaction(amount,"withdraw")
                balance-=amount
                acc_q.Balance=balance
                print("balance:",acc_q.Balance)
                acc_q.save()
                cur_customer.accounts[acc_num].account_details.Balance-=amount
                msg="<td>Withdrawn Successfully!</td><br>"
            else:
                msg="<td>Not sufficient balance!</td><br>"
            
        else:
            msg="<p>Invalid account number</p><br>"
    return render(request, 'withdraw.html',{'customer':cur_customer, 'accounts':accounts,'msg':msg})
    #'customer':cur_customer, 'accounts':accounts

def deposit(request):
    accounts = cur_customer.accounts
    msg="<br>Enter a valid account number!</p><br>"
    if request.method == "POST":
        acc_num=int(request.POST.get('acc_no'))
        amount=int(request.POST.get('amount'))
        print('requestPOST=',acc_num,type(acc_num))
        if acc_num in accounts:
            acc_q=Account_data.objects.get(Account_no=acc_num)
            balance=acc_q.Balance
            print("balance:",balance)
            trans=Account(acc_q)
            trans.create_transaction(amount,"deposit")
            balance+=amount
            acc_q.Balance=balance
            print("balance:",acc_q.Balance)
            acc_q.save()
            cur_customer.accounts[acc_num].account_details.Balance+=amount
            msg="<td>Deposited Successfully!</td><br>"
        else:
            msg="<p>Invalid account number</p><br>"
    return render(request, 'deposit.html',{'customer':cur_customer, 'accounts':accounts,'msg':msg})

def stat_gen(request):
    accounts = cur_customer.accounts
    print(accounts)
    msg=""
    all_transactions = {}
    for acc in accounts:
        print("acc_no:",acc)
        acc_q=Account_data.objects.get(Account_no=int(acc))
        trans=Account(acc_q)
        transaction=trans.get_transaction_log()
        trans_objs_list = list(transaction.values())
        all_transactions[acc] = all_transactions.get(acc, [])+trans_objs_list
        print("trans:",transaction)
    return render(request, 'stat_gen.html',{'customer':cur_customer, 'accounts':accounts, 'transaction':all_transactions,'msg':msg})

def get_transaction_action(request):
    accounts = cur_customer.accounts
    print("got:", request.GET)
    msg="filter"
    button_action = request.GET['account_action']
    all_transactions = {}
    if(button_action == 'withdraw'):
        for acc in accounts:
            transaction=Transactions.objects.filter(Account_no_id=int(acc),Type="withdraw")
            print("withdraw:",transaction)
            all_transactions[acc] = list(transaction)
    elif(button_action == 'deposit'):
        for acc in accounts:
            transaction=Transactions.objects.filter(Account_no_id=int(acc),Type="deposit")
            all_transactions[acc] = list(transaction)
    elif(button_action == 'all'):
        return redirect('profiles:stat_gen')
    print("all_trans:", all_transactions)
    return render(request,'stat_gen.html',{'customer':cur_customer, 'accounts':accounts, 'transaction':all_transactions,'msg':msg});

def get_function_chosen(request):
    print(request.GET) 
    #print("Got menu") 
    menu_chosen = request.GET['function_chosen']
    if(menu_chosen=='view_accounts'):
        return redirect('profiles:account_management') #name of view given in urls.py
    elif(menu_chosen=='withdraw'):
        return redirect('profiles:withdraw') #name of view given in urls.py
    elif(menu_chosen=='deposit'):
        return redirect('profiles:deposit') #name of view given in urls.py
    elif(menu_chosen=='stat_gen'):
        return redirect('profiles:stat_gen') #name of view given in urls.py
   
    
def get_account_action(request):
    print("got:", request.GET)
    account_action = request.GET['account_action']
    if(account_action == 'create'):
       cur_customer.create_account()
    elif(account_action == 'close'):
        print(request.GET)
        print("account:", cur_customer.accounts)
        close_accno = int(request.GET['close_accno'])
        cur_customer.close_account(close_accno)
    else:
        print("Got neither create nor close")
    return redirect('profiles:account_management')    

def create(request):
    a = cur_customer.create_account()
    return a, redirect('profiles:account_management')