from django.shortcuts import render,redirect
from django.views.generic import FormView
from .forms import UserRegistrationForm,UserUpdateForm
from django.contrib.auth import login,logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView,LogoutView
from django.views import View

from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages

def send_transaction_mail(user,subject,template):
        message=render_to_string(template,{
            'user': user,
        })        
        send_email=EmailMultiAlternatives(subject,'',to=[user.email])
        send_email.attach_alternative(message,"text/html")
        send_email.send()

# Create your views here.
class UserRegistrationView(FormView):
    template_name='accounts/user_registration.html'
    form_class=UserRegistrationForm
    success_url=reverse_lazy('register')
    
    def form_valid(self, form):
        # print(form.cleaned_data)
        user=form.save()
        login(self.request,user)
        return super().form_valid(form) #form valid function call korbe jodi sob thik thake
    

class UserLoginView(LoginView):
    template_name='accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')

    
def user_logout(request):
    logout(request)
    return redirect('home')


class UserBankAccountUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})
    
class ChangePasswordView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/change_password.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)        
        message = 'Password changed'
        send_transaction_mail(self.request.user, message, 'accounts/changepassword_email.html')
        messages.success(self.request, 'Your password was changed successfully.')

        return response
