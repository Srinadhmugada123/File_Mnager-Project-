from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Folder, Document, DocumentVersion

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
    
    


class DocumentVersionSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    uploaded_by = serializers.SerializerMethodField()

    class Meta:
        model = DocumentVersion
        fields = ['id', 'version', 'file', 'file_url', 'uploaded_at', 'uploaded_by']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

    def get_uploaded_by(self, obj):
        return obj.uploaded_by.username if obj.uploaded_by else None

 
class DocumentSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    latest_version = serializers.SerializerMethodField()
    latest_file_url = serializers.SerializerMethodField()

    #New
    read_permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=True
    )
    write_permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=True
    )

    class Meta:
        model = Document
        fields = [
            'id', 'name', 'folder',
            'created_at', 'updated_at',
            'created_by', 'updated_by',
            'latest_version', 'latest_file_url',
            'read_permissions', 'write_permissions',
        ]

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None

    def get_updated_by(self, obj):
        return obj.updated_by.username if obj.updated_by else None

    def get_latest_version(self, obj):
        latest = obj.versions.first()
        return latest.version if latest else None

    def get_latest_file_url(self, obj):
        request = self.context.get('request')
        latest = obj.versions.first()
        if latest and latest.file and hasattr(latest.file, 'url'):
            return request.build_absolute_uri(latest.file.url) if request else latest.file.url
        return None
    
    def get_read_users(self, obj):
        return [user.username for user in obj.read_permissions.all()]

    def get_write_users(self, obj):
        return [user.username for user in obj.write_permissions.all()]


    # def create(self, validated_data):
    #     read_users = validated_data.pop("read_permissions", [])
    #     write_users = validated_data.pop("write_permissions", [])
    #     document = Document.objects.create(**validated_data)
    #     if isinstance(read_users, str):
    #         read_users = [int(u) for u in read_users.split(',') if u]
    #     if isinstance(write_users, str):
    #         write_users = [int(u) for u in write_users.split(',') if u]
    #     document.read_permissions.set(read_users)
    #     document.write_permissions.set(write_users)
    #     # refresh_from_db is optional here; get_* methods will fetch from DB
    #     return document
    

class FolderSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    subfolders = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    documents = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = [
            'id', 'name', 'parent',
            'created_at', 'updated_at',
            'created_by', 'updated_by',
            'subfolders', 'documents'
        ]

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None

    def get_updated_by(self, obj):
        return obj.updated_by.username if obj.updated_by else None



