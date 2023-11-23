from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q

from .forms import *
from .models import *
from django.db.models import Value
from django.db.models.functions import Concat
from django.db.models import CharField
from django.db.models import Sum
from django.contrib import messages
from django.core import serializers

# Create your views here.
# Home page

from tgbot.management.commands.bot import bot
import datetime
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.db import connection

from django.conf import settings


def home(request):
    # set for all pages_per_view created_at ascending by 1 from 10 november 2023
    # pages_per_day = Pages_per_day.objects.all()
    # cur_date = datetime.datetime(2023, 11, 10, 9, 32, 0)
    # for page_per_day in pages_per_day:
    #     page_per_day.created_at = cur_date
    #     cur_date += datetime.timedelta(days=1)
    #     page_per_day.save()

    return render(request, 'index.html')


def project_detail(request, project_id):
    # add manager_tg_id
    project = Project.objects.filter(id=project_id).annotate(manager_tg_id=Concat(
        'manager__user__tg_id', Value(''), output_field=CharField())).first()
    if request.user.is_authenticated:
        # if user in Manager, get all projects
        participants = {}
        editors = []
        translators = []
        editors.extend(
            # join tg_id from User where user is in editors and this editor is in project_editors table
            Project_Editor.objects.filter(project=project, active=True).annotate(role=Value('editor', output_field=CharField())).annotate(
                tg_id=Concat('editor__user__tg_id', Value(''), output_field=CharField())).order_by('editor__user__name')
        )
        translators.extend(
            Project_Translator.objects.filter(project=project, active=True).annotate(role=Value('translator', output_field=CharField())).annotate(
                tg_id=Concat('translator__user__tg_id', Value(''), output_field=CharField())).order_by('translator__user__name')
        )

        if project.manager.user == request.user:
            project.role = 'manager'
        elif Project_Editor.objects.filter(project=project, editor__user=request.user):
            project.role = 'editor'
        elif Project_Translator.objects.filter(project=project, translator__user=request.user):
            project.role = 'translator'

        project.translated_count = Pages_per_day.objects.filter(
            project=project).aggregate(Sum('pages_count'))['pages_count__sum']
        if project.translated_count is None:
            project.translated_count = 0
        project.approved_count = Approve.objects.filter(pages_per_day__project=project).aggregate(
            Sum('pages_per_day__pages_count'))['pages_per_day__pages_count__sum']
        if project.approved_count is None:
            project.approved_count = 0

        participants["manager"] = project.manager
        participants["editors"] = editors
        participants["translators"] = translators
        project.participants = participants

        approves = Approve.objects.filter(pages_per_day__project=project)
        disapproves = Disapprove.objects.filter(pages_per_day__project=project)
        pages_per_day = Pages_per_day.objects.filter(project=project)
        # length of pages_per_day
        print(len(pages_per_day))
        # add column approve_count and disapprove_count to pages_per_day
        npd = []
        apprvs = []
        dspprvs = []
        for page_per_day in pages_per_day:
            page_per_day.approve_count = approves.filter(
                pages_per_day=page_per_day).count()
            page_per_day.disapprove_count = disapproves.filter(
                pages_per_day=page_per_day).count()
            page_per_day = page_per_day.__dict__
            # remove _state
            page_per_day.pop('_state')
            page_per_day['created_at'] = page_per_day['created_at'].strftime(
                "%d.%m.%Y %H:%m:%S")
            page_per_day['translator'] = Pages_per_day.objects.get(
                id=page_per_day['id']).translator.user.name + ' ' + Pages_per_day.objects.get(id=page_per_day['id']).translator.user.surname
            # if comment None, set to ""
            if page_per_day['comment'] is None:
                page_per_day['comment'] = ""
            npd.append(page_per_day)

        for approve in approves:
            approve = approve.__dict__
            approve.pop('_state')
            approve['created_at'] = approve['created_at'].strftime(
                "%d.%m.%Y %H:%m:%S")
            approve['editor'] = Approve.objects.get(
                id=approve['id']).editor.user.name + ' ' + Approve.objects.get(id=approve['id']).editor.user.surname
            if approve['comment'] is None:
                approve['comment'] = ""
            approve['pages_count'] = Approve.objects.get(
                id=approve['id']).pages_per_day.pages_count
            apprvs.append(approve)

        for disapprove in disapproves:
            disapprove = disapprove.__dict__
            disapprove.pop('_state')
            disapprove['created_at'] = disapprove['created_at'].strftime(
                "%d.%m.%Y %H:%m:%S")
            print(disapprove['created_at'])
            disapprove['editor'] = Disapprove.objects.get(
                id=disapprove['id']).editor.user.name + ' ' + Disapprove.objects.get(id=disapprove['id']).editor.user.surname
            if disapprove['comment'] is None:
                disapprove['comment'] = ""
            disapprove['pages_count'] = Disapprove.objects.get(
                id=disapprove['id']).pages_per_day.pages_count
            dspprvs.append(disapprove)

        project.pages_per_day = npd
        project.approves = apprvs
        project.disapproves = dspprvs

        project.translated_count = project.translated_count - \
            len(project.disapproves)
        # project.approves = []
        # project.disapproves = []

        pages_to_approve = []
        for page_per_day in npd:
            if page_per_day["approve_count"] == 0 and page_per_day["disapprove_count"] == 0:
                pages_to_approve.append(page_per_day)
                # comment if None, set to ""
        project.pages_to_approve = pages_to_approve
        # sort desc by created_at
        project.pages_to_approve.sort(
            key=lambda x: x['created_at'], reverse=True)

        # avaliable pages count is total_pages_count - sum of pages_count in Pages_per_day which not disapproved
        trsltd_pages = Pages_per_day.objects.filter(project=Project.objects.get(
            id=project_id)).aggregate(Sum('pages_count'))['pages_count__sum']
        disprvd_pages = Disapprove.objects.filter(pages_per_day__project=Project.objects.get(
            id=project_id)).aggregate(Sum('pages_per_day__pages_count'))['pages_per_day__pages_count__sum']
        if trsltd_pages is None:
            trsltd_pages = 0
        if disprvd_pages is None:
            disprvd_pages = 0
        avaliable_pages_count = Project.objects.get(
            id=project_id).total_pages_count - (trsltd_pages - disprvd_pages)

    addTranslatedPagesForm = AddTranslatedPagesForm(
        max_value=avaliable_pages_count)
    addTranslatedPagesForm.fields['pages_count'].widget.attrs['max'] = avaliable_pages_count

    # add project["roles"]
    project.roles = []
    if Project.objects.filter(id=project_id, manager__user=request.user):
        project.roles.append('manager')
    if Project_Editor.objects.filter(project=project, editor__user=request.user, active=True):
        project.roles.append('editor')
    if Project_Translator.objects.filter(project=project, translator__user=request.user, active=True):
        project.roles.append('translator')

    project.translated_count = project.total_pages_count - avaliable_pages_count

    return render(request, 'project_detail.html', {'project': project, 'addTranslatedPagesForm': addTranslatedPagesForm})


