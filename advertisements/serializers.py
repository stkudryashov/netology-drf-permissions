from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        creator = self.context["request"].user
        validated_data["creator"] = creator

        count_open = Advertisement.objects.filter(creator=creator, status='OPEN').count()

        if count_open >= 10:
            raise ValidationError({'detail': 'Too Many Open Advertisement (max count 10)'})

        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        creator = self.context["request"].user
        count_open = Advertisement.objects.filter(creator=creator, status='OPEN').count()

        if data.get('status', '') == 'OPEN':
            if count_open >= 10:
                raise ValidationError({'detail': 'Too Many Open Advertisement (max count 10)'})

        return data
