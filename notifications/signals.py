from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from pip._vendor.pyparsing.core.Regex import sub

from courses.models import Comment
from courses.models import DiscussionSubscription
from notifications.models import Notification
from django.core.mail import send_mail

@receiver(post_save, sender=Comment)
def notify_subscribers_on_new_comment(sender, instance, created, **kwargs):
    if not created:
        return

    discussion = instance.discussion
    subscribers = DiscussionSubscription.objects.filter(discussion=discussion).exclude(user=instance.user)

    for sub in subscribers:
        Notification.objects.create(
            user=sub.user,
            discussion=discussion,
            comment=instance,
            message=f"پاسخ جدیدی در بحث '{discussion.title}' ثبت شد."
        )

        # ایمیل (اختیاری)
        send_mail(
            subject="🗨 پاسخ جدید در Discussion",
            message=f"{instance.user.first_name} یک پاسخ جدید نوشته در بحث: {discussion.title}",
            from_email="noreply@example.com",
            recipient_list=[sub.user.email],
            fail_silently=True,
        )
channel_layer = get_channel_layer()
async_to_sync(channel_layer.group_send)(
    f"user_{sub.user.id}",
    {
        "type": "send_notification",
        "message": f"پاسخ جدید در '{discussion.title}'",
    }
)