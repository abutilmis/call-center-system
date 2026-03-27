from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('entities/', views.entity_list, name='entity_list'),
    path('entities/add/', views.entity_create, name='entity_create'),
    path('entities/<int:pk>/edit/', views.entity_update, name='entity_update'),
    path('entities/<int:pk>/delete/', views.entity_delete, name='entity_delete'),
    path('corrections/', views.correction_list, name='correction_list'),
    path('corrections/add/', views.correction_create, name='correction_create'),
    path('corrections/<int:pk>/approve/', views.correction_approve, name='correction_approve'),
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
]       