from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=False, null=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email or self.username


class Address(models.Model):
    LabelChoices = [
        ("home", "HOME"),
        ("work", "WORK"),
        ("other", "OTHER")
    ]

    user = models.ForeignKey(User, related_name="addresses", on_delete=models.CASCADE)
    label = models.CharField(max_length=10, choices=LabelChoices, default="home", blank=True)
    recipient_name = models.CharField(max_length=100, blank=False, null=False)
    phone = models.CharField(max_length=15, blank=False)
    line1 = models.CharField(max_length=255, blank=False, null=False)
    line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=False, null=False)
    state = models.CharField(max_length=100, blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False, default="Nigeria")
    postal_code = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "addresses"
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default=True),
                name="one_default_address_per_user",
            )
        ]

    def __str__(self):
        return f"{self.recipient_name} - {self.city}"
