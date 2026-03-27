from django.contrib import admin
from .models import User, Entity, ClientCorrection, KnowledgeBase, Announcement

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role',)
    search_fields = ('username', 'email')

class EntityAdmin(admin.ModelAdmin):
    list_display = ('entity_id', 'name', 'entity_type', 'phone')
    search_fields = ('name', 'phone')
    list_filter = ('entity_type',)

class ClientCorrectionAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'agent', 'correction_type', 'phone', 'status', 'created_at')
    list_filter = ('correction_type', 'status')
    search_fields = ('agent__username', 'phone')
    raw_id_fields = ('agent',)

class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('kb_id', 'question', 'category', 'created_by', 'created_at')
    search_fields = ('question', 'answer', 'category')
    list_filter = ('category',)

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('announcement_id', 'title', 'posted_by', 'timestamp')
    search_fields = ('title',)

admin.site.register(User, UserAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(ClientCorrection, ClientCorrectionAdmin)
admin.site.register(KnowledgeBase, KnowledgeBaseAdmin)
admin.site.register(Announcement, AnnouncementAdmin)