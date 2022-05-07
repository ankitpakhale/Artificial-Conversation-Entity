from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import chatbot
from . models import *

chatbot_instance = None

if chatbot_instance == None:
    chatbot_instance = chatbot.Chatbot("./media/New_Json_norm.json")

def home(request):
    if 'email' in request.session:
        return render(request, "home.html", {'title': 'Sili Chatbot Version 1.0'})
    return redirect('sili:LOGIN')

@csrf_exempt
def Talk(request):
    response = {'status': None}
    if request.method == 'POST':
        da = json.loads(request.body)
        mesg = da['message']
        user_input = str(mesg)
        if user_input.lower() == 'quit' or user_input.lower() == 'close':
            return render(request, "home.html", {'title': 'Sili Chatbot Version 1.0'})
        else:
            chat_response = chatbot_instance.ask_question(mesg)
        response['message'] = {'text': str(
            chat_response), 'user': False, 'chat_bot': True}
        response['status'] = 'ok'
    else:
        response['error'] = 'no post data found'

    return HttpResponse(
        json.dumps(response),
        content_type="application/json")
    

# ---------------------EXTRA-----------------------

def SignupView(self):
    if self.POST:
        Name = self.POST['name']
        Email = self.POST['email']
        Number = self.POST['number']
        Password = self.POST['password']
        Age = self.POST['age']
        ConfirmPassword = self.POST['confirmPassword']
        try:
            data=SignUp.objects.get(email=Email)
            if data:
                msg = 'This Email is already Registered'
                return render(self , 'signup.html',{'msg':msg}) 
        except:
            if ConfirmPassword == Password:
                v = SignUp(
                name = Name,
                email = Email,
                number = Number,
                age = Age,
                password = Password,
                confirmPassword = ConfirmPassword
                )
                v.save()
                return render(self , 'signup.html',{'msg':'Congratulations, your account has been successfully created.'}) 
                # return redirect('sili:LOGIN')
            else:
                msg = 'Enter Same Password'
                return render(self , 'signup.html',{'msg':msg}) 
    return render(self,'signup.html')

def login(self):
    if self.POST:
        em = self.POST.get('email')
        pass1 = self.POST.get('password')
        try:
            check = SignUp.objects.get(email = em)
            if check.password == pass1: 
                self.session['email'] = check.email
                return redirect('sili:index')
            else:
                msg = 'Enter Correct Password'
                return render(self , 'login.html',{'msg':msg}) 
        except:
            msg = 'User does not exist'
            return render(self , 'login.html',{'msg':msg}) 
    return render(self,'login.html')


def userLogOut(request):
    del request.session['email']
    print('User logged out')
    return redirect('sili:LOGIN')

def index(request):
    if 'email' in request.session:
        return render(request, 'index.html')
    return redirect('sili:LOGIN')

def about(request):
    if 'email' in request.session:
        return render(request, 'about.html')
    return redirect('sili:LOGIN')

def services(request):
    if 'email' in request.session:
        return render(request, 'services.html')
    return redirect('sili:LOGIN')

def contact(request):
    if 'email' in request.session:
        msg = ''
        if request.method == 'POST':
            db = ContactForm(name = request.POST.get('name'), 
                                email = request.POST.get('email'), 
                                phone = request.POST.get('phone'), 
                                subject = request.POST.get('subject'), 
                                message = request.POST.get('message'))

            db.save()
            key = "Your Message has been sent successfully"
            print(key)
            msg = "Thank you! Your message has been successfully sent."
        return render(request, 'contact.html', {'msg': msg})
    return redirect('sili:LOGIN')

def error(request):
    if 'email' in request.session:
        return render(request, 'error.html')
    return redirect('sili:LOGIN')

def faq(request):
    if 'email' in request.session:
        return render(request, 'faq.html')
    return redirect('sili:LOGIN')

def portfolio(request):
    if 'email' in request.session:
        return render(request, 'portfolio.html')
    return redirect('sili:LOGIN')
