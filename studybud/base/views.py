from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Lets learn PHP'},
#     {'id': 2, 'name': 'Lets learn JavaScript'},
#     {'id': 3, 'name': 'Lets learn Python'},
#     {'id': 4, 'name': 'Lets learn React'},
#     {'id': 5, 'name': 'Lets learn NodeJS'},
#     {'id': 6, 'name': 'Lets learn Laravel'},
#     {'id': 7, 'name': 'Lets learn Django'},
# ]


def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    # Check if the method is POST
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # Check if the user exists in the database
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'The user does not exist')

        # Authenticate User if there's user
        user = authenticate(request, username=username, password=password)

        # Check if the user is authenticated, log in
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'The username of password does not exist')
    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def register_user(request):
    page = 'register'
    form = UserCreationForm()

    # Check if the method is POST:
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        # Validate the form
        # If valid, register the user
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
    context = {'page': page, 'form': form}
    return render(request, 'base/login_register.html', context)


def home(request):
    # Query the database to get all rooms
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q))
    room_count = rooms.count()
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created_at')
    participants = room.participants.all()

    # Add a new message to the room
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )

        # Add a new participant to the room
        room.participants.add(request.user)
        redirect('room', pk=room.id)

    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)

# Create Room


@login_required(login_url='login')
def create_room(request):
    # Create an instance of form class (make a form object)
    form = RoomForm()
    # Check if the request is POST
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

# Update Room


@login_required(login_url='login')
def update_room(request, pk):

    # Get the room we need to update by ID
    room = Room.objects.get(id=pk)

    # Instantiate a form class (make a form object prefilled with room)
    form = RoomForm(instance=room)

    # Check if you are the owner of the room to have permission for updating
    if request.user != room.host:
        return HttpResponse('You are not allowed to update the room')

    # Check if the method is POST
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)

        # Check if the form fields are valid, save them in the database
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

# Delete Room


@login_required(login_url='login')
def delete_room(request, pk):

    # Get the room by ID to delete
    room = Room.objects.get(id=pk)

    # Check if you are the owner of the room to have permission for deleting
    if request.user != room.host:
        return HttpResponse('You are not allowed to delete the room')
    # Check if the request is POST then delete the room
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def delete_message(request, pk):

    # Get the message by ID to delete
    message = Message.objects.get(id=pk)

    # Check if the requested user is message's owner
    if request.user != message.user:
        return HttpResponse('You are not allowed to delete the message')

    # Check for POST request
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})
