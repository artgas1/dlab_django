from .custom_fields import *
from ..models import *

# from drf_extra_fields.relations import *

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
WorkPriceInPriceList -
WorksPriceList -
OperationsPriceInPriceList -
OperationsPriceList - 
MaterialsOnStock - MaterialsOnStockSerializer - MaterialsOnStockView
MaterialUsedOnOperation -  MaterialUsedOnOperationSerializer - MaterialUsedOnOperationView
'''


class ChoicesField(serializers.Field):
    def __init__(self, choices, **kwargs):
        self._choices = choices
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        return getattr(self._choices, data)


class MaterialSerializer(serializers.ModelSerializer):
    unit = ChoicesField(choices=Material.choices_materials_unit)

    class Meta:
        model = Material
        exclude = ['user']


class MaterialOnStockSerializer(serializers.ModelSerializer):
    material = PresentablePrimaryKeyRelatedField(presentation_serializer=MaterialSerializer,
                                                 queryset=Material.objects.all())

    class Meta:
        model = MaterialOnStock
        exclude = ['user']


class MaterialAddingSerializer(serializers.ModelSerializer):
    material = PresentablePrimaryKeyRelatedField(presentation_serializer=MaterialSerializer,
                                                 queryset=Material.objects.all())

    class Meta:
        model = MaterialAdding
        exclude = ['user']


class MaterialUsedOnOperationSerializer(serializers.ModelSerializer):
    material = PresentablePrimaryKeyRelatedField(presentation_serializer=MaterialSerializer,
                                                 queryset=Material.objects.all())
    operation = UserFilteredPrimaryKeyRelatedField(queryset=Operation.objects.all())

    class Meta:
        model = MaterialUsedOnOperation
        exclude = ['user']


class OperationSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super(OperationSerializer, self).to_representation(instance)
        representation['materials'] = MaterialUsedOnOperationSerializer(
            instance.materialusedonoperation_set.all(),
            many=True).data
        for i in range(len(representation['materials'])):
            representation['materials'][i].pop('operation')
        return representation

    class Meta:
        model = Operation
        exclude = ['user']


class WorkSerializer(serializers.ModelSerializer):
    operations = PresentablePrimaryKeyRelatedField(presentation_serializer=OperationSerializer,
                                                   queryset=Operation.objects.all(), many=True,
                                                   required=False,
                                                   allow_null=True)

    class Meta:
        model = Work
        exclude = ['user']


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        exclude = ['user']


class WorksPriceListSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super(WorksPriceListSerializer, self).to_representation(instance)
        representation['works'] = WorkPriceSerializer(instance.workprice_set.all(),
                                                      many=True).data
        for i in range(len(representation['works'])):
            representation['works'][i].pop('price_list')
        return representation

    class Meta:
        model = WorksPriceList
        exclude = ['user']


class ClinicSerializer(serializers.ModelSerializer):
    price_list = PresentablePrimaryKeyRelatedField(presentation_serializer=WorksPriceListSerializer,
                                                   queryset=WorksPriceList.objects.all(),
                                                   required=False,
                                                   allow_null=True)

    class Meta:
        model = Clinic
        read_only_fields = []
        exclude = ['user', 'debt', 'paid']


class DoctorSerializer(serializers.ModelSerializer):
    price_list = PresentablePrimaryKeyRelatedField(presentation_serializer=WorksPriceListSerializer,
                                                   queryset=WorksPriceList.objects.all(),
                                                   required=False,
                                                   allow_null=True)

    class Meta:
        model = Doctor
        read_only_fields = []
        exclude = ['user', 'debt', 'paid']


class OrderSerializer(serializers.ModelSerializer):
    # TODO: check if doctor or clinic field is filled
    doctor = PresentablePrimaryKeyRelatedField(presentation_serializer=DoctorSerializer,
                                               queryset=Doctor.objects.all(),
                                               required=False, allow_null=True)
    clinic = PresentablePrimaryKeyRelatedField(presentation_serializer=ClinicSerializer,
                                               queryset=Clinic.objects.all(),
                                               required=False, allow_null=True)
    files = PresentablePrimaryKeyRelatedField(presentation_serializer=FileSerializer,
                                              queryset=File.objects.all(),
                                              required=False, allow_null=True, many=True)

    progress = ChoicesField(choices=Order.choices_progress, required=False)

    def to_representation(self, instance):
        representation = super(OrderSerializer, self).to_representation(instance)

        representation['works'] = WorkInOrderSerializer(instance.workinorders_set.all(),
                                                        many=True).data
        for i in range(len(representation['works'])):
            representation['works'][i].pop('order')

        representation['operations'] = OperationInOrderSerializer(
            instance.operationsinorders_set.all(),
            many=True).data
        for i in range(len(representation['operations'])):
            representation['operations'][i].pop('order')

        representation['paid_by'] = PaymentForOrderSerializer(instance.paymentfororder_set.all(), many=True).data
        for i in range(len(representation['paid_by'])):
            representation['paid_by'][i].pop('order_instance')
        return representation

    class Meta:
        model = Order
        read_only_fields = ['total_price', 'balance']
        optional_fields = ['is_closed']
        exclude = ['user']


class WorkInOrderSerializer(serializers.ModelSerializer):
    order = UserFilteredPrimaryKeyRelatedField(queryset=Order.objects.all())
    work = PresentablePrimaryKeyRelatedField(presentation_serializer=WorkSerializer,
                                             queryset=Work.objects.all())

    def validate(self, attrs):
        if attrs.get('order'):
            if attrs.get('order').is_closed:
                raise serializers.ValidationError("Cannot add work to closed order")
        return attrs

    class Meta:
        model = WorkInOrders
        exclude = ['user']


class WorkPriceSerializer(serializers.ModelSerializer):
    price_list = UserFilteredPrimaryKeyRelatedField(queryset=WorksPriceList.objects.all())
    work = PresentablePrimaryKeyRelatedField(presentation_serializer=WorkSerializer,
                                             queryset=Work.objects.all())

    class Meta:
        model = WorkPrice
        exclude = ['user']


class OperationsPriceListSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super(OperationsPriceListSerializer, self).to_representation(instance)
        representation['operations'] = OperationPriceSerializer(instance.operationprice_set.all(),
                                                                many=True).data
        for i in range(len(representation['operations'])):
            representation['operations'][i].pop('price_list')
        return representation

    class Meta:
        model = OperationsPriceList
        exclude = ['user']


class TechnicianSerializer(serializers.ModelSerializer):
    price_list = PresentablePrimaryKeyRelatedField(
        presentation_serializer=OperationsPriceListSerializer,
        queryset=OperationsPriceList.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Technician
        exclude = ['user']


class OperationInOrderSerializer(serializers.ModelSerializer):
    order = UserFilteredPrimaryKeyRelatedField(queryset=Order.objects.all())
    operation = PresentablePrimaryKeyRelatedField(presentation_serializer=OperationSerializer,
                                                  queryset=Operation.objects.all())
    technician = PresentablePrimaryKeyRelatedField(presentation_serializer=TechnicianSerializer,
                                                   queryset=Technician.objects.all())

    class Meta:
        model = OperationsInOrders
        exclude = ['user']


class OperationPriceSerializer(serializers.ModelSerializer):
    price_list = UserFilteredPrimaryKeyRelatedField(queryset=OperationsPriceList.objects.all())
    operation = PresentablePrimaryKeyRelatedField(presentation_serializer=OperationSerializer,
                                                  queryset=Operation.objects.all())

    class Meta:
        model = OperationPrice
        exclude = ['user']


class PaymentSerializer(serializers.ModelSerializer):
    doctor = PresentablePrimaryKeyRelatedField(presentation_serializer=DoctorSerializer,
                                               queryset=Doctor.objects.all(),
                                               required=False, allow_null=True)
    clinic = PresentablePrimaryKeyRelatedField(presentation_serializer=ClinicSerializer,
                                               queryset=Clinic.objects.all(),
                                               required=False, allow_null=True)

    payment_form = ChoicesField(choices=Payment.choices_payment)

    class Meta:
        model = Payment
        read_only_fields = ['balance']
        exclude = ['user']


class PaymentForOrderSerializer(serializers.ModelSerializer):
    order_instance = UserFilteredPrimaryKeyRelatedField(queryset=Order.objects.all())
    payment_instance = PresentablePrimaryKeyRelatedField(presentation_serializer=PaymentSerializer,
                                                         queryset=Payment.objects.all())

    def validate(self, attrs):
        if not attrs.get('order_instance').is_closed:
            raise serializers.ValidationError("Cannot pay for not closed order")
        return attrs

    class Meta:
        model = PaymentForOrder
        exclude = ['user']
