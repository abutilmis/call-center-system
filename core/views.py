from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from .models import Entity, ClientCorrection, KnowledgeBase, Announcement
from .forms import EntityForm, KnowledgeBaseForm, AnnouncementForm, AgentRegistrationForm, OSSCUploadForm
from django.db import connection
from django.http import HttpResponse
import json

User = get_user_model()

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
        'total_entities': Entity.objects.count(),
        'agencies_count': Entity.objects.filter(entity_type='agency').count(),
        'tvet_count': Entity.objects.filter(entity_type='tvet').count(),
        'ocss_count': Entity.objects.filter(entity_type='ocss').count(),
        'pending_corrections': ClientCorrection.objects.filter(status='pending').count(),
        'knowledge_count': KnowledgeBase.objects.count(),
        'announcements': Announcement.objects.order_by('-timestamp')[:5],
        'recent_entities': Entity.objects.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard.html', context)

from django.http import JsonResponse
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Entity
import traceback
from django.http import HttpResponse

@login_required
def entity_list(request):
    try:
        entity_type = request.GET.get('type', 'agency')
        query = request.GET.get('q', '')
        sort = request.GET.get('sort', 'date_desc')

        entities = Entity.objects.filter(entity_type=entity_type)

        # AJAX distinct filters
        if request.GET.get('action') == 'get_filters':
            column = request.GET.get('column')
            if column:
                values = entities.exclude(**{f"{column}__isnull": True}).exclude(**{f"{column}__exact": ''}).values_list(column, flat=True).distinct().order_by(column)
                return JsonResponse({'values': list(values)})
            return JsonResponse({'values': []})

        # Apply column filters dynamically
        active_filters = {}
        for key, value in request.GET.items():
            if key.startswith('filter_') and value:
                col = key.replace('filter_', '')
                entities = entities.filter(**{f"{col}__exact": value})
                active_filters[key] = value

        # Search
        if query:
            if entity_type == 'agency':
                entities = entities.filter(
                    Q(name__icontains=query) | Q(phone__icontains=query) | Q(phone2__icontains=query)
                )
            elif entity_type == 'ocss':
                entities = entities.filter(
                    Q(name__icontains=query) | Q(region__icontains=query) | Q(city__icontains=query) | Q(woreda__icontains=query)
                )
            elif entity_type == 'tvet':
                entities = entities.filter(
                    Q(name__icontains=query) | Q(registration_id__icontains=query) | Q(location__icontains=query)
                )
            else:
                entities = entities.filter(name__icontains=query)

        # Sorting
        sort_map = {
            'name_asc': 'name',
            'name_desc': '-name',
            'date_asc': 'created_at',
            'date_desc': '-created_at',
        }
        entities = entities.order_by(sort_map.get(sort, '-created_at'))

        # AJAX autocomplete
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if entity_type == 'ocss':
                results = entities.values('entity_id', 'name', 'region', 'city', 'woreda')[:20]
                # Normalize to match frontend expectations (phone, phone2, city, woreda)
                results_list = []
                for r in results:
                    results_list.append({
                        'entity_id': r['entity_id'],
                        'name': r['name'],
                        'phone': r.get('region', '') or r.get('city', '') or r.get('woreda', ''),
                        'phone2': '',
                        'city': r.get('city', ''),
                        'woreda': r.get('woreda', ''),
                    })
                return JsonResponse({'results': results_list})
            else:
                results = entities.values('entity_id', 'name', 'phone', 'phone2', 'city', 'woreda')[:20]
                return JsonResponse({'results': list(results)})
            

        # Pagination
        paginator = Paginator(entities, 20)
        page = request.GET.get('page')
        try:
            entities_page = paginator.page(page)
        except PageNotAnInteger:
            entities_page = paginator.page(1)
        except EmptyPage:
            entities_page = paginator.page(paginator.num_pages)

        filter_qs = ''.join([f"&{k}={v}" for k, v in active_filters.items()])

        return render(request, 'entity_list.html', {
            'entities': entities_page,
            'query': query,
            'entity_type': entity_type,
            'sort': sort,
            'active_filters': active_filters,
            'filter_qs': filter_qs,
        })
    except Exception as e:
        return HttpResponse(f"<pre>{traceback.format_exc()}</pre>")

