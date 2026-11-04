from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.ProfileView.as_view(), name="profile"),
    path("guest/", views.GuestView.as_view(), name="guest"),
    path("password-reset/", views.PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset/confirm/", views.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("verify-email/request/", views.EmailVerificationRequestView.as_view(), name="verify-email-request"),
    path("verify-email/confirm/", views.EmailVerificationConfirmView.as_view(), name="verify-email-confirm"),
]
