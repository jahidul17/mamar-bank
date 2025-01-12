from django import forms
from .models import Transaction
from accounts.models import UserBankAccount

class TransactionForm(forms.ModelForm):
    class Meta:
        model=Transaction
        fields=['amount','transaction_type']
        
    def __init__(self,*args,**kwargs):
        self.account=kwargs.pop('account') #pop and get are same. account er value k pop kore anlam.
        super().__init__(*args,**kwargs)
        self.fields['transaction_type'].disabled=True #ei field disable thakbe
        self.fields['transaction_type'].widget=forms.HiddenInput()  #user er theke hide kora thakbe
        
    def save(self,commit=True):
        self.instance.account=self.account
        self.instance.balance_after_transaction=self.account.balance #0-----> 5000
        return super().save()
    

class DepositForm(TransactionForm):
    def clean_amount(self): #amount field ke filter korbo
        min_deposit_amount=100
        amount=self.cleaned_data.get('amount') #user err fill up kora form theke amra amount field er value ke niye aslam
        if amount<min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )
        return amount
    
    
class WithdrawForm(TransactionForm):    
    def clean_amount(self):
        account=self.account
        min_withdraw_amount=500
        max_withdraw_amount=30000
        balance=account.balance
        amount=self.cleaned_data.get('amount')
        if amount<min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )
        if amount>max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )
        if amount>balance:
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance.'
            )
        return amount
    
class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount=self.cleaned_data.get('amount')
        return amount





class SendMoneyForm(TransactionForm):
    account_no = forms.IntegerField()

    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']

    def clean_account_no(self):
        account_no = self.cleaned_data['account_no']
        account = UserBankAccount.objects.filter(
            account_no=account_no).exists()
        if not account:
            raise forms.ValidationError(
                f"User with account {account_no} does not exist")
        return account_no

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount > self.account.balance:
            raise forms.ValidationError(f"You don't have enough money")
        return amount

