from django.contrib.auth import login
from django.shortcuts import  redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Course

def course_list(request):
    courses = Course.objects.select_related("title")
    return render(request, "Library/menu.html", {"courses": courses})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('library:menu')
    else:
        form = UserCreationForm()
    return render(request, 'Library/auth/register.html', {'form': form})