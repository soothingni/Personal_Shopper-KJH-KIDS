from django import forms
from .models import OddeyeUsers
from django.contrib.auth.hashers import make_password, check_password

class RegisterForm(forms.Form):
    id = forms.CharField(error_messages={'required': '아이디를 입력해주세요.'}, max_length=15, label="아이디")
    password = forms.CharField(error_messages={'required': '비밀번호를 입력해주세요.'}, widget=forms.PasswordInput, label="비밀번호")
    re_password = forms.CharField(error_messages={'requried': '비밀번호 확인란을 입력해주세요.'}, widget=forms.PasswordInput, label="비밀번호 확인")

    def clean(self):
        cleaned_data = super().clean()
        id = cleaned_data.get('id')
        password = cleaned_data.get('password')
        re_password = cleaned_data.get('re_password')

        if password and re_password:
            if password != re_password:
                self.add_error('password', "비밀번호가 일치하지 않습니다.")
                self.add_error('re_password', "비밀번호가 일치하지 않습니다.")

class LoginForm(forms.Form):
    id = forms.CharField(error_messages={'required': '아이디를 입력해주세요.'}, max_length=15, label="아이디")
    password = forms.CharField(error_messages={'required': '비밀번호를 입력해주세요.'}, widget=forms.PasswordInput, label="비밀번호")

    def clean(self):
        cleaned_data = super().clean()
        id = cleaned_data.get('id')
        password = cleaned_data.get('password')

        if id and password:
            try:
                oddeye_user = OddeyeUsers.objects.get(id=id)
            except OddeyeUsers.DoesNotExist:
                self.add_error('id', '아이디가 없습니다.')
                return

            if not check_password(password, oddeye_user.password):
                self.add_error('password', '비밀번호가 틀렸습니다.')
