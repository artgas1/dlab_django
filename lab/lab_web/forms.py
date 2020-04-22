from django import forms

from .models import *


class UserFormRegistration(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'


class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = '__all__'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class WorkInOrdersForm(forms.ModelForm):
    class Meta:
        model = WorkInOrders
        exclude = ['order']


class OperationInOrdersForm(forms.ModelForm):
    class Meta:
        model = OperationsInOrders
        exclude = ['order']
