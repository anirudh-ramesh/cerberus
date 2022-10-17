# from email import message
# from django.conf import settings
# from twillio.rest import Client

# class MessageHandler:
#     phone_number = None
#     otp = None

#     def __init__(self, phone_number, otp):
#         self.phone_number = phone_number
#         self.otp = otp

#     def send_otp_on_phone(self):
#         client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)

#         message = client.message.create(
#             body= f"Your OTP is {self.otp}",
#             from_= "+19282676794",
#             to = self.phone_number
#         )
#         print(message.sid)     