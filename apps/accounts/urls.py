from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("dang-ky/", views.signup, name="signup"),
    path("dang-nhap/", views.login_view, name="login"),
    path("xac-thuc-2fa/", views.verify_2fa, name="verify_2fa"),
    path("gui-lai-2fa/", views.resend_2fa, name="resend_2fa"),
    path("dang-xuat/", views.logout_view, name="logout"),
    path("dang-nhap/google/", views.google_start, name="google_start"),
    path("dang-nhap/google/callback/", views.google_callback, name="google_callback"),
    path("hoan-tat-dang-ky/", views.complete_signup, name="complete_signup"),
    path("dong-y-dieu-khoan/", views.accept_policies, name="accept_policies"),
    path("tai-khoan/", views.profile, name="profile"),
    path("tai-khoan/doi-mat-khau/", views.password_change, name="password_change"),
    path("quen-mat-khau/", views.password_reset, name="password_reset"),
    path("quen-mat-khau/da-gui/", views.password_reset_done, name="password_reset_done"),
    path("dat-lai-mat-khau/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("dat-lai-mat-khau/xong/", views.password_reset_complete, name="password_reset_complete"),
]
