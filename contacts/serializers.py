from rest_framework import serializers
from .models import Contact, Campaign_Emails, Campaign, Email, Instructions, Profile
from django.contrib.auth.models import User

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class Campaign_EmailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign_Emails
        fields = '__all__'
    
class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'

class InstructionsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)  # Adding user_id as a write-only field

    class Meta:
        model = Instructions
        fields = ['id', 'user', 'user_id', 'first_name', 'last_name', 'email', 'app_password',
                  'second_email', 'second_app_password', 'third_email', 'third_app_password']
        read_only_fields = ['id', 'user']  # id and user should be read-only

    def validate_user_id(self, value):
        """
        Check if the user with the provided user_id exists.
        """
        try:
            user = User.objects.get(pk=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(pk=user_id)
        instructions = Instructions.objects.create(user=user, **validated_data)
        return instructions

    def update(self, instance, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(pk=user_id)
        instance.user = user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
        
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']  # Add other fields as needed
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']
        
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested serializer for User model

    class Meta:
        model = Profile
        fields = ['user', 'image', 'phone']
        
class DeleteLeadsSerializer(serializers.Serializer):
    delete_list = serializers.ListField(child=serializers.CharField())
    campaign_name = serializers.CharField()