@login_required
@supervisor_required
def delete_all_entities(request):
    if request.method == 'POST':
        entity_type = request.POST.get('entity_type')
        if entity_type in ['agency', 'tvet', 'ocss']:
            deleted_count, _ = Entity.objects.filter(entity_type=entity_type).delete()
            messages.success(request, f"Successfully deleted all {deleted_count} {entity_type} records.")
        else:
            messages.error(request, "Invalid entity type specified.")
    return redirect('entity_list')
import pandas as pd
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import AgencyUploadForm
from .models import Entity
import logging

logger = logging.getLogger(__name__)

@login_required
@supervisor_required
def upload_agencies(request):
    if request.method == 'POST':
        form = AgencyUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                df = pd.read_excel(file, engine='openpyxl', dtype=str)
                df.columns = [str(col).strip().title() for col in df.columns]

                required_cols = ['Name', 'Phone1', 'Phone2', 'City', 'Woreda']
                missing = [col for col in required_cols if col not in df.columns]
                if missing:
                    messages.error(
                        request,
                        f'File must contain columns: {required_cols}. Found: {list(df.columns)}. Missing: {missing}'
                    )
                    return redirect('upload_agencies')

                entities_to_create = []
                created = 0
                errors = 0

                for idx, row in df.iterrows():
                    try:
                        name = str(row['Name']) if pd.notna(row['Name']) else ''
                        phone1 = str(row['Phone1']) if pd.notna(row['Phone1']) else ''
                        phone2 = str(row.get('Phone2', '')) if pd.notna(row.get('Phone2')) else ''
                        city = str(row.get('City', '')) if pd.notna(row.get('City')) else ''
                        woreda = str(row.get('Woreda', '')) if pd.notna(row.get('Woreda')) else ''

                        # Clean non‑UTF‑8 characters
                        name = name.encode('utf-8', 'replace').decode('utf-8')
                        phone1 = phone1.encode('utf-8', 'replace').decode('utf-8')
                        phone2 = phone2.encode('utf-8', 'replace').decode('utf-8')
                        city = city.encode('utf-8', 'replace').decode('utf-8')
                        woreda = woreda.encode('utf-8', 'replace').decode('utf-8')

                        if not name or not phone1:
                            errors += 1
                            continue

                        entities_to_create.append(
                            Entity(
                                entity_type='agency',
                                name=name,
                                phone=phone1,
                                phone2=phone2,
                                city=city,
                                woreda=woreda,
                            )
                        )
                        created += 1
                    except Exception as e:
                        errors += 1
                        logger.warning(f"Row {idx+2} failed: {e}")

                # Bulk create all valid entities
                if entities_to_create:
                    Entity.objects.bulk_create(entities_to_create)

                if errors:
                    messages.warning(request, f'{created} agencies imported. {errors} rows skipped due to errors.')
                else:
                    messages.success(request, f'{created} agencies imported successfully.')
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
            return redirect('entity_list')
    else:
        form = AgencyUploadForm()
    return render(request, 'agency_upload.html', {'form': form})
@login_required
def entity_create(request):
    initial_type = request.GET.get('type', 'agency')
    if request.method == 'POST':
        form = EntityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Entity created successfully.")
            return redirect('entity_list')
    else:
        form = EntityForm(initial={'entity_type': initial_type})
    return render(request, 'entity_form.html', {'form': form, 'title': f'Create {initial_type.title()}'})

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

