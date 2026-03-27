from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('entities/', views.entity_list, name='entity_list'),
    path('entities/add/', views.entity_create, name='entity_create'),
    path('entities/<int:pk>/edit/', views.entity_update, name='entity_update'),
    path('entities/<int:pk>/delete/', views.entity_delete, name='entity_delete'),
    path('client-correction/new/', views.client_correction_create, name='client_correction_create'),
    path('client-correction/list/', views.client_correction_list, name='client_correction_list'),
    path('client-correction/<int:pk>/approve/', views.client_correction_approve, name='client_correction_approve'),
    path('client-correction/<int:pk>/detail/', views.client_correction_detail, name='client_correction_detail'),
    path('knowledge/', views.knowledge_list, name='knowledge_list'),
    path('knowledge/add/', views.knowledge_create, name='knowledge_create'),
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/add/', views.announcement_create, name='announcement_create'),
    path('register/', views.register, name='register'),
    path('create-supervisor/', views.create_supervisor, name='create_supervisor'),
    path('upload-agencies/', views.upload_agencies, name='upload_agencies'),
    path('entities/delete-all/', views.delete_all_entities, name='delete_all_entities'),
    path('debug-entities-db/', views.debug_entities_db, name='debug_entities_db'),
    path('test-paginated/', views.test_paginated, name='test_paginated'),
    path('increase-lengths/', views.increase_lengths, name='increase_lengths'),
    path('upload-ossc/', views.upload_ossc, name='upload_ossc'),
    path('debug-entities/', views.debug_entity_list, name='debug_entities'),    
]       