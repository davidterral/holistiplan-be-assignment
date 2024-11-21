from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Snippet, AuditRecord
from .views import get_current_user


@receiver(post_save, sender=User)
def create_audit_record_for_user(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    current_user = get_current_user()
    AuditRecord.objects.create(
        user=current_user,
        model_name='User',
        object_id=instance.id,
        action=action,
    )


@receiver(post_delete, sender=User)
def delete_audit_record_for_user(sender, instance, **kwargs):
    current_user = get_current_user()
    AuditRecord.objects.create(
        user=current_user,
        model_name='User',
        object_id=instance.id,
        action='delete',
    )


@receiver(post_save, sender=Snippet)
def create_audit_record_for_snippet(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    current_user = get_current_user()
    AuditRecord.objects.create(
        user=current_user,
        model_name='Snippet',
        object_id=instance.id,
        action=action,
    )


@receiver(post_delete, sender=Snippet)
def delete_audit_record_for_snippet(sender, instance, **kwargs):
    current_user = get_current_user()
    AuditRecord.objects.create(
        user=current_user,
        model_name='Snippet',
        object_id=instance.id,
        action='delete',
    )
