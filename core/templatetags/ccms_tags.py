from django import template
from core.models import ClientCorrection

register = template.Library()

@register.simple_tag(takes_context=True)
def get_pending_corrections_count(context):
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return 0
    user = request.user
    if user.role == 'supervisor':
        return ClientCorrection.objects.filter(status='pending').count()
    return ClientCorrection.objects.filter(agent=user, status='pending').count()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
