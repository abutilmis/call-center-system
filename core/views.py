from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Entity, CorrectionRequest, KnowledgeBase, Announcement
from .forms import EntityForm, CorrectionRequestForm, KnowledgeBaseForm, AnnouncementForm
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

def supervisor_required(view_func):
    """Decorator to restrict access to supervisors only."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'supervisor':
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def dashboard(request):
    context = {
        'entity_count': Entity.objects.count(),
        'pending_corrections': CorrectionRequest.objects.filter(status='pending').count(),
        'knowledge_count': KnowledgeBase.objects.count(),
        'announcements': Announcement.objects.order_by('-timestamp')[:5],
    }
    return render(request, 'dashboard.html', context)

# Entities
@login_required
def entity_list(request):
    query = request.GET.get('q', '')
    entities = Entity.objects.all()
    if query:
        entities = entities.filter(
            Q(name__icontains=query) | Q(phone__icontains=query) | Q(location__icontains=query)
        )
    return render(request, 'entity_list.html', {'entities': entities, 'query': query})

@login_required
def entity_create(request):
    if request.method == 'POST':
        form = EntityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Entity created successfully.")
            return redirect('entity_list')
    else:
        form = EntityForm()
    return render(request, 'entity_form.html', {'form': form, 'title': 'Create Entity'})

@login_required
def entity_update(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    if request.method == 'POST':
        form = EntityForm(request.POST, instance=entity)
        if form.is_valid():
            form.save()
            messages.success(request, "Entity updated successfully.")
            return redirect('entity_list')
    else:
        form = EntityForm(instance=entity)
    return render(request, 'entity_form.html', {'form': form, 'title': 'Update Entity'})

@login_required
def entity_delete(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    if request.method == 'POST':
        entity.delete()
        messages.success(request, "Entity deleted.")
        return redirect('entity_list')
    return render(request, 'entity_confirm_delete.html', {'entity': entity})

# Correction Requests
@login_required
def correction_list(request):
    if request.user.role == 'supervisor':
        corrections = CorrectionRequest.objects.all().order_by('-created_at')
    else:
        corrections = CorrectionRequest.objects.filter(agent=request.user).order_by('-created_at')
    return render(request, 'correction_list.html', {'corrections': corrections})

@login_required
def correction_create(request):
    if request.method == 'POST':
        form = CorrectionRequestForm(request.POST)
        if form.is_valid():
            correction = form.save(commit=False)
            correction.agent = request.user
            correction.save()
            messages.success(request, "Correction request submitted.")
            return redirect('correction_list')
    else:
        form = CorrectionRequestForm()
    return render(request, 'correction_form.html', {'form': form, 'title': 'Request Correction'})

@login_required
@supervisor_required
def correction_approve(request, pk):
    correction = get_object_or_404(CorrectionRequest, pk=pk)
    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        status = request.POST.get('status')
        if status in ['approved', 'rejected']:
            correction.status = status
            correction.supervisor_comment = comment
            correction.save()
            if status == 'approved':
                # Apply the correction to the entity
                entity = correction.entity
                setattr(entity, correction.field_to_correct, correction.new_value)
                entity.save()
            messages.success(request, f"Request {status}.")
            return redirect('correction_list')
    return render(request, 'correction_approve.html', {'correction': correction})

# Knowledge Base
@login_required
def knowledge_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    knowledge = KnowledgeBase.objects.all()
    if query:
        knowledge = knowledge.filter(Q(question__icontains=query) | Q(answer__icontains=query))
    if category:
        knowledge = knowledge.filter(category=category)
    categories = KnowledgeBase.objects.values_list('category', flat=True).distinct()
    return render(request, 'knowledge_list.html', {
        'knowledge': knowledge,
        'query': query,
        'category': category,
        'categories': categories,
    })

@login_required
@supervisor_required
def knowledge_create(request):
    if request.method == 'POST':
        form = KnowledgeBaseForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.save()
            messages.success(request, "Knowledge entry added.")
            return redirect('knowledge_list')
    else:
        form = KnowledgeBaseForm()
    return render(request, 'knowledge_form.html', {'form': form, 'title': 'Add Knowledge Entry'})

# Announcements
@login_required
def announcement_list(request):
    announcements = Announcement.objects.all().order_by('-timestamp')
    return render(request, 'announcement_list.html', {'announcements': announcements})

@login_required
@supervisor_required
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.posted_by = request.user
            announcement.save()
            messages.success(request, "Announcement posted.")
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'announcement_form.html', {'form': form, 'title': 'Post Announcement'})
from django.http import HttpResponse
from django.contrib.auth import get_user_model

User = get_user_model()

def create_supervisor(request):
    """Temporary view – remove after use."""
    username = "supervisor"
    email = "supervisor@kalzanay@gmail.com"
    password = "superladyhana"   # CHANGE THIS TO A SECURE PASSWORD
    role = "supervisor"

    if User.objects.filter(username=username).exists():
        return HttpResponse(f"User '{username}' already exists.")
    
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    user.role = role
    user.save()
    return HttpResponse(f"Supervisor created!<br>Username: {username}<br>Password: {password}<br>Please log in and change your password.")