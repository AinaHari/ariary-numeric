from rest_framework import serializers
from .models import CustomsCase, DocumentRequirement, CustomsDocument, CustomsEvent


class DocumentRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequirement
        fields = ["id", "name", "is_required", "provided", "notes"]


class CustomsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomsEvent
        fields = ["id", "status", "description", "created_at"]


class CustomsDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomsDocument
        fields = ["id", "name", "file", "created_at"]


class CustomsCaseSerializer(serializers.ModelSerializer):
    requirements = DocumentRequirementSerializer(many=True, read_only=True)
    events = CustomsEventSerializer(many=True, read_only=True)
    documents = CustomsDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomsCase
        fields = ["reference", "description", "origin_country", "destination_country", "mode",
                  "status", "notes", "requirements", "events", "documents", "created_at", "updated_at"]
        read_only_fields = ["reference", "created_at", "updated_at"]


class CustomsCaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomsCase
        fields = ["description", "origin_country", "destination_country", "mode", "notes"]
