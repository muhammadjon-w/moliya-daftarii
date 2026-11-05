from django.db import models


class AccountModel(models.Model):
    id = models.BigIntegerField(primary_key=True, help_text="Telegram user id")
    first_name = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    username = models.CharField(max_length=64, blank=True, null=True)
    language_code = models.CharField(max_length=16, blank=True, null=True)
    chat_id = models.BigIntegerField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    trial_ends_at = models.DateTimeField()
    paid_until = models.DateTimeField(blank=True, null=True)
    last_reminder = models.CharField(max_length=40, blank=True, null=True)
    blocked_bot = models.BooleanField(default=False)

    class Meta:
        app_label = "accounts"
        db_table = "accounts"
        indexes = [models.Index(fields=["trial_ends_at"]), models.Index(fields=["paid_until"])]

    def __str__(self):
        return f"{self.id} {self.first_name or ''}".strip()
