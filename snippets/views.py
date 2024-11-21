import threading
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, renderers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAdminUser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import Snippet, AuditRecord
from .permissions import IsOwnerOrReadOnly
from .serializers import SnippetSerializer, UserSerializer, AuditRecordSerializer

_thread_local = threading.local()

def set_current_user(user):
    _thread_local.user = user

def get_current_user():
    return getattr(_thread_local, 'user', None)


class SnippetHighlight(generics.GenericAPIView):
    queryset = Snippet.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)


@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "users": reverse("user-list", request=request, format=format),
            "snippets": reverse("snippet-list", request=request, format=format),
            "audit-records": reverse("audit-record-list", request=request, format=format),
        }
    )


class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        set_current_user(self.request.user)
        serializer.save(owner=self.request.user)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )


class UserList(generics.ListAPIView):
    
    def get_queryset(self):
        if self.request.user.is_staff and self.request.query_params.get('show_inactive_users', 'false').lower() == 'true':
            return User.objects.all()
        return User.objects.filter(is_active=True)
    
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    
    def get_queryset(self):
        if self.request.user.is_staff and self.request.query_params.get('show_inactive_users', 'false').lower() == 'true':
            return User.objects.all()
        return User.objects.filter(is_active=True)
    
    serializer_class = UserSerializer


@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Set the current user for audit records
    set_current_user(request.user)

    user = User.objects.create_user(username=username, password=password)
    return Response({"detail": "User successfully created"})


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_user(request):
    username = request.data.get('username')
    user = User.objects.filter(username=username).first()
    user.is_active = False
    user.save()
    
    # Set the current user for audit records
    set_current_user(request.user)

    return Response({"detail": "User deleted"})


@api_view(["POST"])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=400)

    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return Response({"message": "Login successful"}, status=200)
    
    return Response({"error": "Invalid username or password"}, status=401)


class AuditRecordList(generics.ListAPIView):

    def get_queryset(self):
        queryset = AuditRecord.objects.all()
        user_id = self.request.query_params.get('user', None)
        action = self.request.query_params.get('action', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        return queryset
    
    serializer_class = AuditRecordSerializer
    permission_classes = [IsAdminUser]
    
    
class AuditRecordDetail(generics.RetrieveAPIView):

    def get_queryset(self):
        queryset = AuditRecord.objects.all()
        user_id = self.request.query_params.get('user', None)
        action = self.request.query_params.get('action', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        return queryset
    
    serializer_class = AuditRecordSerializer
    permission_classes = [IsAdminUser]


class LoginTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
