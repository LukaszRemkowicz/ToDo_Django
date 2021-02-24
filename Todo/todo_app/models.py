from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

"""Profile, maybe for later use. Not used now"""


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=30, null=True)
    description = models.CharField(max_length=400, null=True)
    link = models.CharField(max_length=400, null=True)


    def __str__(self):
        return self.text
