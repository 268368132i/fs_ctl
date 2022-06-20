from django.shortcuts import render, redirect

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse
from django.contrib.auth.views import LoginView

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('exchange:confs'))
            else:
                return HttpResponse("Account not active")
        else:
            print("Someone tried to login and failed")
            print("Username: {} and password {}",format(username,password))
            return HttpResponse('Invalid login detailes supplied')
    else:
        return render(request,'accounts/login.html',{})
        
def logout_view(request):
  logout(request)
  return redirect(reverse('exchange:confs'))

        
class MyUserLogin(LoginView):
  pass