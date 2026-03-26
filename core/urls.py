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
]