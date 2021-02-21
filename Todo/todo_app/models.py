from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    to_do_field = models.CharField(max_length=300, null=True)

    def __str__(self):
        return self.user.username
