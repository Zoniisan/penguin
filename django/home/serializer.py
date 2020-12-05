from rest_framework import serializers
from home.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'stid', 'first_name', 'last_name',
            'first_name_kana', 'last_name_kana'
        )
        datatables_always_serialize = ('id',)
