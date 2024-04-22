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
    class Meta:
        model = Instructions
        fields = '__all__'
        
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

