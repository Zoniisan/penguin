from rest_framework import serializers

from register.models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    kind = serializers.StringRelatedField()
    temp_leader = serializers.StringRelatedField()
    finish_datetime = serializers.DateTimeField(format="%Y/%m/%d %H:%M:%S")

    class Meta:
        model = Registration
        fields = (
            'id', 'verbose_id', 'kind', 'group', 'group_kana',
            'temp_leader', 'finish_datetime'
        )
        datatables_always_serialize = ('id',)
