from django.contrib.auth.models import User
from rest_framework import serializers
from snippets.models import Snippet, AuditRecord, LANGUAGE_CHOICES, STYLE_CHOICES


class SnippetSerializer(serializers.HyperlinkedModelSerializer): 
    owner = serializers.ReadOnlyField(source="owner.username")
    highlight = serializers.HyperlinkedIdentityField(  
        view_name="snippet-highlight", format="html"
    )

    class Meta:
        model = Snippet
        fields = (
            "url",
            "id",
            "highlight",
            "title",
            "code",
            "linenos",
            "language",
            "style",
            "owner",
        )  


class UserSerializer(serializers.HyperlinkedModelSerializer):  
    snippets = serializers.HyperlinkedRelatedField(  
        many=True, view_name="snippet-detail", read_only=True
    )

    class Meta:
        model = User
        fields = ("url", "id", "username", "snippets")  


class AuditRecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AuditRecord
        fields = '__all__'