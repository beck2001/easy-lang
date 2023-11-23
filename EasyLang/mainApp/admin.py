from django.contrib import admin
from .models import *


# Register your models here.


# class MemberAdmin(admin.ModelAdmin):
#     list_display = ("id", "firstname", "lastname", "phone", "joined_date",)


# admin.site.register(Member, MemberAdmin)

# login admin through tg_id



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "tg_id", "name", "surname", "is_staff", "is_active", "created_at", "updated_at",)

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "active",)
    
    # def user_id_display(self, obj):
    #        return obj.user_id.id
    # user_id_display.short_description = 'Usessr ID'
    # # when editing, show user_id_id instead of __str__

    # user_id_display.admin_order_field = 'user_id__id'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "deadline", "manager", "total_pages_count", "created_at", "finished_at")
@admin.register(Translator)
class TranslatorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "active",)

@admin.register(Project_Translator)
class Project_TranslatorAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "translator", "created_at", "active",)

@admin.register(Project_Editor)
class Project_EditorAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "editor", "active",)

@admin.register(Pages_per_day)
class Pages_per_dayAdmin(admin.ModelAdmin):
    # writable created_at
    list_display = ("id", "translator", "project", "pages_count", "created_at",)
    

# register all models
admin.site.register(Editor)
admin.site.register(Approve)
admin.site.register(Disapprove)