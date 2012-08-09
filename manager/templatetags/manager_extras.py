from django import template

register = template.Library()

@register.filter(name='get_current_settings')
def get_current_settings(exercise, set_id):
    """Does a filter on the sets
    
    We need to do this here because it's not possible to pass arguments to function in the template,
    and we are only interested on the settings that belong to the current set
    """
    return exercise.setting_set.filter(sets_id=set_id)