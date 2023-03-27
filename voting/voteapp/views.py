from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Candidate,ControlVote,Position
from django.contrib import messages
from firebase_admin import db
ref=db.reference('votes')
# Create your views here.



@login_required(login_url='login')
def HomePage(request):
    return render (request,'home.html')

def SignupPage(request):
    if request.method=='POST':
        usname=request.POST.get('username')
        email=request.POST.get('email')
        passw=request.POST.get('password')
        usr=User.objects.create_user(usname,email,passw)
        usr.save()
        return redirect('login')
    
    return render (request,'signup.html')

def LoginPage(request):
    if request.method == 'POST':
        username=request.POST.get('ussname')
        passwd=request.POST.get('passww')
        usrr=authenticate(request,username=username,password=passwd)
        if usrr is not None:
            login(request,usrr)
            return redirect('home')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")
    return render (request,'login.html')
        

@login_required
def VotingPage(request, pos):
    obj = get_object_or_404(Position, pk = pos)
    if request.method == "POST":

        temp = ControlVote.objects.get_or_create(user=request.user, position=obj)[0]

        if temp.status == False:
            temp2 = Candidate.objects.get(pk=request.POST.get(obj.title))
            temp2.total_vote += 1
            temp2.save()
            temp.status = True
            temp.save()
            send_vote_to_firebase(candidate_name=temp2.name, position_name=obj.title)
            return HttpResponseRedirect('/voteresult/')
        else:
            messages.success(request, 'you have already been voted this position.')
            return render(request, 'votecandi.html', {'obj':obj})
        
    else:
        return render(request, 'votecandi.html', {'obj':obj})
        
    
    
@login_required
def PositionPage(request):
    obj = Position.objects.all()
    return render(request, "position.html", {'obj':obj})

@login_required
def VoteResultPage(request):
    obj = Candidate.objects.all().order_by('position','-total_vote')
    return render(request, "voteresult.html", {'obj':obj})

def send_vote_to_firebase(candidate_name, position_name):
    ref = db.reference('votes')  # Create a reference to the 'votes' node
    new_vote_ref = ref.push()  # Generate a new unique key for the vote
    new_vote_ref.set({
        'candidate_name': candidate_name,
        'position_name': position_name
    })  # Set the candidate and position names as the vote data

def LogoutPage(request):
    logout(request)
    return redirect('login')


