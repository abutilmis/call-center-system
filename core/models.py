from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class User(AbstractUser):
    ROLE_CHOICES = (
        ('agent', 'Agent'),
        ('supervisor', 'Supervisor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='agent')

    # Override groups and user_permissions to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_user_groups',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    def get_absolute_url(self):
        return reverse('dashboard')


class Entity(models.Model):
    ENTITY_TYPES = (
        ('agency', 'Agency'),
        ('tvet', 'TVET'),
        ('ocss', 'OCSS'),
    )
    entity_id = models.AutoField(primary_key=True)
    entity_type = models.CharField(max_length=200, choices=ENTITY_TYPES, default='agency')
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    phone2 = models.CharField(max_length=200, blank=True, null=True)          # new for agency
    city = models.CharField(max_length=200, blank=True, null=True)           # new for agency
    woreda = models.CharField(max_length=200, blank=True, null=True)
    region = models.CharField(max_length=200, blank=True, null=True)         # new for agency
    location = models.CharField(max_length=200, blank=True)
    registration_id = models.CharField(max_length=200, blank=True)
    additional_info = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"

    def get_absolute_url(self):
        return reverse('entity_detail', args=[self.entity_id])


class ClientCorrection(models.Model):
    TYPE_CHOICES = (
        ('name', 'Name'),
        ('dob', 'Date of Birth'),
        ('sex', 'Sex'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    request_id = models.AutoField(primary_key=True)
    correction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    phone = models.CharField(max_length=200)
    labor_id = models.CharField(max_length=200, blank=True)
    old_data = models.JSONField(default=dict)
    new_data = models.JSONField(default=dict)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_corrections')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    supervisor_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.request_id} - {self.get_correction_type_display()} - {self.status}"

    def get_absolute_url(self):
        return reverse('client_correction_detail', args=[self.request_id])


class KnowledgeBase(models.Model):
    kb_id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='knowledge_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question[:50]

    def get_absolute_url(self):
        return reverse('knowledge_detail', args=[self.kb_id])


class Announcement(models.Model):
    announcement_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('announcement_detail', args=[self.announcement_id])