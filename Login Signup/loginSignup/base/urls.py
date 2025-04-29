from django.urls import path
from . import views

urlpatterns = [
    path("",views.Home,name="home"),        #ROOT URL
    path("home/",views.Home,name="home"),
    path("login/",views.LoginView,name="login"),   
    path("register/",views.RegisterView,name="register"),
    path("login/",views.LoginView,name="login"),
    path("logout/",views.LogoutView, name="logout"),
    path("forgot-password/",views.ForgotPasswordView,name="forgot-password"),
    path("password-reset-sent/<str:reset_id>/",views.PasswordResetSent,name="password-reset-sent"),
    path("reset-password/<str:reset_id>/",views.ResetPassword,name="reset-password")
]