from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
# from django.contrib.auth.models import User


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = BaseUserCreateSerializer.Meta.model
        fields = BaseUserCreateSerializer.Meta.fields
        extra_kwargs = {
            # making email field required for creating a user.
            'email': {'required': True},
        }
