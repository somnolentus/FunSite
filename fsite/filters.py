from django_filters import FilterSet,  DateFilter  # импортируем filterset, чем-то напоминающий знакомые дженерики
from .models import Advertisment, Comment


class AdvertismentFilter(FilterSet):

    class Meta:
        model = Advertisment
        fields = {'heading': ['icontains'], 'body': ['icontains'], 'user': ['in'], 'category': ['in']}


class CommentFilter(FilterSet):
    date_create = DateFilter(field_name='time_create', lookup_expr='date__gt', input_formats=['%d-%m-%Y', '%d/%m/%Y'])

    class Meta:
        model = Comment
        fields = {'comment': ['icontains'], 'user': ['in'], 'hidden': []}

