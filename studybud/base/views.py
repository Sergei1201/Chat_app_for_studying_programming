from django.shortcuts import render, redirect
from .models import Room
from .forms import RoomForm

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


def home(request):
    # Query the database to get all rooms
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)

    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    context = {'room': room}
    return render(request, 'base/room.html', context)


# Create Room
def create_room(request):
    # Create an instance of form class (make a form object)
    form = RoomForm()
    # Check if the request is POST
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

# Update Room
def update_room(request, pk):
    # Get the room we need to update by ID
    room = Room.objects.get(id=pk)
    # Instantiate a form class (make a form object prefilled with room)
    form = RoomForm(instance=room)
    # Check if the method is POST
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        # Check if the form fields are valid, save them in the database
        if form.is_valid:
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

# Delete Room
def delete_room(request, pk):
    # Get the room by ID to delete
    room = Room.objects.get(id=pk)
    # Check if the request is POST then delete the room
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})