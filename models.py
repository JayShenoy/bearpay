from mongoengine import *

class Customer(Document):
	customer_id = StringField(required=True)
	email = EmailField(required=True)
	account_id = StringField(required=True)
	contacts = DictField()

class PendingTransfer(Document):
	sender_account = StringField(required=True)
	amount = FloatField(required=True)
	recipient_account = StringField(required=True)