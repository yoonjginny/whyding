from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'nickname')
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'nickname', 'profile_image', 'introduction')
        read_only_fields = ('email',)

class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)