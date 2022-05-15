from platform import python_revision
from etext import send_sms_via_email
from phone_num import phone_number

provider = "T-Mobile"

sender_cred = ("bappolter327@gmail.com", "PolterChime")

def button_send_text():
    send_sms_via_email(phone_number, "Doorbell Pressed!", provider, sender_cred, subject="PolterChime Alert")

def pir_send_text():
    send_sms_via_email(phone_number, "Movement Detected!", provider, sender_cred, subject="PolterChime Alert")


