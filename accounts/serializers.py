from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile_image', 'introduction']
        read_only_fields = ['id', 'email']
        extra_kwargs = {
            'profile_image': {
                'required': False,
                'help_text': '프로필 이미지를 업로드하세요. (선택사항)'
            },
            'introduction': {
                'required': False,
                'help_text': '자기소개를 입력하세요. (선택사항)'
            },
            'username': {
                'help_text': '사용자 이름을 입력하세요. (필수)'
            }
        }

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text='비밀번호를 입력하세요. (필수)'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='비밀번호를 다시 입력하세요. (필수)'
    )
    profile_image = serializers.ImageField(
        required=False,
        help_text='프로필 이미지를 업로드하세요. (선택사항)',
        use_url=True
    )
    introduction = serializers.CharField(
        required=False,
        help_text='자기소개를 입력하세요. (선택사항)',
        allow_blank=True
    )
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'username', 'profile_image', 'introduction']
        extra_kwargs = {
            'email': {
                'required': True,
                'help_text': '로그인에 사용할 이메일 주소를 입력하세요. (필수)'
            },
            'username': {
                'required': True,
                'help_text': '사용자 이름을 입력하세요. (필수)'
            }
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password": _("비밀번호가 일치하지 않습니다.")})
        return attrs

    def create(self, validated_data):
        # password와 password_confirm 추출
        password = validated_data.pop('password')
        validated_data.pop('password_confirm', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            profile_image=validated_data.get('profile_image', None),
            introduction=validated_data.get('introduction', '')
        )
        user.set_password(password)
        user.save()
        
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, validators=[validate_password], style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": _("새 비밀번호가 일치하지 않습니다.")})
        return attrs

class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    confirm_delete = serializers.BooleanField(required=True)

    def validate(self, attrs):
        if not attrs.get('confirm_delete'):
            raise serializers.ValidationError({"confirm_delete": _("계정 삭제를 확인해주세요.")})
        return attrs

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        required=True,
        help_text='로그아웃할 refresh 토큰'
    )







from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile_image', 'introduction', 'provider', 'social_id']
        read_only_fields = ['id', 'email', 'provider', 'social_id']
        extra_kwargs = {
            'profile_image': {
                'required': False,
                'help_text': '프로필 이미지를 업로드하세요. (선택사항)'
            },
            'introduction': {
                'required': False,
                'help_text': '자기소개를 입력하세요. (선택사항)'
            },
            'username': {
                'help_text': '사용자 이름을 입력하세요. (필수)'
            }
        }

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text='비밀번호를 입력하세요. (필수)'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='비밀번호를 다시 입력하세요. (필수)'
    )
    profile_image = serializers.ImageField(
        required=False,
        help_text='프로필 이미지를 업로드하세요. (선택사항)',
        use_url=True
    )
    introduction = serializers.CharField(
        required=False,
        help_text='자기소개를 입력하세요. (선택사항)',
        allow_blank=True
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'username', 'profile_image', 'introduction', 'provider', 'social_id']
        extra_kwargs = {
            'email': {
                'required': True,
                'help_text': '로그인에 사용할 이메일 주소를 입력하세요. (필수)'
            },
            'username': {
                'required': True,
                'help_text': '사용자 이름을 입력하세요. (필수)'
            },
            'provider': {'read_only': True},
            'social_id': {'read_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        return attrs

    def create(self, validated_data):
        # password와 password_confirm 추출
        password = validated_data.pop('password')
        validated_data.pop('password_confirm', None)
        profile_image = validated_data.get('profile_image', None)

        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            introduction=validated_data.get('introduction', ''),
            profile_image=profile_image,
            provider='email'
        )

        user.set_password(password)
        user.save()

        return user
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, validators=[validate_password], style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "새 비밀번호가 일치하지 않습니다."})
        return attrs

class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    confirm_delete = serializers.BooleanField(required=True)

    def validate(self, attrs):
        if not attrs.get('confirm_delete'):
            raise serializers.ValidationError({"confirm_delete": "계정 삭제를 확인해주세요."})
        return attrs

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        required=True,
        help_text='로그아웃할 refresh 토큰'
    )