from django.db import models
from django.contrib.auth.models import User
from ..lab import settings
# Create your models here.

import uuid
import os
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from model_utils import Choices


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(), ext)
    return os.path.join('documents/' + filename)


'''
Material
Doctor
Clinic
Operation
Work
OperationsInWork
Order
File
Technician
WorkInOrders
OperationInOrders
WorkPriceInPriceList
WorksPriceList
OperationPriceInPriceList
OperationPriceList
MaterialsOnStock
MaterialUsedOnOperation 
'''


class Material(models.Model):
    choices_materials_unit = Choices(
        ('gr', 'гр.'),
        ('sht', 'шт.')
    )
    material_name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=100, choices=choices_materials_unit, default=choices_materials_unit.gr)
    limit = models.IntegerField(validators=[MinValueValidator(0)])
    comment = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Materials"

    def __str__(self):
        return '{} {}'.format(self.id, self.material_name)


class Operation(models.Model):
    operation_name = models.CharField(max_length=100, unique=True)
    materials = models.ManyToManyField(Material, through='MaterialUsedOnOperation')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Operations"

    def __str__(self):
        return '{} {}'.format(self.id, self.operation_name)


class Work(models.Model):
    work_name = models.CharField(max_length=100, unique=True)
    operations = models.ManyToManyField(Operation, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Works"

    def __str__(self):
        return '{} {}'.format(self.id, self.work_name)


class WorksPriceList(models.Model):
    price_list_name = models.CharField(max_length=100, unique=True)
    works = models.ManyToManyField(Work, through='WorkPrice')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Works Price Lists"

    def __str__(self):
        return '{} {}'.format(self.id, self.price_list_name)


class WorkPrice(models.Model):
    price_list = models.ForeignKey(WorksPriceList, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Work Price In Price List"
        unique_together = ('work', 'price_list')

    def __str__(self):
        return '{} {} {} {}'.format(self.id, self.price_list, self.work, self.price)


class OperationsPriceList(models.Model):
    price_list_name = models.CharField(max_length=100, unique=True)
    operations = models.ManyToManyField(Operation, through='OperationPrice')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Operations Price Lists"

    def __str__(self):
        return '{} {}'.format(self.id, self.price_list_name)


class OperationPrice(models.Model):
    price_list = models.ForeignKey(OperationsPriceList, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Operation Price In Price List"
        unique_together = ('price_list', 'operation')

    def __str__(self):
        return '{} {} {} {}'.format(self.id, self.price_list, self.operation, self.price)


class Doctor(models.Model):
    doctor_name = models.CharField(max_length=50, unique=True)
    contacts = models.CharField(max_length=100, blank=True)
    comment = models.CharField(max_length=100, blank=True)
    price_list = models.ForeignKey(WorksPriceList, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    debt = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    paid = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Doctors"

    def __str__(self):
        return '{} {}'.format(self.id, self.doctor_name)


class Clinic(models.Model):
    clinic_name = models.CharField(max_length=50, unique=True)
    contacts = models.CharField(max_length=100, blank=True)
    comment = models.CharField(max_length=100, blank=True)
    price_list = models.ForeignKey(WorksPriceList, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    debt = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    paid = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Clinics"

    def __str__(self):
        return '{} {}'.format(self.id, self.clinic_name)


class Order(models.Model):
    choices_progress = Choices(
        ('NR', 'Не готов'),
        ('HR', 'Частично готов'),
        ('R', 'Готов')
    )
    date = models.DateField(default=date.today)
    patient = models.CharField(max_length=50)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, blank=True, null=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, blank=True, null=True)
    works = models.ManyToManyField(Work, through='WorkInOrders')
    operations = models.ManyToManyField(Operation, through='OperationsInOrders')
    comment = models.CharField(max_length=100, blank=True)
    progress = models.CharField(max_length=100, choices=choices_progress, blank=True, default=choices_progress.NR)
    deadline = models.DateField(blank=True, null=True, default=None)
    total_price = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    is_closed = models.BooleanField(default=False)
    paid_by = models.ManyToManyField('Payment', through='PaymentForOrder')
    balance = models.IntegerField(validators=[MinValueValidator(0)])

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Orders"

    def __str__(self):
        return '{} {} {} {} {}'.format(self.id, self.patient, self.doctor, self.clinic, self.total_price)


class File(models.Model):
    file = models.FileField(upload_to=get_file_path)
    order = models.ForeignKey(Order, related_name='files', on_delete=models.CASCADE, blank=True, null=True,
                              default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Files"

    def __str__(self):
        return '{} {}'.format(self.id, self.file.name)


class Technician(models.Model):
    technician_name = models.CharField(max_length=50)
    contacts = models.CharField(max_length=100, blank=True)
    comment = models.CharField(max_length=100, blank=True)
    price_list = models.ForeignKey(OperationsPriceList, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Technicians"

    def __str__(self):
        return '{} {}'.format(self.id, self.technician_name)


class WorkInOrders(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    amount = models.IntegerField(validators=[MinValueValidator(0)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Work In Orders"

    def __str__(self):
        return '{} {} {}'.format(self.id, self.work, self.amount)


class OperationsInOrders(models.Model):
    date = models.DateField(default=date.today)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    amount = models.IntegerField(validators=[MinValueValidator(0)])
    deadline = models.DateField(default=None, blank=True, null=True)
    is_done = models.BooleanField(default=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Operation In Orders"

    def __str__(self):
        return '{} {} {} {} {}'.format(self.id, self.operation, self.amount, self.technician, self.order)


class MaterialAdding(models.Model):
    date = models.DateField(default=date.today)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    amount = models.IntegerField()
    cost = models.IntegerField(validators=[MinValueValidator(0)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Materials Adding to Stock"

    def __str__(self):
        return '{} {} {}'.format(self.id, self.material, self.amount)


class MaterialOnStock(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE)
    amount = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Materials On Stock"

    def __str__(self):
        return '{} {} {}'.format(self.id, self.material, self.amount)


class MaterialUsedOnOperation(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(0)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Material Used on Operation"
        unique_together = ('operation', 'material')

    def __str__(self):
        return '{} {} {}'.format(self.id, self.operation, self.material)


class Payment(models.Model):
    choices_payment = Choices(("N", "Нал."), ("B", "Безнал."))
    date = models.DateField(default=date.today)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, blank=True, null=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.IntegerField(validators=[MinValueValidator(0)])
    payment_form = models.CharField(max_length=100, choices=choices_payment, default=choices_payment.N)
    comment = models.CharField(max_length=100, blank=True)
    balance = models.IntegerField(validators=[MinValueValidator(0)])

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Payment"

    def __str__(self):
        return '{} {} {}'.format(self.id, self.doctor if self.doctor else self.clinic, self.amount)


class PaymentForOrder(models.Model):
    order_instance = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_instance = models.ForeignKey(Payment, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(1)])

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Payments For Orders"

    def __str__(self):
        return '{} {} {} {}'.format(self.id, self.order_instance, self.payment_instance, self.amount)


@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `File` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `File` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = File.objects.get(pk=instance.pk).file
    except File.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
