from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    name = models.CharField(max_length=300)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_folders')
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_folders')

    def __str__(self):
        return self.name


class Document(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_documents')
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_documents')

    read_permissions = models.ManyToManyField(User, related_name="documents_can_read", blank=True)
    write_permissions = models.ManyToManyField(User, related_name="documents_can_write", blank=True)

    def __str__(self):
        return self.name


class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    file = models.FileField(upload_to='documents/')
    version = models.CharField(max_length=10, default='1.0')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='uploaded_versions')

    class Meta:
        ordering = ['-uploaded_at']  # newest first

    def __str__(self):
        return f"{self.document.name} v{self.version}"
