from django.contrib.auth.base_user import BaseUserManager
class UserManager(BaseUserManager):
    def create_user(self, registration_no, password):
        if not registration_no:
            raise ValueError('Enter Registration No')
        user = self.model(registration_no=registration_no,is_suspended = False)
        user.set_password(password)
        user.save(using=self.db)
        return user
    def create_superuser(self, registration_no, password):
        user = self.create_user(
            registration_no=registration_no,
            password=password)
        user.is_admin = True
        user.is_active = True
        
        user.is_superuser = True
        user.is_staff = True
        
        user.save(using=self._db)
        return user