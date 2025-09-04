from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
# from rest_framework.authtoken.models import Token
from .models import Folder, Document, DocumentVersion
from .serializers import (
    UserSerializer,
    FolderSerializer,
    DocumentSerializer,
    DocumentVersionSerializer,
)


# -------------------- Auth APIs --------------------
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST /api/auth/register/
        body: { "username": "...", "password": "..." }
        """
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {
                    "message": "Registration failed", 
                    "errors": {"detail": "username and password are required"}
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {
                    "message": "Registration failed", 
                    "errors": {"detail": "username already taken"}
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(username=username, password=password)
        # token, _ = Token.objects.get_or_create(user=user)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Registration successful",
                "data": {
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST /api/auth/login/
        body: { "username": "...", "password": "..." }
        """
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {
                    "message": "Login failed", 
                    "errors": {"detail": "Invalid credentials"}
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {"message": "Login successful", 
             "data": {
                 "refresh": str(refresh),
                 "access": str(refresh.access_token)
             }
             }, 
            status=status.HTTP_200_OK
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        POST /api/auth/logout/
        Header: Authorization: Token <token>
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {
                "message": "Logout successfull"
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "error": "Invalid token or already loggedout"
                }, status=status.HTTP_400_BAD_REQUEST
            )


#Generate Access token
class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")

        if refresh_token is None:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate refresh token
            refresh = RefreshToken(refresh_token)
            # Create new access token
            new_access_token = str(refresh.access_token)

            return Response(
                {"access": new_access_token},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )

# --------------- Get Users ----------------------
class UserAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK
        )


# -------------------- Folder APIs --------------------

