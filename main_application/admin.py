from django.contrib import admin

from authentication.models import User, UserRole, MunicipalityUser, CommercialUser
from .models import Client_Commercial, Client_Municipality, Chat, Routes, Chat_Group, VerifyEmail, VerifyForgetEmail

# Register your models here.

admin.site.register(User)
admin.site.register(UserRole)
admin.site.register(MunicipalityUser)
admin.site.register(CommercialUser)

admin.site.register(Client_Municipality)
admin.site.register(Client_Commercial)
admin.site.register(Chat_Group)
admin.site.register(VerifyEmail)
admin.site.register(VerifyForgetEmail)

admin.site.register(Chat)

@admin.register(Routes)
class RoutesAdmin(admin.ModelAdmin):
    list_display = ('url', 'description', 'created_at', 'updated_at')
    search_fields = ('url', 'description')
    list_filter = ('created_at', 'updated_at')