def add_new_project(request):
    # return to previous page
    if request.method == 'POST':
        if not Manager.objects.filter(user=request.user):
            messages.error(request, 'Вы не являетесь менеджером')
            return redirect('home')

        form = AddNewProjectForm(request.POST)
        if form.is_valid():
            project_name = form.cleaned_data['project_name']
            project_description = form.cleaned_data['project_description']
            project_total_pages_count = form.cleaned_data['project_total_pages_count']
            project_deadline = form.cleaned_data['project_deadline']
            project = Project(name=project_name, description=project_description, total_pages_count=project_total_pages_count,
                              manager=Manager.objects.get(user=request.user), deadline=project_deadline)
            project.save()
            messages.success(request, 'Проект ' +
                             project_name + ' успешно создан')

            # send message to author
            bot.send_message(request.user.tg_id, 'Проект ' + project_name + ' успешно создан\nОписание: ' + project_description +
                             '\nКоличество страниц: ' + str(project_total_pages_count) + '\nДедлайн: ' + str(project_deadline) + '\nДобавьте команду проекта')

            return redirect('home')
        else:
            messages.error(request, 'Форма заполнена неверно')
            return redirect('home')
    else:
        messages.error(request, 'Ошибка')
        return redirect('home')


def add_pages(request, project_id):
    if request.method == 'POST':
        # if user not in Project_Translator
        if not Project_Translator.objects.filter(project=Project.objects.get(id=project_id), translator=Translator.objects.get(user=request.user)):
            messages.error(
                request, 'Вы не являетесь переводчиком этого проекта')
            return redirect('project_detail', project_id=project_id)

        form = AddTranslatedPagesForm(
            request.POST, max_value=Project.objects.get(id=project_id).total_pages_count)
        if form.is_valid():
            pages_count = form.cleaned_data['pages_count']

            pages_per_day = Pages_per_day(project=Project.objects.get(id=project_id), translator=Translator.objects.get(
                user=request.user), pages_count=pages_count, comment=form.cleaned_data['comment'])
            pages_per_day.save()
            messages.success(request, 'Вы успешно добавили ' +
                             str(pages_count) + ' страниц')

            bot.send_message(request.user.tg_id, 'Вы успешно добавили ' + str(pages_count) + ' страниц в проект ' + Project.objects.get(id=project_id).name + '\n' + 'Комментарий: ' + form.cleaned_data['comment'] +
                             '\nВсего добавлено: ' + str(Pages_per_day.objects.filter(project=Project.objects.get(id=project_id), translator=Translator.objects.get(user=request.user)).aggregate(Sum('pages_count'))['pages_count__sum']) + ' страниц' + '\nВсего осталось: ' + str(Project.objects.get(id=project_id).total_pages_count - Pages_per_day.objects.filter(project=Project.objects.get(id=project_id), translator=Translator.objects.get(user=request.user)).aggregate(Sum('pages_count'))['pages_count__sum']) + ' страниц')
            editors = Project_Editor.objects.filter(
                project=Project.objects.get(id=project_id), active=True)
            for editor in editors:
                bot.send_message(editor.editor.user.tg_id, 'Переводчик ' + request.user.name + ' ' + request.user.surname + ' добавил ' + str(pages_count) + ' страниц в проект ' + Project.objects.get(id=project_id).name + '\n' + 'Комментарий: ' + form.cleaned_data['comment'] +
                                 '\nПроверьте страницы на соответствие требованиям\n')

            return redirect('project_detail', project_id=project_id)
        else:
            messages.error(request, 'Форма заполнена неверно')
            return redirect('project_detail', project_id=project_id)
    else:
        messages.error(request, 'Ошибка')
        return redirect('project_detail', project_id=project_id)

