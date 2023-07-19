from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import apis


app_name = 'users'

urlpatterns = [
    path('login', apis.LoginAPI.as_view(), name='login'),
    
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('save-referral', apis.SaveReferralDetails.as_view(), name='save-referral'),

    path('view-profile', apis.ViewProfile.as_view(), name='view-profile'),

    path('add-task', apis.AddTaskAPI.as_view(), name='add-task'),

]
