from django.db import models
from IQbackend.mixins import base
from authentication.models import User
from architectural_plans.models import ArchitecturalPlan
from chat.roles import (
    Human, Bot
)

class Chat(base.UUIDCreatedUpdatedMixin, models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="user"
    )
    title = models.CharField(
        max_length=255,
        help_text=""
    )
    address = models.CharField(
        null=True,
        blank=True,
        max_length=1000,
        help_text="Address on which this chat gives real estate data"
    )

    def __str__(self):
        return f"Chat - {self.user.username} - {self.title}"

class Message(base.UUIDCreatedUpdatedMixin, models.Model):
    ROLES = [
        (Human.TYPE, Human.DESC),
        (Bot.TYPE, Bot.DESC),
    ]
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="chat"
    )
    text = models.TextField(
        max_length=2000, 
        help_text="Text of the message"
    )
    sources = models.JSONField(
        null=True, 
        blank=True,
        help_text="List of the sources link coming from llm response"
    )
    map = models.JSONField(
        null=True,
        blank=True,
        help_text='Inner and outer polygons of parcel'
    )
    remaining_plans_query = models.JSONField(
        null=True,
        blank=True,
        help_text='Query to get remaining architectural plans'
    )
    architectural_plans = models.ManyToManyField(
        ArchitecturalPlan,
        help_text="Architectural plans recommended by bot"
    )
    sent_by = models.CharField(
        max_length=20,
        choices=ROLES,
        help_text="Message sent by Bot or User"
    ) 

class UncoveredAddress(base.UUIDCreatedUpdatedMixin, models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="uncovered_address_user"
    )
    query = models.TextField(
        null=True,
        blank=True,
        max_length=2000, 
        help_text="Text of the message"
    )
    address = models.CharField(
        null=True,
        blank=True,
        max_length=1000,
        help_text="Address on which this chat does not give real estate data"
    )

    def __str__(self):
        return f"Uncovered Address - {self.user.username} - {self.address}"