# signup page


def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def approve_pages_per_day(request, pages_per_day_id):
    if request.method == 'POST':
        # if user not in Project_Editor
        if not Project_Editor.objects.filter(project=Pages_per_day.objects.get(id=pages_per_day_id).project, editor=Editor.objects.get(user=request.user)):
            messages.error(request, 'Вы не являетесь редактором этого проекта')
            return redirect('project_detail', project_id=Pages_per_day.objects.get(id=pages_per_day_id).project.id)

        if not Pages_per_day.objects.filter(id=pages_per_day_id):
            messages.error(request, 'Страница не найдена')
            return redirect('project_detail', project_id=Pages_per_day.objects.get(id=pages_per_day_id).project.id)





        approve = Approve(editor=Editor.objects.get(
            user=request.user), pages_per_day=Pages_per_day.objects.get(id=pages_per_day_id))
        approve.save()
        messages.success(request, 'Вы успешно одобрили ' + str(
            Pages_per_day.objects.get(id=pages_per_day_id).pages_count) + ' страниц')
        bot.send_message(request.user.tg_id, 'Вы успешно одобрили ' + str(Pages_per_day.objects.get(id=pages_per_day_id).pages_count) + ' страниц в проекте ' + Pages_per_day.objects.get(id=pages_per_day_id).project.name + ' переводчика ' + Pages_per_day.objects.get(
            id=pages_per_day_id).translator.user.name + ' ' + Pages_per_day.objects.get(id=pages_per_day_id).translator.user.surname + '\nДата перевода: ' + Pages_per_day.objects.get(id=pages_per_day_id).created_at.strftime("%d.%m.%Y %H:%m:%S"))
        bot.send_message(Pages_per_day.objects.get(id=pages_per_day_id).translator.user.tg_id, 'Редактор ' + request.user.name + ' ' + request.user.surname + ' одобрил ' + str(Pages_per_day.objects.get(id=pages_per_day_id).pages_count) +
                         ' страниц в проекте ' + Pages_per_day.objects.get(id=pages_per_day_id).project.name + '\nДата перевода: ' + Pages_per_day.objects.get(id=pages_per_day_id).created_at.strftime("%d.%m.%Y %H:%m:%S"))
        bot.send_message(Pages_per_day.objects.get(id=pages_per_day_id).project.manager.user.tg_id, 'Редактор ' + request.user.name + ' ' + request.user.surname + ' одобрил ' + str(Pages_per_day.objects.get(id=pages_per_day_id).pages_count) +
                         ' страниц в проекте ' + Pages_per_day.objects.get(id=pages_per_day_id).project.name + '\nДата перевода: ' + Pages_per_day.objects.get(id=pages_per_day_id).created_at.strftime("%d.%m.%Y %H:%m:%S"))

        project = Pages_per_day.objects.get(id=pages_per_day_id).project

        # check if all pages approved, send send message that project finished
        if Approve.objects.filter(pages_per_day__project=project).aggregate(Sum('pages_per_day__pages_count'))['pages_per_day__pages_count__sum'] == Pages_per_day.objects.get(id=pages_per_day_id).project.total_pages_count:
            bot.send_message(Pages_per_day.objects.get(id=pages_per_day_id).project.manager.user.tg_id, 'Проект ' + Pages_per_day.objects.get(id=pages_per_day_id).project.name + ' завершен\nВы можете закрывать проект')
        return redirect('project_detail', project_id=Pages_per_day.objects.get(id=pages_per_day_id).project.id)

    else:
        messages.error(request, 'Ошибка')
        return redirect('project_detail', project_id=Pages_per_day.objects.get(id=pages_per_day_id).project.id)


