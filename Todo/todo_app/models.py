from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

"""Profile, maybe for later use. Not used now"""


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    todo_link = models.CharField(max_length=100)
    shared_to = models.CharField(max_length=1000)

    def __str__(self):
        return self.user.username


class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=30, null=True)
    description = models.CharField(max_length=400, null=True)
    link = models.CharField(max_length=400, null=True)
    complete = models.BooleanField(default=False)
    date_added = models.DateField(auto_now_add=True)
    todo_link = models.CharField(max_length=100)

    def __str__(self):
        return self.text
