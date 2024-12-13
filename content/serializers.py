from rest_framework import serializers

from .models import SpyCat, Mission, Target

import requests

def validate_breed(breed):
    response = requests.get("https://api.thecatapi.com/v1/breeds")
    if response.status_code == 200:
        breeds = [b['name'].lower() for b in response.json()]
        if breed.lower() not in breeds:
            raise serializers.ValidationError(f"Invalid breed: {breed}")
    else:
        raise serializers.ValidationError("Unable to validate breed at this time.")

class SpyCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpyCat
        fields = '__all__'

    def validate_breed(self, value):
        validate_breed(value)
        return value

class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = '__all__'
        read_only_fields = ['mission']

class MissionSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True)

    class Meta:
        model = Mission
        fields = ['id', 'cat', 'is_completed', 'is_done_by', 'targets']

    def validate_targets(self, targets_data):
        if not (1 <= len(targets_data) <= 3):
            raise serializers.ValidationError("A mission must have between 1 and 3 targets.")
        return targets_data

    def create(self, validated_data):
        targets_data = validated_data.pop('targets')
        mission = Mission.objects.create(**validated_data)
        for target_data in targets_data:
            Target.objects.create(mission=mission, **target_data)
        return mission