def disapprove_pages_per_day(request, pages_per_day_id):
    if request.method == 'POST':
        # if user not in Project_Editor
        if not Project_Editor.objects.filter(project=Pages_per_day.objects.get(id=pages_per_day_id).project, editor=Editor.objects.get(user=request.user)):
            messages.error(request, 'Вы не являетесь редактором этого проекта')
            return redirect('project_detail', project_id=Pages_per_day.objects.get(id=pages_per_day_id).project.id)

        if not Pages_per_day.objects.filter(id=pages_per_day_id):
            messages.error(request, 'Страница не найдена')
            return redirect('project_detail', project_id=Pages_per_day.objects.get(id=pages_per_day_id).project.id)

        disapprove = Disapprove(editor=Editor.objects.get(user=request.user), pages_per_day=Pages_per_day.objects.get(
            id=pages_per_day_id), comment=request.POST.get('comment'))
        disapprove.save()
        messages.success(request, 'Вы успешно отклонили ' + str(
            Pages_per_day.objects.get(id=pages_per_day_id).pages_count) + ' страниц')
        bot.send_message(request.user.tg_id, 'Вы успешно отклонили ' + str(Pages_per_day.objects.get(id=pages_per_day_id).pages_count) + ' страниц в проекте ' + Pages_per_day.objects.get(id=pages_per_day_id).project.name + ' переводчика ' + Pages_per_day.objects.get(
            id=pages_per_day_id).translator.user.name + ' ' + Pages_per_day.objects.get(id=pages_per_day_id).translator.user.surname + '\nДата перевода: ' + Pages_per_day.objects.get(id=pages_per_day_id).created_at.strftime("%d.%m.%Y %H:%m:%S"))
        bot.send_message(Pages_per_day.objects.get(id=pages_per_day_id).translator.user.tg_id, 'Редактор ' + request.user.name + ' ' + request.user.surname + ' отклонил ' + str(Pages_per_day.objects.get(id=pages_per_day_id).pages_count) +
                         ' страниц в проекте ' + Pages_per_day.objects.get(id=pages_per_day_id).project.name + '\nДата перевода: ' + Pages_per_day.objects.get(id=pages_per_day_id).created_at.strftime("%d.%m.%Y %H:%m:%S"))
        bot.send_message(Pages_per_day.objects.get(id=pages_per_day_id).project.manager.user.tg_id, 'Редактор ' + request.user.name + ' ' + request.user.surname + ' отклонил ' + str(Pages_per_day.objects.get(id=pages_per_day_id).pages_count) +
                         ' страниц в проекте ' + Pages_per_day.objects.get(id=pages_per_day_id).project.name + '\nДата перевода: ' + Pages_per_day.objects.get(id=pages_per_day_id).created_at.strftime("%d.%m.%Y %H:%m:%S"))

        return redirect('project_detail', project_id=Pages_per_day.objects.get(id=pages_per_day_id).project.id)

    else:
        messages.error(request, 'Ошибка')
        return redirect('project_detail', project_id=Pages_per_day.objects.get(id=pages_per_day_id).project.id)


# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'tgbot_url': settings.TELEGRAM_BOT_URL})


