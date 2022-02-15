import uuid
from firebase_admin.messaging import Message
from fcm_django.models import FCMDevice


def get_default_uid():
    return uuid.uuid4().hex[:6].upper()

def send_message_to_user(user, task):
    message_obj = Message(
        data={
            "Task" : task.name,
            "body" : f"New task from {task.company.name}",
        },
    )
    devices = FCMDevice.objects.filter(user=user)
    for device in devices:
        device.send_message(message_obj)
