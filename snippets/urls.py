from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from snippets import views


urlpatterns = [
    path("snippets/", views.SnippetList.as_view(), name="snippet-list"),
    path("snippets/<int:pk>/", views.SnippetDetail.as_view(), name="snippet-detail"),
    path(
        "snippets/<int:pk>/highlight/",
        views.SnippetHighlight.as_view(),
        name="snippet-highlight",
    ),  
    path("users/", views.UserList.as_view(), name="user-list"),
    path("users/<int:pk>/", views.UserDetail.as_view(), name="user-detail"),
    path('users/create/', views.create_user, name='create-user'),
    path('users/delete/', views.delete_user, name='delete-user'),
    path('audit-records/', views.AuditRecordList.as_view(), name='audit-record-list'),
    path('audit-records/<int:pk>/', views.AuditRecordDetail.as_view(), name='audit-record-detail'),
    path('login/', views.LoginTokenView.as_view(), name='api_login'),
    path("", views.api_root),
]

urlpatterns = format_suffix_patterns(urlpatterns)
