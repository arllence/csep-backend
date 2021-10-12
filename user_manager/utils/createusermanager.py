from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

def award_role():
    try:
        record_instances = get_user_model().objects.filter(is_superuser=True)
        for user in record_instances:
            group = Group.objects.get(name='USER_MANAGER')  
            user.groups.add(group)
            print(user.email, " : Awarded Role | USER_MANAGER")
        print("Completed...")
        return True
    except Exception as e:
        print(e)
        return False
