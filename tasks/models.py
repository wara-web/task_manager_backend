from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class Task(models.Model):
    user = models.ForeignKey(
        UserModel, 
        related_name='tasks_created', 
        on_delete=models.CASCADE, 
        verbose_name=_('User')
    )
    title = models.CharField(_('Title'), max_length=100)
    description = models.TextField(_('Description'), blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'), 
        ('complete', 'Complete')
    ], default='pending')
    assigned_to = models.ForeignKey(
        UserModel, 
        related_name='tasks_assigned', 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        ordering = ('created_at', )
        verbose_name = _('task')
        verbose_name_plural = _('tasks')

    def __str__(self):
        return self.title

UserModel = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username