def free_editors_list(request):
    project_id = request.GET.get('project_id')
    query = """WITH ActiveProjectEditors AS (
    SELECT pe.editor_id
    FROM mainApp_project_editor pe
    WHERE pe.project_id = """+project_id+"""
        AND pe.active = 1
)
SELECT e.id, u.name, u.surname, u.tg_id
FROM mainApp_editor e
INNER JOIN mainApp_user u ON u.id = e.user_id
LEFT JOIN ActiveProjectEditors ape ON ape.editor_id = e.id
WHERE e.active = 1
    AND ape.editor_id IS NULL
GROUP BY e.id;"""

    with connection.cursor() as cursor:
        cursor.execute(query)
        editors = cursor.fetchall()

    # get count of projects for editors where they are active
    query = """SELECT e.id, COUNT(DISTINCT pe.project_id) AS total_projects
    FROM mainApp_editor e
    LEFT JOIN mainApp_project_editor pe ON pe.editor_id = e.id
    WHERE e.active = 1 AND pe.active = 1
    GROUP BY e.id;"""


    prc = []
    with connection.cursor() as cursor:
        cursor.execute(query)
        prc = cursor.fetchall()
    prc = dict(prc)


    res = []
    for ed in editors:
        editor = list(ed)
        if editor[0] in prc:
            editor.append(prc[editor[0]])
        else:
            editor.append(0)

        res.append({'id': editor[0], 'name': editor[1],
                   'surname': editor[2], 'tg_id': editor[3], 'total_projects': editor[4]})
    return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})


def free_translators_list(request):
    project_id = request.GET.get('project_id')
    query = """WITH ActiveProjectTranslators AS (
    SELECT pt.translator_id
    FROM mainApp_project_translator pt
    WHERE pt.project_id = """+project_id+"""
        AND pt.active = 1
)
SELECT t.id, u.name, u.surname, u.tg_id
FROM mainApp_translator t
INNER JOIN mainApp_user u ON u.id = t.user_id
LEFT JOIN ActiveProjectTranslators apt ON apt.translator_id = t.id
WHERE t.active = 1
    AND apt.translator_id IS NULL
GROUP BY t.id;"""

    with connection.cursor() as cursor:
        cursor.execute(query)
        translators = cursor.fetchall()

    # get count of projects for translators where they are active
    query = """SELECT t.id, COUNT(DISTINCT pt.project_id) AS total_projects
    FROM mainApp_translator t
    LEFT JOIN mainApp_project_translator pt ON pt.translator_id = t.id
    WHERE t.active = 1 AND pt.active = 1
    GROUP BY t.id;"""

    
    prc = []
    with connection.cursor() as cursor:
        cursor.execute(query)
        prc = cursor.fetchall()
    prc = dict(prc)
    
    res = []
    for tr in translators:
        translator = list(tr)
        if translator[0] in prc:
            translator.append(prc[translator[0]])
        else:
            translator.append(0)

        res.append({'id': translator[0], 'name': translator[1],
                   'surname': translator[2], 'tg_id': translator[3], 'total_projects': translator[4]})
    return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})
    
    


def project_editors_list(request):
    project_id = request.GET.get('project_id')
    query = """SELECT e.id, u.name, u.surname, u.tg_id FROM mainApp_editor e  
        INNER JOIN mainApp_project_editor pe ON pe.editor_id=e.id
        INNER JOIN mainApp_project p ON p.id=pe.project_id
        INNER JOIN mainApp_user u ON u.id = e.user_id
        WHERE p.id = """ + project_id + """ AND pe.active = 1 """

    with connection.cursor() as cursor:
        cursor.execute(query)
        editors = cursor.fetchall()
    res = []
    for editor in editors:
        res.append({'id': editor[0], 'name': editor[1],
                   'surname': editor[2], 'tg_id': editor[3]})
    return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})


def project_translators_list(request):
    project_id = request.GET.get('project_id')
    query = """SELECT t.id, u.name, u.surname, u.tg_id FROM mainApp_translator t  
        INNER JOIN mainApp_project_translator pt ON pt.translator_id=t.id
        INNER JOIN mainApp_project p ON p.id=pt.project_id
        INNER JOIN mainApp_user u ON u.id = t.user_id
        WHERE p.id = """ + project_id + """ AND pt.active = 1 """

    with connection.cursor() as cursor:
        cursor.execute(query)
        editors = cursor.fetchall()
    res = []
    for editor in editors:
        res.append({'id': editor[0], 'name': editor[1],
                   'surname': editor[2], 'tg_id': editor[3]})
    return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})


