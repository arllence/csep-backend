from django.contrib.auth.models import Group
from user_manager.models import AccountActivity, User
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from django.contrib.auth import get_user_model
import logging
from datetime import date

# # create and configure logger
# loggername = str(date.today())
# logging.basicConfig(
#     filename=f"/opt/logs/utils/{loggername}",
#     format='%(asctim)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s',
#     filemode='a'
# )
# # new logger object
# logger = logging.getLogger()

# # setting threshold of logger
# logger.setLevel(logging.DEBUG)
# Get an instance of a logger
logger = logging.getLogger(__name__)

def fetchusergroups(userid):
    userroles = []
    query_set = Group.objects.filter(user=userid)
    if query_set.count() >= 1:
        for groups in query_set:
            userroles.append(groups.name)
        return userroles
        
    else:
        return ""


def log_account_activity(actor, recipient, activity, remarks):
    create_activity = {
        "recipient": recipient,
        "actor": actor,
        "activity": activity,
        "remarks": remarks,

    }
    new_activity = AccountActivity.objects.create(**create_activity)





def sendmail(recipient,subject,message):
    try:
        message = Mail(
        from_email = settings.EMAIL_HOST,
        to_emails=recipient,
        subject = subject,
        html_content= message )
        sg = SendGridAPIClient(settings.EMAIL_HOST_PASSWORD)
        response = sg.send(message)
        if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
            return True
        else:
            return False
    except Exception as e:
        logger.error(e)
        return False


def award_role(role,account_id):
    excludes = ["CHIEF_EVALUATOR","NONE"]
    if not role:
        return True
    if role in excludes:
        return True
    if account_id in excludes:
        return True
    else:
        role = "LEAD_" + role
    try:
        record_instance = get_user_model().objects.get(id=account_id)
        group = Group.objects.get(name=role)  
        record_instance.groups.add(group)
        return True
    except Exception as e:
        logger.error(e)
        return False

def revoke_role(role,account_id):
    excludes = ["CHIEF_EVALUATOR","NONE"]
    if not role:
        return True
    if role in excludes:
        return True
    if account_id in excludes:
        return True
    else:
        role = "LEAD_" + role        
    try:
        record_instance = get_user_model().objects.get(id=account_id)
        group = Group.objects.get(name=role)  
        record_instance.groups.remove(group)
        return True
    except Exception as e:
        logger.error(e)
        print(e)
        return False


def custom_revoke_role(role,account_id):
    try:
        record_instance = get_user_model().objects.get(id=account_id)
        group = Group.objects.get(name=role)  
        record_instance.groups.remove(group)
        return True
    except Exception as e:
        logger.error(e)
        return False
        


def get_role_by_stage(stage):
    if stage == 'I' or stage == 'II':
        role = 'JUNIOR_OFFICER'
    elif stage == 'III':
        role = 'JUNIOR_OFFICER'
    elif stage == 'IV':
        role = 'INTERNAL_EVALUATOR'
    elif stage == 'V':
        role = 'SUBJECT_MATTER_EVALUATOR'
    elif stage == 'VI':
        role = 'EXTERNAL_EVALUATOR'
    elif stage == 'VII':
        role = 'CHIEF_EVALUATOR'
    else:
        role = None

    return role


def get_role_from_roles(roles):
    role = None
    for item in roles:
        if 'LEAD' not in item:
            if 'CHIEF' not in item:
                role = item
            else:
                role = 'CHIEF_EVALUATOR'
        else:
            if item == 'LEAD_INNOVATION_MANAGER':
                role = 'LEAD_INNOVATION_MANAGER'

    return role