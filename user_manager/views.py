import json
import jwt
import random
import re
import app_manager
from rest_framework.views import APIView
from user_manager import serializers
from . import models
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import Permission
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta, date
from user_manager.utils import user_util
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.db import IntegrityError, transaction
from user_manager import models as models
from app_manager import models as app_manager_models
from innovation import models as innovation_models
from user_manager.forms import PictureUploadForm
from string import Template
from email_template import *

def read_template(filename):
    """
    Returns a template object comprising of the contents of the
    file specified by the filename ie messageto client
    """
    with open("email_template/"+filename, 'r', encoding='utf8') as template_file:
        template_file_content = template_file.read()
        return Template(template_file_content)

class AuthenticationViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = models.User.objects.all().order_by('id')
    serializer_class = serializers.SystemUsersSerializer
    search_fields = ['id', ]

    def get_queryset(self):
        return []

    @action(methods=["POST"], detail=False, url_path="login", url_name="login")
    def login_user(self, request):
        payload = request.data
        # print(payload)
        email = request.data.get('email')
        password = request.data.get('password')
        if email is None:
            return Response({"details": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        if password is None:
            return Response({"details": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
        input_email = payload['email']
        input_password = payload['password']
        
        is_authenticated = authenticate(
            email=input_email, password=input_password)

        if is_authenticated: 
            last_password_reset = is_authenticated.last_password_reset
            now_date = datetime.now(timezone.utc)
            # last_reset = (now_date - last_password_reset).days
         
            # if last_reset >= 30:
            #     change_password = True
            # else:
            #     change_password = is_authenticated.is_defaultpassword
            
            verified_email = is_authenticated.verified_email
            if not verified_email:
                response_info = {
                    'verified_email': False,
                    'email': is_authenticated.email
                }
                return Response(response_info, status=status.HTTP_200_OK)

            is_suspended = is_authenticated.is_suspended
            if is_suspended is True or is_suspended is None:
                return Response({"details": "Your Account Has Been Suspended,Contact Admin"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                completed_profile = models.CompletedProfile.objects.filter(user=is_authenticated).exists()
                payload = {
                    'id': str(is_authenticated.id),
                    'email': is_authenticated.email,
                    'name': is_authenticated.first_name,
                    'first_name': is_authenticated.first_name,
                    'last_name': is_authenticated.last_name,
                    # 'password_change_status': change_password,
                    "verified_email": is_authenticated.verified_email,
                    "completed_profile":completed_profile,
                    'superuser': is_authenticated.is_superuser,
                    'exp': datetime.utcnow() + timedelta(seconds=settings.TOKEN_EXPIRY),
                    'iat': datetime.utcnow()
                }
                # print(payload)
                
                token = jwt.encode(payload, settings.TOKEN_SECRET_CODE)
                response_info = {
                    "token": token,
                    # "change_password": change_password,
                    "verified_email": is_authenticated.verified_email
                }
                return Response(response_info, status=status.HTTP_200_OK)
        else:
            return Response({"details": "Invalid Email / Password"}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-account", url_name="create-account")
    def create_account(self, request):
        payload = request.data
        # print(payload)
        serializer = serializers.CreateUserSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                email = payload['email']
                first_name = payload['first_name']
                last_name = payload['last_name']
                register_as = payload['register_as']
                hear_about_us = payload['hear_about_us']
                hear_about_us_other = payload['hear_about_us_other']
                newsletter = payload['newsletter']
                accepted_terms = payload['accepted_terms']
                password = payload['password']
                confirm_password = payload['confirm_password']
                userexists = get_user_model().objects.filter(email=email).exists()

                if userexists:
                    return Response({'details': 'User With Credentials Already Exist'}, status=status.HTTP_400_BAD_REQUEST)

               
                password_min_length = 8

                string_check= re.compile('[-@_!#$%^&*()<>?/\|}{~:]') 

                if(password != confirm_password): 
                    return Response({'details':
                                     'Passwords Not Matching'},
                                    status=status.HTTP_400_BAD_REQUEST)

                if(string_check.search(password) == None): 
                    return Response({'details':
                                     'Password Must contain a special character'},
                                    status=status.HTTP_400_BAD_REQUEST)

                if not any(char.isupper() for char in password):
                    return Response({'details':
                                     'Password must contain at least 1 uppercase letter'},
                                    status=status.HTTP_400_BAD_REQUEST)

                if len(password) < password_min_length:
                    return Response({'details':
                                     'Password Must be atleast 8 characters'},
                                    status=status.HTTP_400_BAD_REQUEST)

                if not any(char.isdigit() for char in password):
                    return Response({'details':
                                     'Password must contain at least 1 digit'},
                                    status=status.HTTP_400_BAD_REQUEST)
                                    
                if not any(char.isalpha() for char in password):
                    return Response({'details':
                                     'Password must contain at least 1 letter'},
                                    status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    group_details = Group.objects.get(id=register_as)
                except (ValidationError, ObjectDoesNotExist):
                    return Response({'details': 'Role does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                
                is_superuser = False
                if group_details.name == "SUPERUSER":
                    is_superuser = True
                

                hashed_pwd = make_password(password)
                newuser = {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "hear_about_us": hear_about_us,
                    "hear_about_us_other": hear_about_us_other,
                    "newsletter": newsletter,
                    "accepted_terms": accepted_terms,
                    "register_as": register_as,
                    "is_active": True,
                    "is_superuser": is_superuser,
                    "password": hashed_pwd,
                }
                create_user = get_user_model().objects.create(**newuser)
                group_details.user_set.add(create_user)
                user_util.log_account_activity(
                    create_user, create_user, "Account Creation",
                    "USER CREATED")

                try:
                    recipient = create_user.email
                    name = create_user.first_name
                    subject = "Activate Your IEN-AFRICA Account"
                    otp = random.randint(1000,100000)
                    print("otp: ", otp)
                    message_template = read_template("activation_email.html")
                    message = message_template.substitute(NAME=name, OTP=otp)
                    # print(message)
                    # message =f'Hi {name}, thanks for joining us, \njust one more step.\n Here is your OTP verification code: {otp}'
                    try:
                        existing_otp = models.OtpCodes.objects.get(recipient=create_user)
                        existing_otp.delete()
                    except Exception as e:
                        print(e)
                    models.OtpCodes.objects.create(recipient=create_user,otp=otp)
                    user_util.sendmail(recipient,subject,message)
                except Exception as e:
                    print(e)
                info = {
                    'email': email
                }
                return Response(info, status=status.HTTP_200_OK)

        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["POST"], detail=False, url_path="verify-email", url_name="verify-email")
    def verify_email(self, request):
        payload = request.data

        serializer = serializers.OtpSerializer(data=payload, many=False)

        if serializer.is_valid():
            with transaction.atomic():
                otp = payload['otp']
                email = payload['email']
                try:
                    check = models.OtpCodes.objects.get(otp=otp)
                    user = get_user_model().objects.get(email=email)
                    user.verified_email = True
                    user.save()
                    check.delete()
                    return Response('Success', status=status.HTTP_200_OK)
                except Exception as e:
                    print(e)
                    return Response({'details':
                                     'Incorrect OTP Code'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path="send-password-reset-link",url_name="send-password-reset-link")
    def send_password_reset_link(self, request):
        payload = request.data
        serializer = serializers.UserEmailSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                email = payload['email']
                serverurl = payload['serverurl']
                try:
                    user_details = get_user_model().objects.get(email=email)
                except (ValidationError, ObjectDoesNotExist):
                    return Response({'details': 'Email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    existing_otp = models.OtpCodes.objects.get(recipient=user_details)
                    otp = existing_otp.otp
                except Exception as e:
                    otp = random.randint(1000,100000) 
                    models.OtpCodes.objects.create(recipient=user_details,otp=otp)

                               
                subject = "Password Reset | IEN-AFRICA"
                link = serverurl + "?otp=" + str(otp) + "&email=" + email
                # message = f"Hello {user_details.first_name}, \nClick this link to reset your password: {link}"

                message_template = read_template("reset_password.html")
                message = message_template.substitute(NAME=user_details.first_name, LINK=link)
                
                # print(message)
                # send mail
                mail=user_util.sendmail(email,subject,message)

                user_util.log_account_activity(
                    user_details, user_details, "Sent Password Reset Link", "Password Reset Link Sent")
                return Response("Password Reset Successful", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["POST"], detail=False, url_path="reset-user-password", url_name="reset-user-password")
    def reset_user_password(self, request):
        payload = request.data
        print(payload)
        serializer = serializers.UserPasswordChangeSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                email = payload['email']
                otp = payload['otp']
                password = payload['password']
                confirm_password = payload['confirm_password']

                try:
                    userInstance = get_user_model().objects.get(email=email)
                except Exception as e:
                    print(e)
                    return Response({'details': "User Doesn't Exist"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    existing_otp = models.OtpCodes.objects.get(recipient=userInstance,otp=otp)
                    existing_otp.delete()
                except Exception as e:
                    print(e)
                    return Response({'details': "Incorrect Verification Code"}, status=status.HTTP_400_BAD_REQUEST)
               
                password_min_length = 8

                string_check= re.compile('[-@_!#$%^&*()<>?/\|}{~:]') 

                if(password != confirm_password): 
                    return Response({'details':'Passwords Not Matching'},status=status.HTTP_400_BAD_REQUEST)

                if(string_check.search(password) == None): 
                    return Response({'details':'Password Must contain a special character'},status=status.HTTP_400_BAD_REQUEST)

                if not any(char.isupper() for char in password):
                    return Response({'details':'Password must contain at least 1 uppercase letter'},status=status.HTTP_400_BAD_REQUEST)

                if len(password) < password_min_length:
                    return Response({'details':'Password Must be atleast 8 characters'},status=status.HTTP_400_BAD_REQUEST)

                if not any(char.isdigit() for char in password):
                    return Response({'details':'Password must contain at least 1 digit'},status=status.HTTP_400_BAD_REQUEST)
                                    
                if not any(char.isalpha() for char in password):
                    return Response({'details':'Password must contain at least 1 letter'},status=status.HTTP_400_BAD_REQUEST)


                hashed_pwd = make_password(password)
                userInstance.password = hashed_pwd
                userInstance.save()


                user_util.log_account_activity(
                    userInstance, userInstance, "Password Reset","Password reset")

                return Response("success", status=status.HTTP_200_OK)

        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["POST"], detail=False, url_path="resend-otp", url_name="resend-otp")
    def resend_otp(self, request):
        payload = request.data
        print(payload)

        serializer = serializers.ResendOtpSerializer(data=payload, many=False)

        if serializer.is_valid():
            with transaction.atomic():
                email = payload['email']
                                
                try:
                    user = get_user_model().objects.get(email=email)
                    recipient = user.email
                    name = user.first_name
                    subject = "Activate Your IEN-AFRICA Account"
                    otp = random.randint(1000,100000)
                    print(otp)
                    # message =f"Hi {name}, thanks for joining us \nJust one more step...\nHere is your OTP verification code: {otp}"
                    message_template = read_template("activation_email.html")
                    message = message_template.substitute(NAME=name, OTP=otp)
                    try:
                        existing_otp = models.OtpCodes.objects.get(recipient=user)
                        existing_otp.delete()
                    except Exception as e:
                        print(e)
                    models.OtpCodes.objects.create(recipient=user,otp=otp)
                    mail=user_util.sendmail(recipient,subject,message)
                    return Response('success', status=status.HTTP_200_OK)
                except Exception as e:
                    print(e)
                    return Response({'details':'Error. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    
   



class AccountManagementViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,JSONParser)
    queryset = models.User.objects.all().order_by('id')
    serializer_class = serializers.SystemUsersSerializer
    search_fields = ['id', ]

    def get_queryset(self):
        return []

    @action(methods=["GET"], detail=False, url_path="check-completed-profile", url_name="check-completed-profile")
    def check_completed_profile(self, request):
        user_id = request.user.id
        roles = user_util.fetchusergroups(user_id)
        if 'INNOVATOR' in roles:
            if user_id:
                check = models.CompletedProfile.objects.filter(user=user_id).exists()
                info = {
                    "status": check
                }
                return Response(info, status=status.HTTP_200_OK)
            else:
                return Response({'details':'Invalid User'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": True}, status=status.HTTP_200_OK)


    # @action(methods=["POST"], detail=False, url_path="verify-email", url_name="verify-email")
    # def verify_email(self, request):
    #     payload = request.data

    #     serializer = serializers.OtpSerializer(data=payload, many=False)

    #     if serializer.is_valid():
    #         with transaction.atomic():
    #             otp = payload['otp']
    #             print(otp)
    #             try:
    #                 check = models.OtpCodes.objects.get(otp=otp)
    #                 user = get_user_model().objects.get(id=request.user.id)
    #                 user.verified_email = True
    #                 user.save()
    #                 check.delete()

    #                 payload = {
    #                 'id': str(user.id),
    #                 'email': user.email,
    #                 'name': user.first_name,
    #                 "verified_email": user.verified_email,
    #                 'superuser': user.is_superuser,
    #                 'exp': datetime.utcnow() + timedelta(seconds=settings.TOKEN_EXPIRY),
    #                 'iat': datetime.utcnow()
    #                 }
                
    #                 token = jwt.encode(payload, settings.TOKEN_SECRET_CODE)
    #                 info = {
    #                     "token": token
    #                 }
    #                 return Response(info, status=status.HTTP_200_OK)
    #             except Exception as e:
    #                 print(e)
    #                 return Response({'details':
    #                                  'Incorrect OTP Code'},
    #                                 status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-profile", url_name="create-profile")
    def create_profile(self, request):
        payload = request.data
        authenticated_user = request.user

        # print(payload)

        serializer = serializers.CreateProfileSerializer(data=payload, many=False)
        if serializer.is_valid():
            for key in payload:
                if not payload[key]:
                    payload[key] = None
            with transaction.atomic():
                email = payload['email']
                first_name = payload['first_name'].capitalize()
                last_name = payload['last_name'].capitalize()
                phone = str(payload['phone'])
                phonecode = payload['phonecode']
                # id_number = payload['id_number']
                gender = payload['gender']
                age_group = payload['age_group']
                disability = payload['disability']
                country = payload['country']
                bio = payload['bio']
                state = payload['state'].capitalize()
                city = payload['city'].capitalize()
                address = payload['address']
                postal = payload['postal']
                employment = payload['employment']
                skills = payload['skills']
                try:
                    level_of_education = payload['level_of_education']
                    print(level_of_education)
                except Exception as e:
                    level_of_education = None
                    print("level_of_education: ",e)
                try:
                    institution_name = payload['institution_name']
                    course_name = payload['course_name']
                    study_summary = payload['study_summary']
                except Exception as e:
                    institution_name = None
                    course_name = None
                    study_summary = None
                    print(e)
                

                authenticated_user.first_name = first_name
                authenticated_user.last_name = last_name
                authenticated_user.save()

                if phonecode:
                    if phonecode[0] != '+':
                        phonecode = '+' + phonecode

                    if phone[0] == '0':
                        phone = phone[1:]
                    
                    if phone[0] != '+':
                        phone = phonecode + '-' + phone
                    else:
                        try:
                            phone = phone.split('-')
                            code, number = phone
                            phone = phonecode + '-' + number
                        except Exception as e:
                            print(e)
                            

                


                education = {
                    "user": authenticated_user,
                    "institution_name" : institution_name,
                    "course_name" : course_name,
                    "study_summary" : study_summary,
                }
                is_underage = False
                if age_group == "14-17":
                    is_underage = True
                    guardian_details = {
                        "name" : payload['guardian_name'],
                        "id_number" : payload['guardian_id_number'],
                        "contact" : payload['guardian_contact']
                    }
                    for key in guardian_details:
                        if not guardian_details[key]:
                            return Response({'details':"Guardian Details Required"}, status=status.HTTP_400_BAD_REQUEST)

                user_exists = models.CompletedProfile.objects.filter(user=authenticated_user).exists()
                if user_exists:
                    user_profile = models.UserInfo.objects.get(user=authenticated_user)
                    user_profile.phone = phone
                    # user_profile.id_number = id_number
                    user_profile.age_group = age_group
                    user_profile.disability = disability
                    user_profile.country = country
                    user_profile.bio = bio
                    user_profile.state = state
                    user_profile.city = city
                    user_profile.physical_address = address
                    user_profile.postal_code = postal
                    user_profile.education_level = level_of_education
                    user_profile.employment = employment

                    user_profile.save()

                    if is_underage:
                        models.Guardian.objects.filter(user=authenticated_user).update(**guardian_details)

                    current_skills = models.Skills.objects.filter(user=authenticated_user)
                    all_skills = []
                    for skill in current_skills:
                        all_skills.append(skill.name)

                    for skill in skills:
                        if skill not in all_skills:
                            to_create = {
                                "user": authenticated_user,
                                "name" : skill
                            }

                            models.Skills.objects.create(**to_create)
                    
                    try:
                        education = models.Education.objects.get(user=authenticated_user)
                        education.institution_name = institution_name 
                        education.course_name = course_name
                        # education.grade = grade
                        education.study_summary = study_summary
                        education.save()
                    except Exception as e:
                        print(e)
                        if level_of_education:
                            models.Education.objects.create(**education)

                    
                else:
                    profile = {
                        "user": authenticated_user,
                        "gender": gender,
                        "phone": phone,
                        # "id_number": id_number,
                        "age_group": age_group,
                        "disability": disability,
                        "country": country,
                        "bio": bio,
                        "state": state,
                        "city": city,
                        "physical_address": address,
                        "postal_code": postal,
                        "education_level": level_of_education,
                        "employment_status": employment
                    }
                    models.UserInfo.objects.create(**profile)
                    if is_underage:
                        guardian_details.update({"user": authenticated_user})
                        models.Guardian.objects.create(**guardian_details)

                    for skill in skills:
                        to_create = {
                            "user": authenticated_user,
                            "name" : skill
                        }
                        models.Skills.objects.create(**to_create)

                    
                    # save education details
                    if level_of_education:
                        models.Education.objects.create(**education)
                    # save completed profile status
                    models.CompletedProfile.objects.create(user=authenticated_user)

                return Response("succees", status=status.HTTP_200_OK)
        else:
            return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], detail=False, url_path="user-profile", url_name="user-profile")
    def user_profile(self, request):
        authenticated_user = request.user
        try:
            serializer = serializers.UserProfileSerializer(authenticated_user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'details':'Error Geting Profile'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-certification", url_name="create-certification")
    def create_certification(self, request):
        payload = request.data
        authenticated_user = request.user

        # print(payload)

        serializer = serializers.CreateCertificationSerializer(data=payload, many=False)
        if serializer.is_valid():
            for key in payload:
                if not payload[key]:
                    payload[key] = None
            with transaction.atomic():
                name = payload['name']
                expiration_date = payload['expiration_date']    

                cert_id = None
                try:
                    cert_id = payload['cert_id']  
                except Exception as e:
                    pass  

                if cert_id:
                    cert = models.Certification.objects.get(id=cert_id) 
                    cert.name=name 
                    cert.expiration_date=expiration_date
                    cert.save()
                else:        
                    raw = {
                        "user": authenticated_user,
                        "name" : name,
                        "expiration_date" : expiration_date
                    }
                    models.Certification.objects.create(**raw) 

                return Response("succees", status=status.HTTP_200_OK)
        else:
            return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="get-certifications", url_name="get-certifications")
    def get_certifications(self, request):
        authenticated_user = request.user
        try:
            data = models.Certification.objects.filter(user=authenticated_user, status=True).order_by('-date_created')
            serializer = serializers.CertificationSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'details':'Error Geting Certifications'},status=status.HTTP_400_BAD_REQUEST)

    


    @action(methods=["POST"], detail=False, url_path="delete-certification", url_name="delete-certification")
    def delete_certification(self, request):
        payload = request.data
        authenticated_user = request.user

        serializer = serializers.DeleteCertificationSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                cert_id = payload['cert_id']

                cert = models.Certification.objects.get(id=cert_id)
                cert.status = False
                cert.save()
                return Response('success', status=status.HTTP_200_OK)
        else:
            return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
    # ASSOCIATION
    
    @action(methods=["POST"], detail=False, url_path="create-association", url_name="create-association")
    def create_association(self, request):
        payload = request.data
        authenticated_user = request.user
        print(payload)

        # try:

        #     payload['expiration'] = datetime.now().strftime('%Y-%m-%d')
        #     print(payload['expiration'])
        # except Exception as e:
        #     print(e)

        serializer = serializers.CreateAssociationSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                name = payload['name']
                role = payload['role']    
                expiration = payload['expiration']    
                certificate_id = payload['certificate']  

                try:
                    certificate = models.Document.objects.get(id=certificate_id)
                except Exception as e:
                    return Response({'details':'No Certificate Uploaded'}, status=status.HTTP_400_BAD_REQUEST)

                association_id = None
                try:
                    association_id = payload['association_id']  
                except Exception as e:
                    pass  

                if association_id:
                    association = models.Association.objects.get(id=association_id) 
                    association.name=name 
                    association.role=role
                    association.expiration=expiration
                    association.document=certificate
                    association.save()
                else:        
                    raw = {
                        "user": authenticated_user,
                        "name" : name,
                        "role" : role,
                        "expiration": expiration,
                        "document": certificate
                    }
                    models.Association.objects.create(**raw) 

                return Response("succees", status=status.HTTP_200_OK)
        else:
            return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="get-associations", url_name="get-associations")
    def get_association(self, request):
        authenticated_user = request.user
        try:
            data = models.Association.objects.filter(user=authenticated_user, status=True).order_by('-date_created')
            serializer = serializers.AssociationSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'details':'Error Geting Associations'},status=status.HTTP_400_BAD_REQUEST)
  


    @action(methods=["POST"], detail=False, url_path="delete-association", url_name="delete-association")
    def delete_association(self, request):
        payload = request.data

        serializer = serializers.DeleteAssociationSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                association_id = payload['association_id']

                association = models.Association.objects.get(id=association_id)
                association.status = False
                association.save()
                return Response('success', status=status.HTTP_200_OK)
        else:
            return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                

    # HOBBY
    
    @action(methods=["POST"], detail=False, url_path="create-hobby", url_name="create-hobby")
    def create_hobby(self, request):
        payload = request.data
        authenticated_user = request.user

        serializer = serializers.CreateHobbySerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                name = payload['name']  

                hobby_id = None
                try:
                    hobby_id = payload['hobby_id']  
                except Exception as e:
                    pass  

                if hobby_id:
                    hobby = models.Hobby.objects.get(id=hobby_id) 
                    hobby.name=name 
                    hobby.save()
                else:        
                    raw = {
                        "user": authenticated_user,
                        "name" : name
                    }
                    models.Hobby.objects.create(**raw) 

                return Response("succees", status=status.HTTP_200_OK)
        else:
            return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="get-hobbies", url_name="get-hobbies")
    def get_hobbies(self, request):
        authenticated_user = request.user
        try:
            data = models.Hobby.objects.filter(user=authenticated_user, status=True).order_by('-date_created')
            serializer = serializers.HobbySerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'details':'Error Geting Hobbies'},status=status.HTTP_400_BAD_REQUEST)
  


    @action(methods=["POST"], detail=False, url_path="delete-hobby", url_name="delete-hobby")
    def delete_hobby(self, request):
        payload = request.data

        serializer = serializers.DeleteHobbySerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                hobby_id = payload['hobby_id']

                hobby = models.Hobby.objects.get(id=hobby_id)
                hobby.status = False
                hobby.save()
                return Response('success', status=status.HTTP_200_OK)
        else:
            return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                


    @action(methods=["POST"], detail=False, url_path="upload-document", url_name="upload-document")
    def upload_document(self, request):
        auth_user = request.user
        form = PictureUploadForm(request.POST, request.FILES)
        upload_status = False
        document_type = request.data['documentType']
        try:
            checker = request.data['checker']
        except:
            checker = None

        if form.is_valid():
            with transaction.atomic():
                uploaded_files = []
                not_uploaded_files = []
                for f in request.FILES.getlist('document'):
                    original_file_name = f.name
                    if document_type == 'profile_picture':
                        original_file_exists = models.ProfilePicture.objects.filter(
                            original_file_name=original_file_name).exists()
                    elif checker == "INNOVATION":
                        original_file_exists = innovation_models.InnovationDocument.objects.filter(
                            original_file_name=original_file_name).exists()
                    else:
                        original_file_exists = models.Document.objects.filter(
                            original_file_name=original_file_name).exists()
                    if original_file_exists:
                        upload_status = False
                        not_uploaded_files.append(
                            {"name": str(original_file_name), "reason": "File already exists"})

                    else:
                        uploaded_files.append({"name": str(original_file_name)})
                        upload_status = True
                        loggedin_user = request.user
                        if  document_type == 'profile_picture':
                            old_pictures = models.ProfilePicture.objects.filter(user=auth_user.id)
                            if old_pictures:
                                for picture in old_pictures:
                                    picture.status = False
                                    picture.save()
                            newinstance = models.ProfilePicture.objects.create(
                                profile_picture=f, user=loggedin_user, original_file_name=original_file_name, status=True)
                            url = newinstance.profile_picture.url
                            info = {
                                    "url_link" : url
                                }
                        else:
                            if checker == "INNOVATION":
                                title_obj = app_manager_models.IntellectualProperty.objects.get(id=document_type)
                                title = title_obj.name
                                innovation = request.data['innovation']
                                innovation = innovation_models.Innovation.objects.get(id=innovation)
                                exists = innovation_models.InnovationDocument.objects.filter(innovation=innovation,title=title)
                                if exists:
                                    fileInstance = exists.first()
                                    fileInstance.document=f
                                    fileInstance.innovation=innovation
                                    fileInstance.original_file_name=original_file_name
                                    fileInstance.title=title
                                    fileInstance.save()
                                else:
                                    newinstance = innovation_models.InnovationDocument.objects.create(
                                        document=f, innovation=innovation, original_file_name=original_file_name,title=title)
                                info = {
                                    "success" : "success"
                                }
                            else:
                                newinstance = models.Document.objects.create(
                                    document=f, user=loggedin_user, original_file_name=original_file_name, document_type=document_type)
                                url = newinstance.document.url
                                doc_id = newinstance.id
                                info = {
                                    "url_link" : url,
                                    "doc_id": doc_id
                                }
                if upload_status is True:
                    return Response(info, status=status.HTTP_200_OK)
                else:
                    return Response({"details": "File Already Exists"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"details": "Invalid file passed"}, status=status.HTTP_400_BAD_REQUEST)

    
    # @action(methods=["POST"], detail=False, url_path="resend-otp", url_name="resend-otp")
    # def resend_otp(self, request):
    #     payload = request.data

    #     serializer = serializers.OtpSerializer(data=payload, many=False)

    #     if serializer.is_valid():
    #         with transaction.atomic():
    #             otp = payload['otp']
                                
    #             try:
    #                 user = request.user
    #                 recipient = user.email
    #                 name = user.first_name
    #                 subject = "Activate Your IEN-AFRICA Account"
    #                 otp = random.randint(1000,100000)
    #                 message =f"Hi {name}, thanks for joining us \nJust one more step...\nHere is your OTP verification code: {otp}"
    #                 try:
    #                     existing_otp = models.OtpCodes.objects.get(recipient=user)
    #                     existing_otp.delete()
    #                 except Exception as e:
    #                     print(e)
    #                 print(message)
    #                 models.OtpCodes.objects.create(recipient=user,otp=otp)
    #                 mail=user_util.sendmail(recipient,subject,message)
    #             except Exception as e:
    #                 print(e)
    #             return Response('success', status=status.HTTP_200_OK)


    @action(methods=["POST"], detail=False, url_path="change-password", url_name="change-password")
    def change_password(self, request):
        authenticated_user = request.user
        payload = request.data

        serializer = serializers.PasswordChangeSerializer(
            data=payload, many=False)

        if serializer.is_valid():
            with transaction.atomic():
                new_password = payload['new_password']
                confirm_password = payload['confirm_password']
                current_password = payload['current_password']
                password_min_length = 8

                string_check= re.compile('[-@_!#$%^&*()<>?/\|}{~:]') 

                if(string_check.search(new_password) == None): 
                    return Response({'details':
                                     'Password Must contain a special character'},
                                    status=status.HTTP_400_BAD_REQUEST)

                if not any(char.isupper() for char in new_password):
                    return Response({'details':
                                     'Password must contain at least 1 uppercase letter'},
                                    status=status.HTTP_400_BAD_REQUEST)

                if len(new_password) < password_min_length:
                    return Response({'details':
                                     'Password Must be atleast 8 characters'},
                                    status=status.HTTP_400_BAD_REQUEST)

                if not any(char.isdigit() for char in new_password):
                    return Response({'details':
                                     'Password must contain at least 1 digit'},
                                    status=status.HTTP_400_BAD_REQUEST)
                                    
                if not any(char.isalpha() for char in new_password):
                    return Response({'details':
                                     'Password must contain at least 1 letter'},
                                    status=status.HTTP_400_BAD_REQUEST)
                try:
                    user_details = get_user_model().objects.get(id=authenticated_user.id)
                except (ValidationError, ObjectDoesNotExist):
                    return Response({'details': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                # check if new password matches current password
                encoded = user_details.password
                check_pass = check_password(new_password, encoded)
                if check_pass:
                    return Response({'details': 'New password should not be the same as old passwords'}, status=status.HTTP_400_BAD_REQUEST)


                if new_password != confirm_password:
                    return Response({"details": "Passwords Do Not Match"}, status=status.HTTP_400_BAD_REQUEST)
                is_current_password = authenticated_user.check_password(
                    current_password)
                if is_current_password is False:
                    return Response({"details": "Invalid Current Password"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user_util.log_account_activity(
                        authenticated_user, user_details, "Password Change", "Password Change Executed")
                    existing_password = authenticated_user.password
                    user_details.is_defaultpassword = False
                    new_password_hash = make_password(new_password)
                    user_details.password = new_password_hash
                    user_details.last_password_reset = datetime.now()
                    user_details.save()
                    return Response("Password Changed Successfully", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="list-users-with-role", url_name="list-users-with-role")
    def list_users_with_role(self, request):
        authenticated_user = request.user
        role_name = request.query_params.get('role_name')
        if role_name is None:
            return Response({'details': 'Role is Required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            role = Group.objects.get(name=role_name)
        except (ValidationError, ObjectDoesNotExist):
            return Response({'details': 'Role does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        selected_users = get_user_model().objects.filter(groups__name=role.name)
        user_info = serializers.UsersSerializer(selected_users, many=True)
        return Response(user_info.data, status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="get-account-activity", url_name="get-account-activity")
    def get_account_activity(self, request):
        authenticated_user = request.user
        account_id = request.query_params.get('account_id')
        if account_id is None:
            return Response({'details': 'Account ID is Required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            account_instance = get_user_model().objects.get(id=account_id)
        except (ValidationError, ObjectDoesNotExist):
            return Response({'details': 'Account does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        selected_records = []
        if hasattr(account_instance, 'user_account_activity'):
            selected_records = account_instance.user_account_activity.all()
        user_info = serializers.AccountActivitySerializer(
            selected_records, many=True)
        return Response(user_info.data, status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="get-account-activity-detail", url_name="get-account-activity-detail")
    def get_account_activity_detail(self, request):
        authenticated_user = request.user
        request_id = request.query_params.get('request_id')
        if request_id is None:
            return Response({'details': 'Request ID is Required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            account_activity_instance = models.AccountActivity.objects.get(
                id=request_id)
        except (ValidationError, ObjectDoesNotExist):
            return Response({'details': 'Request does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        account_info = serializers.AccountActivityDetailSerializer(
            account_activity_instance, many=False)
        return Response(account_info.data, status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="list-roles", url_name="list-roles")
    def list_roles(self, request):
        role = Group.objects.all()
        record_info = serializers.RoleSerializer(role, many=True)
        return Response(record_info.data, status=status.HTTP_200_OK)
    
    @action(methods=["GET"], detail=False, url_path="fetch-roles", url_name="fetch-roles")
    def fetch_roles(self, request):
        stage = request.query_params.get('role')
        
        if stage == 'I' or stage == 'II':
            role_name = 'JUNIOR_OFFICER'
        elif stage == 'III':
            role_name = 'INTERNAL_EVALUATOR'
        elif stage == 'IV':
            role_name = 'SUBJECT_MATTER_EVALUATOR'
        elif stage == 'V':
            role_name = 'EXTERNAL_EVALUATOR'

        print(role_name)
        role = Group.objects.filter(name=role_name)
        # for r in role:
        print(role)
        record_info = serializers.RoleSerializer(role, many=True)
        return Response(record_info.data, status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="list-user-roles", url_name="list-user-roles")
    def list_user_roles(self, request):
        authenticated_user = request.user
        role = user_util.fetchusergroups(authenticated_user.id)
        rolename = {
            "group_name": role
        }
        return Response(rolename, status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="get-user-details", url_name="get-user-details")
    def get_user_details(self, request):
        authenticated_user = request.user
        user_id = request.query_params.get('user_id')
        if user_id is None:
            return Response({'details': 'Invalid Filter Criteria'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_details = get_user_model().objects.get(id=user_id)
        except (ValidationError, ObjectDoesNotExist):
            return Response({'details': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        user_info = serializers.UsersSerializer(user_details, many=False)
        return Response(user_info.data, status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="filter-by-email", url_name="filter-by-email")
    def filter_by_email(self, request):
        authenticated_user = request.user
        email = request.query_params.get('email')
        if email is None:
            return Response({'details': 'Invalid Filter Criteria'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_details = get_user_model().objects.filter(email__icontains=email)
        except (ValidationError, ObjectDoesNotExist):
            return Response({'details': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        user_info = serializers.UsersSerializer(user_details, many=True)
        return Response(user_info.data, status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="fetch-users", url_name="fetch-users")
    def fetch_users(self, request):
        users = get_user_model().objects.all()
        user_info = serializers.UsersSerializer(users, many=True)        
        return Response(user_info.data, status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="get-profile-details", url_name="get-profile-details")
    def get_profile_details(self, request):
        authenticated_user = request.user
        payload = request.data
        try:
            user_details = get_user_model().objects.get(id=authenticated_user.id)
        except (ValidationError, ObjectDoesNotExist):
            return Response({'details': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        user_info = serializers.UsersSerializer(user_details, many=False)
        return Response(user_info.data, status=status.HTTP_200_OK)




class SuperUserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.User.objects.all().order_by('id')
    serializer_class = serializers.SystemUsersSerializer
    search_fields = ['id', ]

    def get_queryset(self):
        return []

    @action(methods=["POST"], detail=False, url_path="reset-user-password",url_name="reset-user-password")
    def reset_user_password(self, request):
        authenticated_user = request.user
        payload = request.data
        serializer = serializers.UserIdSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                userid = payload['user_id']
                try:
                    user_details = get_user_model().objects.get(id=userid)
                except (ValidationError, ObjectDoesNotExist):
                    return Response({'details': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                new_password = str(user_details.email)
                hashed_password = make_password(new_password)
                user_details.password = hashed_password
                user_details.is_defaultpassword = True
                user_details.save()
                user_util.log_account_activity(
                    authenticated_user, user_details, "Password Reset", "Password Reset Executed")
                return Response("Password Reset Successful", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="edit-user",url_name="edit-user")
    def edit_user(self, request):
        payload = request.data
        # print(payload)
        serializer = serializers.EditUserSerializer(data=payload, many=False)
        if serializer.is_valid():
            # email = payload['email']
            first_name = payload['first_name']
            last_name = payload['last_name']
            # phone_number = payload['phone_number']
            # gender = payload['gender']
            # register_as = payload['register_as']
            account_id = payload['account_id']

            try:
                record_instance = get_user_model().objects.get(id=account_id)
            except (ValidationError, ObjectDoesNotExist):
                return Response(
                    {'details': 'User does not exist'},
                    status=status.HTTP_400_BAD_REQUEST)

            record_instance.first_name = first_name
            record_instance.last_name = last_name
            # record_instance.email = email
            # record_instance.phone_number = phone_number
            # record_instance.gender = gender
            # record_instance.register_as = register_as
            record_instance.save()

            return Response("Successfully Updated",
                            status=status.HTTP_200_OK)

        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path="award-role", url_name="award-role")
    def award_role(self, request):
        payload = request.data
        authenticated_user = request.user
        serializer = serializers.ManageRoleSerializer(data=payload, many=False)
        if serializer.is_valid():
            role_id = payload['role_id']
            account_id = payload['account_id']
            if not role_id:
                return Response(
                    {'details': 'Select atleast one role'},
                    status=status.HTTP_400_BAD_REQUEST)

            try:
                record_instance = get_user_model().objects.get(id=account_id)
            except (ValidationError, ObjectDoesNotExist):
                return Response(
                    {'details': 'Invalid User'},
                    status=status.HTTP_400_BAD_REQUEST)

            group_names = []

            for assigned_role in role_id:
                group = Group.objects.get(id=assigned_role)
                group_names.append(group.name)

                record_instance.groups.add(group)
            # user_util.log_account_activity(
            #     authenticated_user, record_instance, "Role Assignment",
            #     "USER ASSIGNED ROLES {{i}}".format(group_names))
            return Response("Successfully Updated",
                            status=status.HTTP_200_OK)

        else:
            return Response({"details": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path="revoke-role", url_name="revoke-role")
    def revoke_role(self, request):
        payload = request.data
        authenticated_user = request.user
        serializer = serializers.ManageRoleSerializer(data=payload, many=False)
        if serializer.is_valid():
            role_id = payload['role_id']
            account_id = payload['account_id']
            if not role_id:
                return Response(
                    {'details': 'Select atleast one role'},
                    status=status.HTTP_400_BAD_REQUEST)

            try:
                record_instance = get_user_model().objects.get(id=account_id)
            except (ValidationError, ObjectDoesNotExist):
                return Response(
                    {'details': 'Invalid User'},
                    status=status.HTTP_400_BAD_REQUEST)

            group_names = []

            for assigned_role in role_id:
                group = Group.objects.get(id=assigned_role)
                group_names.append(group.name)
                record_instance.groups.remove(group)

            user_util.log_account_activity(
                authenticated_user, record_instance, "Role Revokation",
                "USER REVOKED ROLES {{i}}".format(group_names))

            return Response("Successfully Updated",
                            status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def password_generator(self):
        # generate password
        lower = "abcdefghijklmnopqrstuvwxyz"
        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numbers = "0123456789"
        symbols = "[}{$@]!?"

        sample_lower = random.sample(lower,2)
        sample_upper = random.sample(upper,2)
        sample_numbers = random.sample(numbers,2)
        sample_symbols = random.sample(symbols,2)

        all = sample_lower + sample_upper + sample_numbers + sample_symbols

        random.shuffle(all)

        password = "".join(all)
        # print(password)
        # end generate password
        return password

    @action(methods=["POST"], detail=False, url_path="create-user", url_name="create-user")
    def create_user(self, request):
        payload = request.data
        authenticated_user = request.user

        serializer = serializers.AddUserSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                email = payload['email']
                first_name = payload['first_name']
                last_name = payload['last_name']
                register_as = payload['role_name']
                userexists = get_user_model().objects.filter(email=email).exists()                

                if userexists:
                    return Response({'details': 'User With Credentials Already Exist'}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    group_details = Group.objects.get(id=register_as)
                except (ValidationError, ObjectDoesNotExist):
                    return Response({'details': 'Role does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                
                is_superuser = False
                if group_details.name == "USER_MANAGER":
                    is_superuser = True
                
                password = self.password_generator()
                print(password)

                hashed_pwd = make_password(password)
                newuser = {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "register_as": register_as,
                    "is_active": True,
                    "is_superuser": is_superuser,
                    "password": hashed_pwd,
                }
                create_user = get_user_model().objects.create(**newuser)
                group_details.user_set.add(create_user)
                user_util.log_account_activity(
                    authenticated_user, create_user, "Account Creation",
                    "USER CREATED")
                info = {
                    'success': 'User Created Successfully',
                    'password': password
                }
                return Response(info, status=status.HTTP_200_OK)

        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="suspend-user", url_name="suspend-user")
    def suspend_user(self, request):
        authenticated_user = request.user
        payload = request.data
        serializer = serializers.SuspendUserSerializer(
            data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                user_id = payload['user_id']
                remarks = payload['remarks']
                try:
                    user_details = get_user_model().objects.get(id=user_id)
                except (ValidationError, ObjectDoesNotExist):
                    return Response({'details': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                user_details.is_suspended = True
                user_util.log_account_activity(
                    authenticated_user, user_details, "Account Suspended", remarks)
                user_details.save()
                return Response("Account Successfully Changed", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path="un-suspend-user", url_name="un-suspend-user")
    def un_suspend_user(self, request):
        authenticated_user = request.user
        payload = request.data
        serializer = serializers.SuspendUserSerializer(
            data=payload, many=False)
        if serializer.is_valid():
            user_id = payload['user_id']
            remarks = payload['remarks']
            with transaction.atomic():
                try:
                    user_details = get_user_model().objects.get(id=user_id)
                except (ValidationError, ObjectDoesNotExist):
                    return Response({'details': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                user_details.is_suspended = False
                user_util.log_account_activity(
                    authenticated_user, user_details, "Account UnSuspended", remarks)
                user_details.save()
                return Response("Account Unsuspended", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