def appoint_editor(request):
    if request.method == "POST":
        project_id = request.POST.get('project_id')
        editor_id = request.POST.get('role_user_id')
        # if user not in project editors with this project with active
        editors_count = 0
        is_active_editor_in_project = Project_Editor.objects.filter(project=Project.objects.get(
            id=project_id), editor=Editor.objects.get(id=editor_id), active=True).count()
        if is_active_editor_in_project:
            editors_count = 1

        if editors_count == 0:
            # check if editor already in project, make it active
            if Project_Editor.objects.filter(project=Project.objects.get(id=project_id), editor=Editor.objects.get(id=editor_id)):
                print('bar')
                Project_Editor.objects.filter(project=Project.objects.get(
                    id=project_id), editor=Editor.objects.get(id=editor_id)).update(active=True)
            else:
                Project_Editor(project=Project.objects.get(
                    id=project_id), editor=Editor.objects.get(id=editor_id), active=True).save()
            bot.send_message(Editor.objects.get(id=editor_id).user.tg_id,
                             'Вы назначены редактором в проекте ' + Project.objects.get(id=project_id).name)

            messages.success(request, 'Редактор ' + Editor.objects.get(id=editor_id).user.name + ' ' + Editor.objects.get(
                id=editor_id).user.surname + ' проекта ' + Project.objects.get(id=project_id).name + ' успешно назначен')
            return redirect('home')
        else:
            messages.error(request, 'Редактор ' + Editor.objects.get(id=editor_id).user.name + ' ' + Editor.objects.get(
                id=editor_id).user.surname + ' проекта ' + Project.objects.get(id=project_id).name + ' уже назначен')
            return redirect('home')
    else:
        messages.error(request, 'Ошибка')
        return redirect('home')


def appoint_translator(request):
    if request.method == "POST":
        project_id = request.POST.get('project_id')
        translator_id = request.POST.get('role_user_id')
        
        translators_count = 0
        is_active_translator_in_project = Project_Translator.objects.filter(project=Project.objects.get(
            id=project_id), translator=Translator.objects.get(id=translator_id), active=True).count()
        if is_active_translator_in_project:
            translators_count = 1



        if translators_count == 0:
            # check if translator already in project, make it active
            if Project_Translator.objects.filter(project=Project.objects.get(id=project_id), translator=Translator.objects.get(id=translator_id)):
                Project_Translator.objects.filter(project=Project.objects.get(
                    id=project_id), translator=Translator.objects.get(id=translator_id)).update(active=True)
            else:
                Project_Translator(project=Project.objects.get(
                    id=project_id), translator=Translator.objects.get(id=translator_id), active=True).save()
            bot.send_message(Translator.objects.get(id=translator_id).user.tg_id,
                             'Вы назначены переводчиком в проекте ' + Project.objects.get(id=project_id).name)

            messages.success(request, 'Переводчик ' + Translator.objects.get(id=translator_id).user.name + ' ' + Translator.objects.get(
                id=translator_id).user.surname + ' проекта ' + Project.objects.get(id=project_id).name + ' успешно назначен')
            return redirect('home')
        else:
            messages.error(request, 'Переводчик ' + Translator.objects.get(id=translator_id).user.name + ' ' + Translator.objects.get(
                id=translator_id).user.surname + ' проекта ' + Project.objects.get(id=project_id).name + ' уже назначен')
            return redirect('home')
    else:
        messages.error(request, 'Ошибка')
        return redirect('home')


def dismiss_editor(request):
    if request.method == "POST":
        project_id = request.POST.get('project_id')
        editor_id = request.POST.get('role_user_id')
        Project_Editor.objects.filter(project=Project.objects.get(
            id=project_id), editor=Editor.objects.get(id=editor_id)).update(active=False)
        bot.send_message(Editor.objects.get(id=editor_id).user.tg_id,
                         'Вы убраны из проекта ' + Project.objects.get(id=project_id).name)
        messages.success(request, 'Редактор успешно убран')
        return redirect('home')
    else:
        messages.error(request, 'Ошибка')
        return redirect('home')


def dismiss_translator(request):
    if request.method == "POST":
        project_id = request.POST.get('project_id')
        translator_id = request.POST.get('role_user_id')
        Project_Translator.objects.filter(project=Project.objects.get(
            id=project_id), translator=Translator.objects.get(id=translator_id)).update(active=False)
        bot.send_message(Translator.objects.get(id=translator_id).user.tg_id,
                         'Вы убраны из проекта ' + Project.objects.get(id=project_id).name)
        messages.success(request, 'Переводчик успешно убран')
        return redirect('home')
    else:
        messages.error(request, 'Ошибка')
        return redirect('home')


def cancel_approve(request, actionId):
    if request.method == "GET":
        if request.user.is_authenticated:
            if not Project_Editor.objects.filter(project=Approve.objects.get(id=actionId).pages_per_day.project, editor=Editor.objects.get(user=request.user)):
                messages.error(
                    request, 'Вы не являетесь редактором этого проекта')
                # redirect to referer
                return redirect(request.META.get('HTTP_REFERER'))

            user_id = request.user
            Approve.objects.filter(id=actionId).delete()
            messages.success(request, 'Одобрение отменено')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'Ошибка')
        return redirect(request.META.get('HTTP_REFERER'))

