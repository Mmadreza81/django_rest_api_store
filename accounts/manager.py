from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, username, password):
        if not email:
            raise ValueError('کاربر باید ایمیل داشته باشد')
        if not phone_number:
            raise ValueError('کاربر باید شماره موبایل داشته باشد')
        if not username:
            raise ValueError('کاربر باید نام کاربری داشته باشد')

        user = self.model(email=self.normalize_email(email), phone_number=phone_number, username=username)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, phone_number, username, password):
        user = self.create_user(email, phone_number, username, password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
