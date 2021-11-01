from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm ,PasswordChangeForm
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.forms import modelformset_factory
from django.urls import reverse


from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage

# Create your views here.
User=get_user_model()


class homepage(View):
    ''' View for homepage of our website '''
    def get(self,request):                                              
        return render(request=request, template_name="main/home.html")

class register_as_company(View):
    ''' This view is used for registering the company '''
    
    form_class = CompanySignUpForm
    initial={'key':'value'}
    template_name="main/Employer-Signup.html"
    
    def get(self,request):
        form = self.form_class(initial=self.initial)
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        form=self.form_class(request.POST or None,request.FILES or None)
        if form.is_valid():      
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
    
            user = User.objects.create_user(email, password)

            user.active = False
            user.name = form.cleaned_data.get('name')
            user.save()

            company = Company.objects.create(user = user)
            company.save()
            
            current_site = get_current_site(request)
            mail_subject = 'Verify your email to activate your account.'
            message = render_to_string('main/acc_active_email.html', {
                   'user': user,
                   'domain': current_site.domain,
                   'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                   'token': account_activation_token.make_token(user),
                })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            return HttpResponse('Please confirm your email address to complete the registration') 

        else:      
            print("ERROR")                                                           
            for field, items in form.errors.items():
                for item in items:
                    messages.error(request, f"{field}: {item}")

            form=self.form_class(initial=self.initial)
            return render(request ,self.template_name,{'form':form})

def activate(request, uidb64, token):
    ''' View for activating the user after email verification '''
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.active = True
        user.save()
        login(request, user)

        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


class login_request(View):
    form_class = AuthenticationForm
    initial={'key':'value'}
    template_name="main/Login-Page.html"
    
    def get(self,request):
        form = self.form_class(initial = self.initial)
        return render(request,self.template_name,{'form':form})
    
    def post(self,request):
        form = self.form_class(request=request,data=request.POST)
        if form.is_valid():                                             
            email = form.cleaned_data.get('username')                     
            password = form.cleaned_data.get('password')    
            user = authenticate(email = email, password = password)
 
            if user is not None: 
                login(request,user)                                     
                return redirect("main:company")                               
            else:                                                            
                messages.error(request, "Invalid username or password.")     
                form=self.form_class(initial=self.initial)
                return render(request, self.template_name, {'form':form})

        else:
            email = form.cleaned_data.get('username')                     
            password = form.cleaned_data.get('password')                     
            user = authenticate(email = email, password=password)

            try:
                user=User.objects.get(email = email)
                if user.is_active is False:
                    current_site = get_current_site(request)
                    mail_subject = 'Verify your email to activate your account.'
                    message = render_to_string('main/acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                        })
                    to_email = form.cleaned_data.get('email')
                    email = EmailMessage(mail_subject, message, to=[to_email])
                    email.send()
                    return HttpResponse("Verify your Email first")
            except:                                                                    
                messages.error(request, "Invalid username or password.")         
            
            form = self.form_class(initial = self.initial)
            return render(request ,self.template_name,{'form':form})


class post_job(View):
    ''' View for posting the job '''

    def get(self, request):
        if request.user.is_anonymous:
            return redirect("main:homepage")

        form = Job_Post(request.user)
        categories = Category.objects.all()
        locations = Location.objects.all()
        return render(request = request, template_name = "main/post_job.html", context={"form":form, "categories" : categories, "locations" : locations}) 

    def post(self, request):
        form = Job_Post(request.user, request.POST)
        if form.is_valid():
            job_profile = form.save(commit=False)
            company = Company.objects.get(user = request.user)  
            job_profile.company = company  
            job_profile.save()                
            title = form.cleaned_data.get('role')
            messages.success(request, f"New job posted : {title}")   
            return redirect("main:company")
        else :
            print(form.errors)
            return redirect("main:company")


class company_profile(View):
    ''' view for company profile '''
    def get(self,request):
        if request.user.is_anonymous:
            return redirect("main:homepage")
        elif request.user.admin == True:
            jobs = Jobs.objects.all()
            return render(request, 'main/Employer-Profile.html', {'jobs': jobs})
        try:
            company = Company.objects.get(user = request.user)
        except Company.DoesNotExist:
            return redirect("main:homepage")
        
        jobs = Jobs.objects.filter(company = company)
        return render(request, 'main/Employer-Profile.html', {'jobs': jobs})

class logout_request(View):
    def get(self,request):
        logout(request)
        return redirect("main:homepage") 
