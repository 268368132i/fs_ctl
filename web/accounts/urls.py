from django.urls import path
from . import views
app_name='accounts'

urlpatterns=[
	path('login_old/', views.user_login, name='user_login_old'),
	path('login/', views.MyUserLogin.as_view(), name='user_login'),
	path('logout/', views.logout_view, name='user_logout'),
]