# logout page


def user_logout(request):
    logout(request)
    return redirect('login')

# send to translator if he didnot translate page


def notify_to_translate(request):
    projects = Project.objects.filter(finished_at__isnull=True)
    for project in projects:
        if not Pages_per_day.objects.filter(project=project, translator__user=request.user):
            bot.send_message(
                request.user.tg_id, 'Вы не добавили страницы в проект ' + project.name + '\nДобавьте страницы')
    return HttpResponse('ok')


def notify_that_project_finished(request):
    projects = Project.objects.filter(finished_at__isnull=True)
    for project in projects:
        if Approve.objects.filter(pages_per_day__project=project).aggregate(Sum('pages_per_day__pages_count'))["pages_per_day__pages_count__sum"] == project.total_pages_count:
            print(project.manager)
            bot.send_message(project.manager.user.tg_id, 'Проект ' +
                             project.name + ' завершен\nВы можете закрывать проект')
    return HttpResponse('ok')


def editor_summary(request):
    # Редактору уведомление в пятницу в 17 00, сколько проверить нужно и сколько проверили за неделю
    query = """SELECT e.id as editor_id, p.id as project_id, u.tg_id, u.name, u.surname FROM mainApp_editor e  
        INNER JOIN mainApp_project_editor pe ON pe.editor_id=e.id
        INNER JOIN mainApp_project p ON p.id=pe.project_id
        INNER JOIN mainApp_user u ON u.id = e.user_id"""

    with connection.cursor() as cursor:
        cursor.execute(query)
        editors = cursor.fetchall()

    for editor in editors:
        print(editor)
        project = Project.objects.get(id=editor[1])
        pages_to_approve = Pages_per_day.objects.filter(project=project, created_at__gte=datetime.datetime.now(
        )-datetime.timedelta(days=7)).aggregate(Sum('pages_count'))["pages_count__sum"]
        approves = Approve.objects.filter(pages_per_day__project=project, created_at__gte=datetime.datetime.now(
        )-datetime.timedelta(days=7)).aggregate(Sum('pages_per_day__pages_count'))["pages_per_day__pages_count__sum"]
        disapproves = Disapprove.objects.filter(pages_per_day__project=project, created_at__gte=datetime.datetime.now(
        )-datetime.timedelta(days=7)).aggregate(Sum('pages_per_day__pages_count'))["pages_per_day__pages_count__sum"]
        message = 'Статистика редактора ' + \
            editor[3] + ' ' + editor[4] + ' за неделю\n'
        message += 'Осталось страниц на модерацию: ' + \
            str(pages_to_approve-approves-disapproves) + '\n'
        message += 'Всего одобрено: ' + str(approves) + '\n'
        message += 'Всего отклонено: ' + str(disapproves) + '\n'
        bot.send_message(editor[2], message)
    return HttpResponse('ok')


def translator_summary(request):
    # сколько осталось по каждому проекту, сколько выполнено за неделю, сколько одобрено
    translators = Translator.objects.filter(active=True).annotate(
        tg_id=Concat('user__tg_id', Value(''), output_field=CharField()))

    # for all projects in which he posted pages
    for translator in translators:
        total_translated = Pages_per_day.objects.filter(
            translator__user=translator.user).aggregate(Sum('pages_count'))['pages_count__sum']
        total_approved = Approve.objects.filter(editor__user=translator.user).aggregate(
            Sum('pages_per_day__pages_count'))['pages_per_day__pages_count__sum']
        total_disapproved = Disapprove.objects.filter(editor__user=translator.user).aggregate(
            Sum('pages_per_day__pages_count'))['pages_per_day__pages_count__sum']

        translator_projects_id = Pages_per_day.objects.filter(
            translator__user=translator.user).values_list('project', flat=True).distinct()
        translator_projects = Project.objects.filter(
            id__in=translator_projects_id)

        message = 'Статистика переводчика ' + translator.user.name + \
            ' ' + translator.user.surname + ' за неделю\n'
        message += 'Всего переведено: ' + str(total_translated) + '\n'
        message += 'Всего одобрено: ' + str(total_approved) + '\n'
        message += 'Всего отклонено: ' + str(total_disapproved) + '\n\n'

        for project in translator_projects:
            p_total_translated = Pages_per_day.objects.filter(
                translator__user=translator.user, project=project).aggregate(Sum('pages_count'))['pages_count__sum']
            p_total_approved = Approve.objects.filter(editor__user=translator.user, pages_per_day__project=project).aggregate(
                Sum('pages_per_day__pages_count'))['pages_per_day__pages_count__sum']
            p_total_disapproved = Disapprove.objects.filter(editor__user=translator.user, pages_per_day__project=project).aggregate(
                Sum('pages_per_day__pages_count'))['pages_per_day__pages_count__sum']
            if (p_total_translated is None):
                p_total_translated = 0
            if (p_total_approved is None):
                p_total_approved = 0
            if (p_total_disapproved is None):
                p_total_disapproved = 0
            p_total_left = project.total_pages_count - \
                (p_total_translated - p_total_disapproved)
            message += 'Проект ' + project.name + '\n'
            message += 'Всего переведено: ' + str(p_total_translated) + '\n'
            message += 'Всего одобрено: ' + str(p_total_approved) + '\n'
            message += 'Всего отклонено: ' + str(p_total_disapproved) + '\n'
            message += 'Осталось: ' + str(p_total_left) + '\n'
            message += 'Дедлайн: ' + str(project.deadline) + '\n\n'
        bot.send_message(translator.user.tg_id, message)
    return HttpResponse('ok')


