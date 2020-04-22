from rest_framework import viewsets, views
from ..models import *
from .serializers import *
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import mixins
from .custom_mixins import CreateListModelMixin
from .custom_functions import *

'''
Models - Serializer - ViewSet 
Material - MaterialSerializer - MaterialView
Doctor - DoctorSerializer - DoctorView
Clinic - ClinicSerializer - ClinicView
Operation - OperationSerializer - OperationView
Work - WorkSerializer - WorkView
OperationsInWork - OperationsInWorkSerializer
Order - OrderSerializer - OrderView
File - FileSerializer - FileView
Technician - TechnicianSerializer - TechnicianView
WorkInOrders - WorkInOrdersSerializer - WorkInOrdersView
OperationInOrders - OperationsInOrdersSerializer - OperationsInOrdersView
WorksPriceList - 
OperationPriceList - 
MaterialsOnStock - MaterialsOnStockSerializer - MaterialsOnStockView
MaterialUsedOnOperation -  MaterialUsedOnOperationSerializer - MaterialUsedOnOperationView
'''


class DoctorView(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    serializer_class = DoctorSerializer

    def get_queryset(self):
        """
        doctors only for authenticated owner
        """
        return Doctor.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ClinicView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClinicSerializer

    def get_queryset(self):
        return Clinic.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MaterialView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MaterialSerializer

    def get_queryset(self):
        return Material.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        material = serializer.save(user=self.request.user)
        update_stock(material, 0, self.request.user)


class MaterialOnStockView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MaterialOnStockSerializer

    def get_queryset(self):
        return MaterialOnStock.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MaterialAddingView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MaterialAddingSerializer

    def get_queryset(self):
        return MaterialAdding.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        data = serializer.validated_data
        update_stock(material=data.get('material'), amount=data.get('amount'),
                     user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        data = serializer.validated_data
        update_stock(material=data.get('material'), amount=data.get('amount'),
                     user=self.request.user)

    def perform_destroy(self, instance):
        update_stock(instance.material, instance.amount, self.request.user, action='delete')
        instance.delete()


class WorkView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkSerializer

    def get_queryset(self):
        return Work.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OperationView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OperationSerializer

    def get_queryset(self):
        return Operation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TechnicianView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TechnicianSerializer

    def get_queryset(self):
        return Technician.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FileView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FileSerializer

    def get_queryset(self):
        return File.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MaterialUsedOnOperationView(CreateListModelMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MaterialUsedOnOperationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return MaterialUsedOnOperation.objects.filter(user=self.request.user)


class OrderView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, balance=0)

    # todo if is_closed is changed from 1 to 0
    # def perform_update(self, serializer):
    #     if serializer.is_valid(raise_exception=True):
    #         prev_object = serializer
    #         prev_customer = prev_object.clinic if prev_object.clinic else serializer.prev_object.doctor
    #         prev_customer_type = 0 if prev_object.clinic else 1
    #         serializer.save()
    #     order = serializer.save()
    #     data = serializer.validated_data
    #     if data.get('clinic') or data.get('doctor'):
    #         if not prev_customer:
    #             if data.get('clinic'):
    #                 customer = data.get('clinic')
    #             else:
    #                 customer = data.get('doctor')
    #             customer.debt += order.total_price
    #         else:
    #             prev_customer.debt -= order.total_price
    #             if prev_customer_type:
    #                 if data.get('clinic'):
    #                     customer = data.get('clinic')
    #                 else:
    #                     customer = data.get('doctor')
    #                 customer.debt += order.total_price
    #                 return
    #             else:
    #                 if data.get('doctor'):
    #                     return
    #                 else:
    #                     customer = data.get('clinic')
    #                     customer.debt += order.total_price

    def perform_destroy(self, instance):
        # customer = instance.clinic if instance.clinic else instance.doctor
        # customer.debt -= instance.total_price
        for i in instance.paymentfororder_set.all():
            PaymentForOrderView().perform_destroy(instance=i)
        instance.delete()


class WorkInOrdersView(CreateListModelMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkInOrderSerializer

    def get_queryset(self):
        return WorkInOrders.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        data = serializer.validated_data
        if isinstance(data, list):
            for i in range(len(data)):
                data[i]['user'] = self.request.user
            serializer.save()
            for i in range(len(data)):
                update_sum_of_order(data[i].get('order'))
        else:
            data['user'] = self.request.user
            serializer.save()
            update_sum_of_order(data.get('order'))

    def perform_update(self, serializer):
        order_replaced = self.get_object().order
        serializer.save()
        data = serializer.validated_data
        order = data.get('order') if data.get('order') else order_replaced
        update_sum_of_order(order)
        if order_replaced != order:
            update_sum_of_order(order_replaced)

    def perform_destroy(self, instance):
        print(instance)
        update_sum_of_order(instance.order)
        instance.delete()


class OperationsInOrdersView(CreateListModelMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OperationInOrderSerializer

    def get_queryset(self):
        return OperationsInOrders.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorksPriceListView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WorksPriceListSerializer

    def get_queryset(self):
        return WorksPriceList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorkPriceView(CreateListModelMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkPriceSerializer

    def get_queryset(self):
        return WorkPrice.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OperationsPriceListView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OperationsPriceListSerializer

    def get_queryset(self):
        return OperationsPriceList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OperationPriceView(CreateListModelMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OperationPriceSerializer

    def get_queryset(self):
        return OperationPrice.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentView(CreateListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    # TODO Add Update Method when validation of doctor || clinic will be added
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        serializer.save(user=self.request.user, balance=data.get('amount'))
        if data.get('clinic') and data.get('doctor'):
            raise ValidationError('Both clinic and doctor cannot be provided')
        elif data.get('clinic'):
            customer = data.get('clinic')
        elif data.get('doctor'):
            customer = data.get('doctor')
        else:
            raise ValidationError('Neither clinic nor doctor were provided')
        update_paid(customer, data.get('amount'))

    def perform_destroy(self, instance):
        for i in instance.paymentfororder_set.all():
            PaymentForOrderView().perform_destroy(instance=i)
        instance.delete()


class PaymentForOrderView(CreateListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentForOrderSerializer

    def get_queryset(self):
        return PaymentForOrder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        data = serializer.validated_data
        if isinstance(data, list):
            for i in range(len(data)):
                update_balance_order_payment(data[i].get('order_instance'), data[i].get('payment_instance'),
                                             data[i].get('amount'), 1)
                data[i]['user'] = self.request.user
        else:
            update_balance_order_payment(data.get('order_instance'), data.get('payment_instance'),
                                         data.get('amount'), 1)
            data['user'] = self.request.user
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
        update_balance_order_payment(instance.order_instance, instance.payment_instance, instance.amount, -1)


class WorksReportView(views.APIView):
    """
    params:
    doctor - pk, get orders of this doctor (optional)
    clinic - pk, get orders of this clinic (optional)
    start - date %d.%m.%Y, get orders from this date (optional)
    end - date %d.%m.%Y, get order before this date (optional)
    only_not_paid - int, if 1 - shows only not paid works, if 0 - show all works (optional)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        report = []
        query_params = request.query_params
        clinic_filter, doctor_filter = query_params.get('clinic'), query_params.get('doctor')
        only_not_paid_filter = query_params.get('only_not_paid')

        # Проверяем на целое число
        if clinic_filter:
            clinic_filter = check_is_int(clinic_filter, 'Clinic')
            clinic = Clinic.objects.filter(user=user).filter(id=clinic_filter).first()
            if not clinic:
                raise NotFound(detail='No such clinic')
        if doctor_filter:
            doctor_filter = check_is_int(doctor_filter, 'Doctor')
            doctor = Doctor.objects.filter(user=user).filter(id=doctor_filter).first()
            if not doctor:
                raise NotFound(detail='No such doctor')
        start_date_filter, end_date_filter = [convert_to_datetime(query_params.get('start')),
                                              convert_to_datetime(query_params.get('end'))]
        if only_not_paid_filter:
            only_not_paid_filter = check_is_int(only_not_paid_filter, 'Only Not Paid')

        # Если не заданы клиника и доктор
        if not clinic_filter and not doctor_filter:
            clinics_query, doctors_query = Clinic.objects.filter(user=user), Doctor.objects.filter(user=user)
            orders_query = filter_by_date(Order.objects.filter(user=user), start_date_filter, end_date_filter)
            for clinic in clinics_query:
                orders = orders_query.filter(clinic=clinic).order_by('date')
                report.append({'clinic': clinic.clinic_name, 'total': 0, 'patients': []})
                form_report_of_patients(report[-1], orders, only_not_paid_filter)
            for doctor in doctors_query:
                orders = orders_query.filter(doctor=doctor).filter(clinic=None).order_by('date')
                report.append({'doctor': doctor.doctor_name, 'total': 0, 'patients': []})
                form_report_of_patients(report[-1], orders, only_not_paid_filter)

        # Если задана и клиника, и доктор
        elif doctor_filter and clinic_filter:
            orders_query = filter_by_date(
                Order.objects.filter(user=user).filter(clinic=clinic).filter(doctor=doctor).order_by('date'),
                start_date_filter, end_date_filter)
            report.append({'clinic': clinic.clinic_name, 'doctor': doctor.doctor_name, 'total': 0, 'patients': []})
            form_report_of_patients(report[-1], orders_query, only_not_paid_filter)

        # Если задан только доктор
        elif doctor_filter:
            orders_query = filter_by_date(
                Order.objects.filter(user=user, doctor=doctor).order_by('date'),
                start_date_filter, end_date_filter)
            report.append({'doctor': doctor.doctor_name, 'total': 0, 'patients': []})
            form_report_of_patients(report[-1], orders_query, only_not_paid_filter)

        # Если задана только клиника
        elif clinic_filter:
            orders_query = filter_by_date(
                Order.objects.filter(user=user, clinic=clinic).order_by('date'),
                start_date_filter, end_date_filter)
            report.append({'clinic': clinic.clinic_name, 'total': 0, 'patients': []})
            form_report_of_patients(report[-1], orders_query, only_not_paid_filter)

        # Выводим результат
        return Response(report)


class OperationsReportView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        report = []
        query_params = request.query_params
        start_date_filter, end_date_filter = [convert_to_datetime(query_params.get('start')),
                                              convert_to_datetime(query_params.get('end'))]
        technician_filter = query_params.get('technician')
        if technician_filter:
            technician_filter = check_is_int(technician_filter, 'Technician')
            technician = Technician.objects.filter(user=user).filter(id=technician_filter).first()
            if not technician:
                raise NotFound(detail='No such technician')

            operations_query = filter_by_date(
                OperationsInOrders.objects.filter(user=user).filter(technician=technician).order_by(
                    'date'), start_date_filter, end_date_filter)
            form_report_for_technician(report, technician, operations_query)
        else:
            operations_query = filter_by_date(OperationsInOrders.objects.filter(user=user).order_by('date'),
                                              start_date_filter,
                                              end_date_filter)
            technicians_query = Technician.objects.filter(user=user)
            for technician in technicians_query:
                form_report_for_technician(report, technician, operations_query.filter(technician=technician))
        return Response(report)
