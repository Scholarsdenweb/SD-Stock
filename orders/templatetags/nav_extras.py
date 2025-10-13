from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def active_class(context, starts_with):
    path = context['request'].path
    if path.startswith(starts_with):
        return "active"
    return ""


@register.simple_tag(takes_context=True)
def active_class_end(context, ends_with):
    path = context['request'].path
    if path.endswith(ends_with):
        return "active"
    return ""