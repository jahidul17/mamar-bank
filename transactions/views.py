from django.shortcuts import render
from django.views.generic import CreateView,ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositForm,WithdrawForm,LoanRequestForm,SendMoneyForm
from .constants import DEPOSIT,WITHDRAWAL,LOAN,LOAN_PAID,SEND_MONEY,RECEIVE_MONEY
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum  
from django.views import View
from django.shortcuts import get_object_or_404,redirect
from django.urls import reverse_lazy

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from accounts.models import UserBankAccount

# Create your views here.
# ei view ke inherit kore amrea deposite,withdraw,loan request er kaj korbo.

def send_transaction_mail(user,amount,subject,template):
        message=render_to_string(template,{
            'user': user,
            'amount': amount,
        })
        
        send_email=EmailMultiAlternatives(subject,'',to=[user.email])
        send_email.attach_alternative(message,"text/html")
        send_email.send()


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name='transactions/transaction_form.html'
    model=Transaction
    title=''
    success_url=reverse_lazy('transaction_report')
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs
         

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # template e context data pass kora
        context.update({
            'title': self.title
        })

        return context



class DepositMoneyView(TransactionCreateMixin):
    form_class=DepositForm
    title="Deposit"
    
    #By default set value in backend when user visit Deposit form
    def get_initial(self):
        initial={'transaction_type':DEPOSIT}
        return initial
    
    # Is form valid like request.POST method if form valid
    def form_valid(self, form):
        amount=form.cleaned_data.get('amount')
        account=self.request.user.account
        account.balance += amount #user er kache 500 taka, ami doposit korlam 1000. total balance 1500tk.
        account.save(
            update_fields=['balance']
        )
        messages.success(self.request,f"{amount} $ was deposited to your account successfully. ")
        send_transaction_mail(self.request.user,amount,"Deposit Message","transactions/deposite_email.html")
        return super().form_valid(form)
    
    
    
class WithdrawMoneyView(TransactionCreateMixin):
    form_class=WithdrawForm
    title="Withdraw Money"
    
    #By default set value in backend when user visit Deposit form
    def get_initial(self):
        initial={'transaction_type':WITHDRAWAL}
        return initial
    
    # Is form valid like request.POST method if form valid
    def form_valid(self, form):
        amount=form.cleaned_data.get('amount')
        account=self.request.user.account
        account.balance -= amount #user er kache 1500 taka, ami withdrewl korlam 1000. total balance 500tk.
        account.save(
            update_fields=['balance']
        )
        messages.success(self.request,f"Successfully withdraw {amount} $ form your account. ")
        
        send_transaction_mail(self.request.user,amount,"Withdrawl Message","transactions/withdrawl_email.html")
        return super().form_valid(form)
    
    
    
class LoanRequestView(TransactionCreateMixin):
    form_class=LoanRequestForm
    title="Request for loan"
    
    #By default set value in backend when user visit Deposit form
    def get_initial(self):
        initial={'transaction_type':LOAN}
        return initial
    
    # Is form valid like request.POST method if form valid
    def form_valid(self, form):
        amount=form.cleaned_data.get('amount')
        current_loan_count=Transaction.objects.filter(account=self.request.user.account,transaction_type=3,loan_approve=True).count() 
        #transaction_type=3 means loan field form constants
        if current_loan_count>=3:
            return HttpResponse("You have crossed your limits.")
    
        messages.success(self.request,f"Loan request for amount {amount} $ has been successfully sent to admin. ")
        
        send_transaction_mail(self.request.user,amount,"Loan Message","transactions/loan_email.html")
        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin,ListView):
    template_name="transactions/transaction_report.html"
    model=Transaction
    balance=0
    context_object_name="report_list"
    
    def get_queryset(self):
        #jodi user kono type filter na kora taile tar total transaction report dekhabo.
        queryset=super().get_queryset().filter(
            # account=self.request.user.account
            account=self.request.user.account
        )
        start_date_str=self.request.GET.get('start_date')
        end_date_str=self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date=datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date=datetime.strptime(end_date_str, "%Y-%m-%d").date()

            queryset=queryset.filter(timestamp__date__gte =start_date,timestamp__date__lte=end_date)
            #here timestamp is variable form model then date and then gte menas greaterthan, lte means lessthan
       
            self.balance=Transaction.objects.filter(timestamp__date__gte =start_date,timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
            
        else: 
            self.balance=self.request.user.account.balance
                   
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context.update({
            'account':self.request.user.account
        })
        return context
    

class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        print(loan)
        if loan.loan_approve:
            user_account = loan.account
                # Reduce the loan amount from the user's balance
                # 5000, 500 + 5000 = 5500
                # balance = 3000, loan = 5000
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(self.request,f'Loan amount is greater than available balance')

        return redirect('loan_list')



class LoanListView(LoginRequiredMixin,ListView):
    model=Transaction
    template_name="transactions/loan_request.html"
    context_object_name="loans"
    
    def get_queryset(self):
        user_account=self.request.user.account
        queryset=Transaction.objects.filter(account=user_account,transaction_type=LOAN)
        return queryset




class SendMoneyView(TransactionCreateMixin):
    title = "Send money"
    form_class = SendMoneyForm
    template_name = 'transactions/send_money.html'

    def get_initial(self):
        initial = {
            'transaction_type': SEND_MONEY
        }
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        account_no = form.cleaned_data['account_no']

        receiver_account = UserBankAccount.objects.get(account_no=account_no)
        receiver_account.balance += amount
        send_transaction_mail(self.request.user,amount,"Receive Money Message","transactions/receive_money_email.html")
        receiver_account.save(update_fields=['balance'])

        receiver_transaction = Transaction(
            amount=amount, transaction_type=RECEIVE_MONEY, account=receiver_account, balance_after_transaction=receiver_account.balance)
        receiver_transaction.save()

        sender_account = self.request.user.account
        sender_account.balance -= amount
        send_transaction_mail(self.request.user,amount,"Send Money Message","transactions/send_money_email.html")
        sender_account.save(update_fields=['balance'])

        messages.success(self.request, f"""{
                         amount} has been sent to Account:  {account_no}""")
        return super().form_valid(form)
    
    
     