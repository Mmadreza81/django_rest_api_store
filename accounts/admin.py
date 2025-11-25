from django.contrib import admin
from .models import User, Profile, OtpCode, Address
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm, UserChangeForm

@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created')

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class AddressInline(admin.StackedInline):
    model = Address
    can_delete = False

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ['email', 'phone_number', 'is_admin']
    list_filter = ('is_admin',)
    readonly_fields = ('last_login',)

    fieldsets = (
        ('main', {'fields': ('email', 'phone_number', 'username', 'password')}),
        ('Permissions',
         {'fields': ('is_active', 'is_admin', 'is_superuser', 'last_login', 'groups', 'user_permissions')})
    )

    add_fieldsets = (
        (None, {'fields': ('phone_number', 'email', 'username', 'password1', 'password2')})
    )

    search_fields = ('email', 'username')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')
    inlines = [ProfileInline, AddressInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser and 'is_superuser' in form.base_fields:
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['is_admin'].disabled = True
            form.base_fields['is_active'].disabled = True
        return form


admin.site.register(User, UserAdmin)
