# Shop_ease/templatetags/extra_filters.py
from django import template

register = template.Library()

@register.filter
def times(value, arg):
    """Multiply two numbers (for template)"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0