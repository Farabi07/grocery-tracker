from django.contrib import admin
from django.contrib.auth.models import Group

from .models import *

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Designation._meta.fields]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = [field.name for field in User._meta.fields]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Employee._meta.fields]

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Role._meta.fields]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Permission._meta.fields]

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
	list_display = [field.name for field in City._meta.fields]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Country._meta.fields]

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Branch._meta.fields]


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
	list_display = [field.name for field in LoginHistory._meta.fields]


admin.site.unregister(Group)
