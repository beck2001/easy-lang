from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/add/', views.add_new_project, name='add_new_project'),
    path('project/<int:project_id>/add_pages/', views.add_pages, name='add_pages'),
    # approve pages_per_day
    path('pages_per_day/<int:pages_per_day_id>/approve/', views.approve_pages_per_day, name='approve_pages_per_day'),
    path('pages_per_day/<int:pages_per_day_id>/disapprove/', views.disapprove_pages_per_day, name='disapprove_pages_per_day'),
    path('free_editors_list', views.free_editors_list, name="free_editors_list"),
    path('free_translators_list', views.free_translators_list, name="free_translators_list"),
    path('project_editors_list', views.project_editors_list, name="project_editors_list"),
    path('project_translators_list', views.project_translators_list, name="project_translators_list"),
    path('appoint_editor', views.appoint_editor, name="appoint_editor"),
    path('appoint_translator', views.appoint_translator, name="appoint_translator"),
    path('dismiss_editor', views.dismiss_editor, name="dismiss_editor"),
    path('dismiss_translator', views.dismiss_translator, name="dismiss_translator"),

    path('cancel_approve/<int:actionId>', views.cancel_approve, name="cancel_approve"),


    # notifications
    path('notify_that_project_finished', views.notify_that_project_finished, name="notify_that_project_finished"),
    path('notify_to_translate', views.notify_to_translate, name="notify_to_translate"),
    path('translator_summary', views.translator_summary, name="translator_summary"),
    path('editor_summary', views.editor_summary, name="editor_summary"),

    path("end_project", views.end_project, name="end_project"),
    path("delete_project", views.delete_project, name="delete_project"),
]