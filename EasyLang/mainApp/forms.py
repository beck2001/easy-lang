from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class LoginForm(forms.Form):
    # username is int
    username = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': "form-control",
            'placeholder': 'Телеграм ID'
        }),
        label='',
        required=True,
        min_value=1,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'placeholder': 'Пароль'
        }),
        label='',
        required=True,
    )

    remember_me = forms.BooleanField(
        # first checkbox then label
        widget=forms.CheckboxInput(attrs={
            'class': "form-check-input",
        }),
        label='Запомнить меня',
        required=False,
    )


class AddNewProjectForm(forms.Form):
    # </div>
    # <div class="modal-body form-group">
    #   <!-- form -->
    #   <input type="text" class="form-control new-project-input-text" name="project_name" id="project_name" placeholder="Название"/>
    #   <br>
    #   <input type="text" class="form-control new-project-input-text" name="project_description" id="project_description" placeholder="Описание"/>
    # </div>
    # <div class="modal-footer">
    #   <button class="new_project_btn col">
    #     Создать
    #   </button>
    # </div>
    project_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': "form-control new-project-input-text",
            'placeholder': 'Название'
        }),
        label='',
        required=True,
        max_length=100,
        min_length=1,
    )
    project_description = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': "form-control new-project-input-text",
            'placeholder': 'Описание'
        }),
        label='',
        required=True,
    )
    project_total_pages_count = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': "form-control new-project-input-text",
            'placeholder': 'Количество страниц'
        }),
        label='',
        required=True,
        min_value=1,
        max_value=1000000,
    )
    project_deadline = forms.DateField(
        localize=True,
        # day.month.year
        widget=forms.DateInput(attrs={
            'class': "form-control new-project-input-text",
            'placeholder': 'Дедлайн',
            'type': 'date'
        },
        ),

        label='',
        required=True
    )

# template sends to form max_value
class AddTranslatedPagesForm(forms.Form):

    def __init__(self,*args,**kwargs):
        print(kwargs)
        self.max_value = kwargs.pop('max_value')
        super(AddTranslatedPagesForm,self).__init__(*args,**kwargs)
        self.fields['pages_count'].widget=forms.NumberInput(attrs={
            'class': "form-control",
            'placeholder': 'Количество страниц',
            'id': 'add_pages_count',
            'max': self.max_value
        })

    # <div class="detail_card"><div class="detail_card_title">Добавить переведенные страницы</div><div class="detail_card_content"><form action="/projects/{{project.id}}/add_pages/" method="post">{% csrf_token %}<div class="form-group"><label for="pages_count">Количество страниц</label><input type="number" class="form-control" id="pages_count" name="pages_count" placeholder="Количество страниц"></div><button type="submit" class="btn btn-primary">Добавить</button></form></div></div>
    pages_count = forms.IntegerField(
        label='',
        required=True,
    )
    comment = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'placeholder': 'Комментарий',
            'max_length': 500
        }),
        label='',
        required=False,
        max_length=500,
    )

