from django.urls import path
from . import views
from django.conf.urls import url
from main.views import *
app_name="main"

urlpatterns = [
    path("",homepage.as_view(),name="homepage"),
    path("register_as_company/",register_as_company.as_view(), name="register_as_company"), 
    path("login/",login_request.as_view(), name="login"),
    path("logout/", logout_request.as_view(), name="logout"), 
    path("post_job/", post_job.as_view(), name ='post_job'),
    path("company_profile/",company_profile.as_view(),name="company"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate')
]