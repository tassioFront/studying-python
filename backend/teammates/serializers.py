from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "type"]
        read_only_fields = ["id"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "name", "type", "password"]

    def validate_type(self, value):
        """Prevent creating superuser teammates through registration endpoint"""
        if value == User.SUPERUSER:
            raise serializers.ValidationError(
                "Superuser teammates can only be created through management commands or Django admin."
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
