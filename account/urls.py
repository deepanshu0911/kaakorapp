from django.urls import path
from account import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenVerifyView, TokenBlacklistView

urlpatterns = [
    path('create-user', views.CreateUser.as_view(), name='create-user'),
    path('verify-user/<str:token>', views.UserVerification.as_view()),
    path('user-login', views.UserLogin.as_view(), name='user-login'),
    path('user', views.UserAPI.as_view(), name='user'),
    path('users/manage', views.UsersManageAPI.as_view()),
    path('logout', views.UserLogout.as_view()),
    # path('logout', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('dashboard', views.DashboardAPI.as_view()),


]

urlpatterns = format_suffix_patterns(urlpatterns)
