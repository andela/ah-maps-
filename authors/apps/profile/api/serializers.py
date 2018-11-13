from rest_framework import serializers
from django.apps import apps
from django.contrib.auth import get_user_model
from ...core.upload import uploader

TABLE = apps.get_model('profile', 'Profile')
APP = 'profile_api'
fields = ('image', 'bio',)
User = get_user_model()


class ProfileListSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = TABLE

        fields = fields + ('username',)

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email


class ProfileUpdateSerializer(serializers.ModelSerializer):
    image_file = serializers.ImageField(required=False)

    class Meta:
        model = TABLE

        fields = fields + ('image_file',)

    def update(self, instance, validated_data):
        instance.bio = validated_data.get('bio', instance.bio)
        if validated_data.get('image_file'):
            image = uploader(validated_data.get('image_file'))
            instance.image = image.get('secure_url') if image else instance.image
        instance.save()

        return instance


class ProfileFollowSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex="^(?!.*\ )[A-Za-z\d\-\_][^\W_]+$",
        min_length=3,
        required=True,
        error_messages={
            'invalid': 'Sorry, invalid username. No spaces or special characters allowed.',
            'required': 'Sorry, username is required.',
            'min_length': 'Sorry, username must have at least 3 characters.'
        }

    )

    class Meta:
        model = TABLE

        fields = ['username', ]

    def create(self, validated_data):
        current_profile = self.context.get('request').user.profile
        is_following = current_profile.following(profile=current_profile)

        # ensure the user exists
        try:
            user = User.objects.get(username=validated_data.get('username'))
        except User.DoesNotExist:
            raise serializers.ValidationError('User {} does not exists'.format(validated_data.get('username')))

        # ensure username has not been followed before
        if validated_data.get('username', None) in is_following:
            raise serializers.ValidationError('You cannot follow someone that you already follow.')

        # ensure you don't follow yourself
        current_username = self.context.get('request').user.username
        if current_username == validated_data.get('username'):
            raise serializers.ValidationError('You cannot follow yourself.')

        # follow
        profile = TABLE.objects.get(user__username=validated_data.get('username'))
        current_profile.follow(profile)
        return current_profile
