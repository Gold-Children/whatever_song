from rest_framework import serializers
from django.contrib.auth import get_user_model


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    image = serializers.ImageField(required=False)

    def create(self, validated_data):
        user = get_user_model()(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            image=validated_data.get('image', None),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


    class Meta:
        model = get_user_model()
        fields = ['username',
                'password',
                'email',
                'nickname',
                'image',
                ]