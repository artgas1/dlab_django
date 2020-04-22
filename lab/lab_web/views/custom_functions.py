from django.conf import settings
import datetime
from rest_framework.exceptions import ParseError
from ..models import *
from rest_framework import serializers


def convert_to_datetime(string):
    try:
        if not string:
            return None
        else:
            date_converted = datetime.datetime.strptime(string, settings.INPUT_OUTPUT_DATE_FORMAT)
            return date_converted
    except Exception as e:
        raise ParseError(detail='Date has to be in {} format'.format(settings.INPUT_OUTPUT_DATE_FORMAT))


def check_is_int(string, instance_name):
    if not string.isdigit():
        raise ParseError(detail='{} param has to be int or pk'.format(instance_name))
    else:
        query_filter = int(string)
        return query_filter


def filter_by_date(queryset, start_date_filter, end_date_filter):
    if start_date_filter and end_date_filter:
        return queryset.filter(date__range=(start_date_filter, end_date_filter))
    elif start_date_filter and not end_date_filter:
        return queryset.filter(date__gte=start_date_filter)
    elif not start_date_filter and end_date_filter:
        return queryset.filter(date__lte=end_date_filter)
    else:
        return queryset


def update_paid(customer, amount):
    customer.paid += amount
    customer.save()


def update_debt(customer, amount):
    customer.debt += amount
    customer.save()


def update_sum_of_one_order(order):
    work_in_orders = order.workinorders_set.all()
    total_price = 0
    for i in work_in_orders:
        total_price += i.price * i.amount
    customer = order.clinic if order.clinic else order.doctor
    if customer:
        update_debt(customer, -(order.total_price - total_price))
    order.total_price = total_price
    order.save()


def update_sum_of_order(order):
    update_sum_of_one_order(order)


def update_stock(material, amount, user, action='add'):
    if action == 'delete':
        material_on_stock = material.materialonstock
        material_on_stock.amount -= amount
        material_on_stock.save()
        return
    if not hasattr(material, 'materialonstock'):
        MaterialOnStock(material=material, amount=amount, user=user).save()
    else:
        material_on_stock = material.materialonstock
        material_on_stock.amount += amount
        material_on_stock.save()


def update_balance_order_payment(order, payment, amount, k=1):
    if k > 0:
        if order.balance + amount > order.total_price:
            raise serializers.ValidationError("Paid sum can't be greater than total price")
        if payment.balance - amount < 0:
            raise serializers.ValidationError("Can't use more money than is available")
    order.balance += amount * k
    payment.balance -= amount * k
    order.save()
    payment.save()


def form_report_of_patients(report, orders, only_not_paid):
    for order in orders:
        if only_not_paid:
            if order.is_paid:
                continue
        report['total'] += order.total_price
        report['patients'].append({'patient': order.patient, 'total': 0, 'works': []})
        patient_report = report['patients'][-1]
        work_report = patient_report['works']
        work_in_order = order.workinorders_set.all()
        if work_in_order:
            for work in work_in_order:
                work_report.append(
                    {'work': work.work.work_name, 'price': work.price, 'amount': work.amount})
                patient_report['total'] += work.price * work.amount


def form_report_for_technician(report, technician, operations_query):
    report.append({"technician_name": technician.technician_name, "operations": [], "total": 0})
    operations_report = report[-1]
    for operation in operations_query:
        operation_info = {"operation": operation.operation.operation_name, "price": operation.price,
                          "amount": operation.amount, "total": operation.price * operation.amount}
        operations_report['operations'].append(operation_info)
        report[-1]['total'] += operation_info['total']
