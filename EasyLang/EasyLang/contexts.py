# import models from ../mainApp/models.py
from mainApp.models import *
from django.db.models import Q
from django.db.models import Value
from django.db.models.functions import Concat
from django.db.models import CharField
from django.db.models import Sum
from django.utils import timezone

from mainApp.forms import AddNewProjectForm

def projects_context(request):
    context_data = dict()
    user_projects = []
    if request.user.is_authenticated:
        # if user in Manager, get all projects
        if Manager.objects.filter(user=request.user, active=True):
            user_projects.extend(
                # set "role" to "manager" 
                Project.objects.all().annotate(role=Value('manager', output_field=CharField())).order_by('name').order_by('finished_at')

            )
        # if user in Editor, get all projects where he is editor
        if Editor.objects.filter(user=request.user, active=True):
            # select projects where user is in editors and this editor is in project_editors table
            user_projects.extend(
                Project.objects.filter(
                    Q(project_editor__editor__user=request.user) &
                    Q(project_editor__active=True)
                ).annotate(role=Value('editor', output_field=CharField())).order_by('name').order_by('finished_at')
            )
        # if user in Translator, get all projects where he is translator
        if Translator.objects.filter(user=request.user, active=True):
           user_projects.extend(
                Project.objects.filter(
                     Q(project_translator__translator__user=request.user) &
                     Q(project_translator__active=True)
                ).annotate(role=Value('translator', output_field=CharField())).order_by('name').order_by('finished_at')
              )
               
        # for each project get Pages_per_day and sum pages_count
        for project in user_projects:
            project_id = project.id
            project.translated_count = Pages_per_day.objects.filter(project=project).aggregate(Sum('pages_count'))['pages_count__sum']
            if project.translated_count is None:
                project.translated_count = 0
            project.approved_count = Approve.objects.filter(pages_per_day__project=project).aggregate(Sum('pages_per_day__pages_count'))['pages_per_day__pages_count__sum']
            if project.approved_count is None:
                project.approved_count = 0
            trsltd_pages = Pages_per_day.objects.filter(project=Project.objects.get(id=project_id)).aggregate(Sum('pages_count'))['pages_count__sum']
            disprvd_pages = Disapprove.objects.filter(pages_per_day__project=Project.objects.get(id=project_id)).aggregate(Sum('pages_per_day__pages_count'))['pages_per_day__pages_count__sum']
            if trsltd_pages is None:
                trsltd_pages = 0
            if disprvd_pages is None:
                disprvd_pages = 0
            avaliable_pages_count = Project.objects.get(id=project_id).total_pages_count - (trsltd_pages - disprvd_pages)

            project.translated_count = project.total_pages_count - avaliable_pages_count


        
        tmpProjects = []
        # remove duplicates with same id
        for p in user_projects:
            found = False
            for pp in tmpProjects:
                if p.id == pp.id:
                    found = True
            if not found:
                tmpProjects.append(p)

        for p in tmpProjects:
            tmpProjects[tmpProjects.index(p)].roles = []
            # get all roles for project
            for pp in user_projects:
                if p.name == pp.name and p.id == pp.id:
                    tmpProjects[tmpProjects.index(p)].roles.append(pp.role)
            # if deadline is over, set deadline_over to True
            if p.deadline < timezone.now().date():
                tmpProjects[tmpProjects.index(p)].deadline_over = True
            else:
                tmpProjects[tmpProjects.index(p)].deadline_over = False
            # is_finished
            if p.finished_at is None:
                tmpProjects[tmpProjects.index(p)].is_finished = False
            else:
                tmpProjects[tmpProjects.index(p)].is_finished = True
        context_data['user_projects'] = tmpProjects

    return context_data

def createProjectForm(request):
    context_data = dict()
    context_data['add_new_project_form'] = AddNewProjectForm(request.POST)
    return context_data

def userData(request):
    context_data = dict()
    if request.user.is_authenticated:
        if Manager.objects.filter(user=request.user, active=True):
            context_data['is_manager'] = True
        else:
            context_data['is_manager'] = False
        if Editor.objects.filter(user=request.user, active=True):
            context_data['is_editor'] = True
        else:
            context_data['is_editor'] = False
    return context_data