def end_project(request):
    project_id = request.GET.get('project_id')
    if request.user.is_authenticated:
        if not Project.objects.filter(id=project_id, manager__user=request.user):
            messages.error(request, 'Вы не являетесь менеджером этого проекта')
            return redirect(request.META.get('HTTP_REFERER'))
        elif not Project.objects.filter(id=project_id):
            messages.error(request, 'Проект не найден')
            return redirect(request.META.get('HTTP_REFERER'))
        elif not Project_Editor(project=Project.objects.get(id=project_id), editor=Editor.objects.get(user=request.user)):
            messages.error(request, 'Вы не являетесь редактором этого проекта')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            if Project.objects.get(id=project_id).total_pages_count != Approve.objects.filter(pages_per_day__project=Project.objects.get(id=project_id)).aggregate(Sum('pages_per_day__pages_count'))["pages_per_day__pages_count__sum"]:
                messages.error(request, 'Не все страницы одобрены, вы не сможете завершить проект')
                return redirect(request.META.get('HTTP_REFERER'))
            Project.objects.filter(id=project_id).update(
                finished_at=datetime.datetime.now())
            messages.success(request, 'Проект успешно завершен')
            editors = Project_Editor.objects.filter(
                project=Project.objects.get(id=project_id), active=True)
            for editor in editors:
                bot.send_message(editor.editor.user.tg_id, 'Проект ' +
                                 Project.objects.get(id=project_id).name + ' завершен')
            translators = Project_Translator.objects.filter(
                project=Project.objects.get(id=project_id), active=True)
            for translator in translators:
                bot.send_message(translator.translator.user.tg_id, 'Проект ' +
                                 Project.objects.get(id=project_id).name + ' завершен')
            bot.send_message(Project.objects.get(id=project_id).manager.user.tg_id,
                             'Проект ' + Project.objects.get(id=project_id).name + ' завершен')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'Вы не авторизованы')
        return redirect(request.META.get('HTTP_REFERER'))


def delete_project(request):
    project_id = request.GET.get('project_id')
    if request.user.is_authenticated:
        if not Project.objects.filter(id=project_id, manager__user=request.user):
            messages.error(request, 'Вы не являетесь менеджером этого проекта')
            return redirect(request.META.get('HTTP_REFERER'))
        elif not Project.objects.filter(id=project_id):
            messages.error(request, 'Проект не найден')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            
            messages.success(request, 'Проект успешно удален')
            editors = Project_Editor.objects.filter(project=Project.objects.get(id=project_id), active=True)
            for editor in editors:
                bot.send_message(editor.editor.user.tg_id, 'Проект ' + Project.objects.get(id=project_id).name + ' удален')
            translators = Project_Translator.objects.filter(project=Project.objects.get(id=project_id), active=True)
            for translator in translators:
                bot.send_message(translator.translator.user.tg_id, 'Проект ' + Project.objects.get(id=project_id).name + ' удален')
            bot.send_message(Project.objects.get(id=project_id).manager.user.tg_id, 'Проект ' + Project.objects.get(id=project_id).name + ' удален')
            Project.objects.filter(id=project_id).delete()
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'Вы не авторизованы')
        return redirect(request.META.get('HTTP_REFERER'))
