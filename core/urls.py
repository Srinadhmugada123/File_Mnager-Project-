from django.urls import path
from .views import (
    RegisterAPIView, LoginAPIView, LogoutAPIView,
    UserAPIView,
    FolderCreateAPIView, FolderDetailAPIView,
    DocumentCreateAPIView, DocumentDetailAPIView, DocumentHistoryAPIView, RefreshTokenAPIView, DocumentAPIView
)

urlpatterns = [
    # Auth
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),

    #Token generate
    path('custom/token/refresh/', RefreshTokenAPIView.as_view(), name="custom_token_refresh"),

    #Users
    path("users/", UserAPIView.as_view(), name="users"),

    # Folders
    path("folders/", FolderCreateAPIView.as_view(), name="folder-create"),
    path("folders/<int:pk>/", FolderDetailAPIView.as_view(), name="folder-detail"),

    # Documents
    path("documents/", DocumentCreateAPIView.as_view(), name="document-create"),
    path("documents/<int:pk>/", DocumentDetailAPIView.as_view(), name="document-detail"),
    path("documents/<int:pk>/history/", DocumentHistoryAPIView.as_view(), name="document-history"),
]