class FolderCreateAPIView(APIView):
    def get(self, request):
        folders = Folder.objects.filter(parent=None).prefetch_related('subfolders', 'documents')
        if not folders.exists():
            return Response(
                {
                    "message": "No folders found", 
                    "data": []
                }, status=status.HTTP_200_OK
            )

        serializer = FolderSerializer(folders, many=True)
        return Response(
            {
                "message": "success", 
                "data": serializer.data
            }, status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save(created_by=request.user, updated_by=request.user)
            out = FolderSerializer(obj).data
            return Response(
                {
                    "message": "Create folder successful", 
                    "data": out
                }, status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "message": "Creation failed", 
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST
        )


class FolderDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Folder.objects.get(pk=pk)
        except Folder.DoesNotExist:
            return None

    def get(self, request, pk):
        folder = self.get_object(pk)
        if not folder:
            return Response(
                {
                    "message": f"Folder with ID {pk} not found", 
                    "data": []
                }, status=status.HTTP_404_NOT_FOUND
            )
        serializer = FolderSerializer(folder)
        return Response(
            {
                "message": "success", 
                "data": serializer.data
            }, status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        folder = self.get_object(pk)
        if not folder:
            return Response(
                {
                    "message": f"Folder with ID {pk} not found"
                }, status=status.HTTP_404_NOT_FOUND
            )

        serializer = FolderSerializer(folder, data=request.data, partial=True)
        if serializer.is_valid():
            obj = serializer.save(updated_by=request.user)
            out = FolderSerializer(obj).data
            return Response(
                {
                    "message": "Update folder successful", 
                    "data": out
                }, status=status.HTTP_200_OK
            )

        return Response(
            {
                "message": "Update failed", 
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        folder = self.get_object(pk)
        if not folder:
            return Response(
                {
                    "message": f"Folder with ID {pk} not found"
                }, status=status.HTTP_404_NOT_FOUND
            )

        folder.delete()
        return Response(
            {
                "message": "Deleted folder successful"
            }, status=status.HTTP_204_NO_CONTENT
        )


# -------------------- Helpers for Versions --------------------

def bump_minor(version_str: str) -> str:
    """
    Safely bump a semantic-like minor version by 0.1 using Decimal.
    '1.0' -> '1.1'
    """
    try:
        v = Decimal(version_str)
    except (InvalidOperation, TypeError):
        v = Decimal('1.0')
    return f"{(v + Decimal('0.1')).quantize(Decimal('0.1'))}"


# -------------------- Document APIs --------------------

class DocumentCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        docs = Document.objects.all().prefetch_related('versions')
        if not docs.exists():
            return Response(
                {
                    "message": "No documents found", 
                    "data": []
                }, status=status.HTTP_200_OK
            )

        serializer = DocumentSerializer(docs, many=True, context={'request': request})
        return Response(
            {
                "message": "success", 
                "data": serializer.data
            }, status=status.HTTP_200_OK
        )

    def post(self, request):
        """
        Create a document with initial version 1.0
        form-data: name, folder, file
        """
        if 'file' not in request.FILES:
            return Response(
                {
                    "message": "Creation failed", 
                    "errors": {"file": ["No file uploaded. Use multipart/form-data with key 'file'."]}
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        name = request.data.get('name')
        folder_id = request.data.get('folder')
        file_obj = request.FILES.get('file')
        folder = Folder.objects.get(pk=folder_id)
       
        if not name or not folder_id:
            return Response(
                {
                    "message": "Creation failed", 
                    "errors": {"detail": "name and folder are required"}
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            folder = Folder.objects.get(pk=folder_id)
        except Folder.DoesNotExist:
            return Response(
                {
                    "message": "Creation failed", 
                    "errors": {"folder": ["Folder not found"]}
                }, status=status.HTTP_400_BAD_REQUEST
            )

        # Create the logical document
        doc = Document.objects.create(
            name=name,
            folder=folder,
            created_by=request.user,
            updated_by=request.user,
        )
        
        def parse_m2m(field):
            if field in request.data:
                if hasattr(request.data, "getlist"):
                    values = request.data.getlist(field)
                else:
                    values = [request.data.get(field)]
                
                ids = []
                for v in values:
                    if isinstance(v, str) and "," in v:
                        ids.extend([int(i) for i in v.split(",") if i.strip().isdigit()])
                    elif str(v).isdigit():
                        ids.append(int(v))
                return ids
            return []
        
        read_ids = parse_m2m("read_permissions")
        write_ids = parse_m2m("write_permissions")

        if read_ids:
            doc.read_permissions.set(User.objects.filter(id__in=read_ids))
            print(f"Assigned read_permissions: {read_ids}")
        
        if write_ids:
            doc.write_permissions.set(User.objects.filter(id__in=write_ids))
            print(f"Assigned write_permissions:{write_ids}")
        
        #create first version 1.0 
        DocumentVersion.objects.create(
            document = doc,
            file = file_obj,
            version = '1.0',
            uploaded_by = request.user,
        )


        #final response with file + permissions
        out = DocumentSerializer(doc, context={'request':request}).data
        out["read_permissions"] = [{"id": uid} for uid in doc.read_permissions.values_list("id", flat=True)]
        out["write_permissions"] = [{"id": uid} for uid in doc.write_permissions.values_list("id", flat=True)]

        return Response(
            {
                "message": "Document created successfully",
                "data" : out
            }, status=status.HTTP_201_CREATED
        )

        # serializer = DocumentSerializer(doc)

        # response_data = serializer.data
        # response_data["read_permissions"] = [{"id": uid} for uid in doc.read_permissions.values_list("id", flat=True)]
        # response_data["write_permissions"] = [{"id": uid} for uid in doc.write_permissions.values_list("id", flat=True)]

        # return Response(
        #     {
        #         "message": "Document created successfully",
        #         "data": response_data,
        #     },
        #     status=201,
        # )

        
        # # Create first version 1.0
        # DocumentVersion.objects.create(
        #     document=doc,
        #     file=file_obj,
        #     version='1.0',
        #     uploaded_by=request.user,
        # )

        # out = DocumentSerializer(doc, context={'request': request}).data
        # return Response(
        #     {
        #         "message": "Document created successfully", 
        #         "data": out
        #     }, status=status.HTTP_201_CREATED
        # )
    


class DocumentDetailAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        try:
            return Document.objects.prefetch_related('versions').get(pk=pk)
        except Document.DoesNotExist:
            return None

    def get(self, request, pk):
        doc = self.get_object(pk)
        if not doc:
            return Response(
                {
                    "message": f"Document with ID {pk} not found", 
                    "data": []
                }, status=status.HTTP_404_NOT_FOUND
            )

        serializer = DocumentSerializer(doc, context={'request': request})
        return Response(
            {
                "message": "success", 
                "data": serializer.data
            }, status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        """
        Update a document.
        - If 'file' provided: create a new version (bump minor: 1.0 -> 1.1).
        - If only metadata (name/folder) provided: update document fields.
        """
        doc = self.get_object(pk)
        if not doc:
            return Response(
                {
                    "message": f"Document with ID {pk} not found"
                }, status=status.HTTP_404_NOT_FOUND
            )

        file_obj = request.FILES.get('file', None)
        name = request.data.get('name', None)
        folder_id = request.data.get('folder', None)

        # Update metadata if provided
        if name is not None:
            doc.name = name
        if folder_id is not None:
            try:
                folder = Folder.objects.get(pk=folder_id)
                doc.folder = folder
            except Folder.DoesNotExist:
                return Response(
                    {
                        "message": "Update failed", 
                        "errors": {"folder": ["Folder not found"]}
                    }, status=status.HTTP_400_BAD_REQUEST
                )

        # If file present, create a new version
        version_msg = None
        if file_obj:
            latest = doc.versions.first()
            next_version = bump_minor(latest.version if latest else '1.0')
            DocumentVersion.objects.create(
                document=doc,
                file=file_obj,
                version=next_version,
                uploaded_by=request.user,
            )
            version_msg = f"New version created: {next_version}"

        doc.updated_by = request.user
        doc.save()

        out = DocumentSerializer(doc, context={'request': request}).data
        message = "Update document successful"
        if version_msg:
            message = f"{message} ({version_msg})"
        return Response(
            {
                "message": message, 
                "data": out
            }, status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        doc = self.get_object(pk)
        if not doc:
            return Response(
                {
                    "message": f"Document with ID {pk} not found"
                }, status=status.HTTP_404_NOT_FOUND
            )

        doc.delete()
        return Response(
            {
                "message": "Deleted document successful"
            }, status=status.HTTP_204_NO_CONTENT
        )


class DocumentHistoryAPIView(APIView):
    """
    GET /api/documents/<id>/history/
    Returns all versions (file + version + uploaded_at + uploaded_by)
    """
    def get(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response(
                {
                    "message": f"Document with ID {pk} not found", "data": []
                }, status=status.HTTP_404_NOT_FOUND
            )

        versions = doc.versions.all()
        serializer = DocumentVersionSerializer(versions, many=True, context={'request': request})
        return Response(
            {
                "message": "success", 
                "data": serializer.data
            }, status=status.HTTP_200_OK
        )
    
        # for version in versions:
        #     history_data.append({
        #         "id": version.id,
        #         "version": version.version,
        #         "file": request.build_absolute_uri(version.file.url) if version.file else None,
        #         "uploaded_at": version.uploaded_at,
        #         "uploaded_by": version.uploaded_by.username if version.uploaded_by else None,
        #         # from Document model
        #         "created_at": doc.created_at,
        #         "created_by": doc.created_by.username if doc.created_by else None,
        #     })

        # return Response(
        #     {
        #         "message": "success",
        #         "data": history_data
        #     }, status=status.HTTP_200_OK
        # )





# -----------------New Task -----------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Document
from .serializers import DocumentSerializer


class DocumentAPIView(APIView):

    def parse_m2m(self, data, field_name):
        """
        Parse ManyToMany values from request.data (form-data).
        Supports:
        - Multiple keys (read_permissions=1, read_permissions=2)
        - Comma-separated string (read_permissions="1,2,3")
        """
        if field_name in data:
            if hasattr(data, "getlist"):  # form-data with multiple values
                values = data.getlist(field_name)
            else:  # raw JSON or single field
                values = [data.get(field_name)]

            ids = []
            for v in values:
                if isinstance(v, str) and "," in v:
                    ids.extend([int(i) for i in v.split(",") if i.strip().isdigit()])
                elif str(v).isdigit():
                    ids.append(int(v))
            return ids
        return []

    # 🔹 GET: All docs or single doc
    def get(self, request, pk=None):
        if pk:
            doc = Document.objects.filter(pk=pk).first()
            if not doc:
                return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = DocumentSerializer(doc)
            return Response(serializer.data)
        docs = Document.objects.all()
        serializer = DocumentSerializer(docs, many=True)
        return Response(serializer.data)

    # 🔹 POST: Create document
    def post(self, request):
        data = request.data.copy()

        read_ids = self.parse_m2m(request.data, "read_permissions")
        write_ids = self.parse_m2m(request.data, "write_permissions")

        # remove M2M fields before serializer validation
        data.pop("read_permissions", None)
        data.pop("write_permissions", None)

        serializer = DocumentSerializer(data=data)
        if serializer.is_valid():
            doc = serializer.save()

            # Assign M2M after save
            if read_ids:
                doc.read_permissions.set(read_ids)
            if write_ids:
                doc.write_permissions.set(write_ids)

            # Refresh data
            serializer = DocumentSerializer(doc)
            return Response(
                {"message": "Document created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🔹 PUT: Update document
    def put(self, request, pk=None):
        doc = Document.objects.filter(pk=pk).first()
        if not doc:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        read_ids = self.parse_m2m(request.data, "read_permissions")
        write_ids = self.parse_m2m(request.data, "write_permissions")

        data.pop("read_permissions", None)
        data.pop("write_permissions", None)

        serializer = DocumentSerializer(doc, data=data, partial=True)
        if serializer.is_valid():
            doc = serializer.save()

            if read_ids:
                doc.read_permissions.set(read_ids)
            if write_ids:
                doc.write_permissions.set(write_ids)

            serializer = DocumentSerializer(doc)
            return Response(
                {"message": "Document updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🔹 DELETE: Remove document
    def delete(self, request, pk=None):
        doc = Document.objects.filter(pk=pk).first()
        if not doc:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        doc.delete()
        return Response({"message": "Document deleted"}, status=status.HTTP_204_NO_CONTENT)
