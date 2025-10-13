from django import template

register = template.Library()

@register.filter
def verbose_name_from_ct(contenttype):
    """
    Given a ContentType object, returns the model's verbose_name.
    Usage: {{ txn.contenttype|verbose_name_from_ct }}
    """
    try:
        return contenttype.model_class()._meta.verbose_name.title()
    except Exception:
        return ""
