from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from .models import *
from django.http import HttpResponse

@login_required(login_url='login')         #RESTRICTING THE UNAUTHORIZED USERS
def Home(request):
    return render(request,"index.html")

def RegisterView(request):
    
    # GETTING USER INPUTS FROM FRONT END
    if(request.method == "POST"):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        #VALIDATING THE DATA PROVIDED
        user_data_has_error = False
        
        #ENSURING THAT THE USER CREDENTIALS HAVE NOT BEEN USED BEFORE
        if(User.objects.filter(username=username).exists()):
            user_data_has_error=True
            messages.error(request, "Username already exists!")
                
        if(User.objects.filter(email=email).exists()):
            user_data_has_error=True
            messages.error(request, "An account with this email already exists")
    
        #VALIDATING PASSWORD LENGTH
        if(len(password) < 5):
            user_data_has_error=True
            messages.error(request, "Password must be atleast 5 characters")
    
        #IF ALL THE USER CREDENTIALS ARE VALID
        if(user_data_has_error):
            return redirect("register")
        else:
            new_user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username=username,
                email=email,
                password = password
            )
            messages.success(request, "Account created successfully. Login Now")
            return redirect("login")
            
    return render(request,"register.html")

def LoginView(request):
    
    #GETTING USER CREDENTIALS FROM FRONTEND
    if(request.method == "POST"):
        username = request.POST.get("username")
        password = request.POST.get("password")
    
        #AUTHENTICATING USER CREDENTIALS
        user = authenticate(request,username=username,password=password)
        
        if (user is not None):
            #LOGIN IF THE CREDENTIALS ARE VALID
            login(request,user)
            
            #REDIRECT TO HOME PAGE
            return redirect("home")
        
        else:
            messages.error(request, "Invalid Username or Password")    
            return redirect("login")
    
    return render(request,"login.html")

def LogoutView(request):
    logout(request)
    
    #REDIRECT TO THE LOGIN PAGE AFTER LOGGING OUT
    return redirect("login")

def ForgotPasswordView(request):
    
    if(request.method == "POST"):
        email = request.POST.get("email")
        
        #VERIFYING THE EMAIL EXISTENCE
        try:
            user = User.objects.get(email=email)
            
            #IF THE EMAIL IS VALID
            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()
            
            password_reset_url = reverse('reset-password',kwargs = {'reset_id' : new_password_reset.reset_id})
            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
            
            #EMAIL CONTENT
            email_body = f'Reset your password using the link below : \n\n\n{full_password_reset_url}'
            
            email_message = EmailMessage(
                'Reset your password',   #EMAIL SUBJECT
                email_body,
                settings.EMAIL_HOST_USER,   #EMAIL SENDER
                [email]     #EMAIL RECEIVER
            )
            
            email_message.fail_silently = True
            email_message.send()
            
            return redirect("password-reset-sent",reset_id = new_password_reset.reset_id)
            
        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' was found")
            return redirect('forgot-password')
            
    return render(request,"forgot_password.html")

def PasswordResetSent(request,reset_id):
    
    if(PasswordReset.objects.filter(reset_id=reset_id).exists()):
        return render(request,"password_reset_sent.html")
    else:
        #REDIRECT TO THE FORGOT PASSWORD PAGE IF THE CODE DOES NOT EXIST
        messages.error(request,"Invalid reset id")
        return redirect("forgot-password")

def ResetPassword(request,reset_id):
    
    try:
        password_reset_id = PasswordReset.objects.get(reset_id = reset_id)
    
        #GET PASSWORDS FROM THE FRONT END FORM    
        if (request.method == "POST"):
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            passwords_have_error = False
            
            #VERIFYING THE PASSWORD AND THE RESET LINK
            if(password != confirm_password):
                passwords_have_error=True
                messages.error(request, "Password do not match")
        
            if(len(password) < 5):
                passwords_have_error=True
                messages.error(request,"Password must have atleast 5 characters")
               
            #ENSURING THE LINK IS NOT EXPIRED
            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)    
             
            if(timezone.now() > expiration_time):
                password_reset_id.delete()
                passwords_have_error=True
                messages.error(request,"Resent link has expired")    
              
            #RESET PASSWORD
            if(not passwords_have_error):
                user = password_reset_id.user
                user.set_password(password)
                user.save()
                
                #DELETE RESET ID AFTER USE
                password_reset_id.delete()
                
                #REDIRECT TO THE LOGIN PAGE
                messages.success(request,"Password reset completed. Proceed to login")
                return redirect("login")    
            else:
                return redirect("reset-password",reset_id=reset_id)    
    
    except PasswordReset.DoesNotExist:
        messages.error(request,"Invalid reset id")
        return redirect("forgot-password")
    
    return render(request,"reset_password.html")