# Client Correction Requests
@login_required
def client_correction_list(request):
    if request.user.role == 'supervisor':
        corrections = ClientCorrection.objects.all().order_by('-created_at')
    else:
        corrections = ClientCorrection.objects.filter(agent=request.user).order_by('-created_at')
    return render(request, 'client_correction_list.html', {'corrections': corrections})

@login_required
def client_correction_create(request):
    if request.method == 'POST':
        correction_type = request.POST.get('correction_type')
        phone = request.POST.get('phone')
        labor_id = request.POST.get('labor_id', '')
        old_data = request.POST.get('old_data', '{}')
        new_data = request.POST.get('new_data', '{}')
        
        try:
            old_data_dict = json.loads(old_data)
            new_data_dict = json.loads(new_data)
        except ValueError:
            old_data_dict = {}
            new_data_dict = {}

        if correction_type and phone:
            ClientCorrection.objects.create(
                correction_type=correction_type,
                phone=phone,
                labor_id=labor_id,
                old_data=old_data_dict,
                new_data=new_data_dict,
                agent=request.user,
                status='pending'
            )
            messages.success(request, "Client correction request submitted successfully.")
            return redirect('client_correction_list')
        else:
            messages.error(request, "Please fill in all required fields.")
            
    return render(request, 'client_correction_form.html', {'title': 'New Client Correction'})

@login_required
@supervisor_required
def client_correction_approve(request, pk):
    correction = get_object_or_404(ClientCorrection, pk=pk)
    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        status = request.POST.get('status')
        if status in ['approved', 'rejected']:
            correction.status = status
            correction.supervisor_comment = comment
            correction.save()
            messages.success(request, f"Request {status}.")
            return redirect('client_correction_list')
    return render(request, 'client_correction_approve.html', {'correction': correction})

@login_required
def client_correction_detail(request, pk):
    correction = get_object_or_404(ClientCorrection, pk=pk)
    if request.user.role != 'supervisor' and correction.agent != request.user:
        messages.error(request, "You don't have permission to view this request.")
        return redirect('client_correction_list')
    return render(request, 'client_correction_detail.html', {'correction': correction})

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

# User Registration
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

