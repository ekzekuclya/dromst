# from django.db import models
#
#
# class TelegramUser(models.Model):
#     user_id = models.IntegerField(unique=True)
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255, blank=True, null=True)
#     username = models.CharField(max_length=255, blank=True, null=True)
#     date_joined = models.DateTimeField(auto_now_add=True)
#     is_operator = models.BooleanField(default=False)
#     is_super_admin = models.BooleanField(default=False)
#
#     def __str__(self):
#         return self.username if self.username else "None"