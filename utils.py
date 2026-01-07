from django.contrib.auth.mixins import UserPassesTestMixin
import jdatetime

class IsAdminUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin

def to_jalali(datetime_obj):
    if not datetime_obj:
        return None
    return jdatetime.datetime.fromgregorian(datetime=datetime_obj).strftime('%Y/%m/%d - %H:%M')