# Temporary supervisor creation (remove after use)
def create_supervisor(request):
    username = "supervisor"
    email = "supervisor@example.com"
    password = "YourStrongPassword123"   # CHANGE THIS!
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
def increase_lengths(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE core_entity ALTER COLUMN name TYPE varchar(200);")
            cursor.execute("ALTER TABLE core_entity ALTER COLUMN phone TYPE varchar(200);")
            cursor.execute("ALTER TABLE core_entity ALTER COLUMN phone2 TYPE varchar(200);")
            cursor.execute("ALTER TABLE core_entity ALTER COLUMN city TYPE varchar(200);")
            cursor.execute("ALTER TABLE core_entity ALTER COLUMN woreda TYPE varchar(200);")
        return HttpResponse("✅ All text fields increased to 200 characters.")
    except Exception as e:
        return HttpResponse(f"❌ Error: {e}")
from .forms import OSSCUploadForm

@login_required
@supervisor_required
def upload_ossc(request):
    if request.method == 'POST':
        form = OSSCUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                df = pd.read_excel(file, engine='openpyxl', dtype=str)
                # Normalize: strip, lowercase, replace spaces, slashes, hyphens with underscore
                df.columns = [
                    str(col).strip().lower().replace(' ', '_').replace('/', '_').replace('-', '_')
                    for col in df.columns
                ]

                # Expected normalized column names (for checking)
                required_norm = {
                    'region': 'region',
                    'zone_city': 'zone_city',
                    'woreda_sub_city': 'woreda_sub_city',
                    'ossc_name': 'ossc_name',
                }
                # Original expected names (for user messages)
                original_names = {
                    'region': 'Region',
                    'zone_city': 'Zone/City',
                    'woreda_sub_city': 'Woreda/Sub-City',
                    'ossc_name': 'OSSC Name',
                }

                # Check which required columns are present
                present = set(df.columns)
                missing = [original_names[req] for req in required_norm.keys() if required_norm[req] not in present]
                if missing:
                    messages.error(
                        request,
                        f'File must contain columns: {list(original_names.values())}. '
                        f'Found: {list(df.columns)}. Missing: {missing}'
                    )
                    return redirect('upload_ossc')

                entities_to_create = []
                created = 0
                errors = 0

                for idx, row in df.iterrows():
                    try:
                        # Access normalized column names
                        region = str(row['region']) if pd.notna(row['region']) else ''
                        zone = str(row['zone_city']) if pd.notna(row['zone_city']) else ''
                        woreda = str(row['woreda_sub_city']) if pd.notna(row['woreda_sub_city']) else ''
                        name = str(row['ossc_name']) if pd.notna(row['ossc_name']) else ''

                        # Clean encoding
                        region = region.encode('utf-8', 'replace').decode('utf-8')
                        zone = zone.encode('utf-8', 'replace').decode('utf-8')
                        woreda = woreda.encode('utf-8', 'replace').decode('utf-8')
                        name = name.encode('utf-8', 'replace').decode('utf-8')

                        if not name:
                            errors += 1
                            continue

                        entities_to_create.append(
                            Entity(
                                entity_type='ocss',
                                name=name,
                                region=region,
                                city=zone,
                                woreda=woreda,
                                phone='',
                            )
                        )
                        created += 1
                    except Exception as e:
                        errors += 1
                        logger.warning(f"Row {idx+2} failed: {e}")

                if entities_to_create:
                    Entity.objects.bulk_create(entities_to_create)

                if errors:
                    messages.warning(request, f'{created} OCSS entries imported. {errors} rows skipped.')
                else:
                    messages.success(request, f'{created} OCSS entries imported successfully.')
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
            return redirect('entity_list')
    else:
        form = OSSCUploadForm()
    return render(request, 'ossc_upload.html', {'form': form})         
def debug_entities_db(request):
    from core.models import Entity
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    import traceback
    try:
        entities = Entity.objects.all().order_by('entity_id')   # changed from 'id'
        paginator = Paginator(entities, 20)
        page = request.GET.get('page', 1)
        entities_page = paginator.page(page)
        return HttpResponse(f"Page {page}: {len(entities_page)} entities")
    except Exception as e:
        return HttpResponse(f"Error: {e}<br><pre>{traceback.format_exc()}</pre>")

def test_paginated(request):
    import traceback
    try:
        from core.models import Entity
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

        entities = Entity.objects.filter(entity_type='agency').order_by('entity_id')   # changed from 'id'
        paginator = Paginator(entities, 20)
        page = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        html = f"<h1>Page {page_obj.number} of {paginator.num_pages}</h1><ul>"
        for e in page_obj:
            html += f"<li>{e.name} - {e.phone} - {e.city} - {e.woreda}</li>"
        html += "</ul>"
        return HttpResponse(html)
    except Exception as e:
        return HttpResponse(f"<pre>{traceback.format_exc()}</pre>")    
def debug_entity_list(request):
    import traceback
    from django.http import HttpResponse
    from django.core.paginator import Paginator
    try:
        entity_type = request.GET.get('type', 'agency')
        query = request.GET.get('q', '')
        sort = request.GET.get('sort', 'date_desc')

        entities = Entity.objects.filter(entity_type=entity_type)
        # Simplify: no search/sort for debug
        paginator = Paginator(entities, 20)
        page = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)

        html = f"<h1>Debug: {entity_type} (Page {page_obj.number})</h1><ul>"
        for e in page_obj:
            html += f"<li>{e.name} - {e.phone}</li>"
        html += "</ul>"
        return HttpResponse(html)
    except Exception as e:
        return HttpResponse(f"<pre>{traceback.format_exc()}</pre>")        