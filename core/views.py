from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AgentRegistrationForm

def register(request):
    if request.method == 'POST':
        form = AgentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = AgentRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})