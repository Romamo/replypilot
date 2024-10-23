from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group
from django.dispatch import receiver


@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    """
    User signed up with social or local(not confirmed email)
    :param request:
    :param user:
    :param kwargs:
    :return:
    """
    user.is_staff = True
    user.save(update_fields=['is_staff'])

    # Add user to group with name Customer
    group = Group.objects.get(name='Customer')
    user.groups.add(group)
