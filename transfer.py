import requests
import json
from config import *
from models import *
from mongoengine import connect

connect(MONGODB_NAME, host=MONGODB_URI)

def get_customer_id(recording):
	return '59d93f88ceb8abe24251c0d9'

def email_transfer(sender_id, amount, recipient_name):
	sender = Customer.objects(customer_id=sender_id).first()
	recipient = sender.contacts[recipient_name]

	pending_transfer = PendingTransfer()
	pending_transfer.sender_account = sender.account_id
	pending_transfer.amount = amount
	pending_transfer.recipient_account = recipient.account_id
	pending_transfer.save()

	transfer_id = str(pending_transfer.id)

	return transfer_id

def transfer_money(transfer_id):
	transfer = PendingTransfer.objects(id=transfer_id).first()

	url = 'http://api.reimaginebanking.com/accounts/{}/transfers?key={}'.format(transfer.sender_account, C1_API_KEY)
	payload = {
	  'medium': 'balance',
	  'payee_id': transfer.recipient_account,
	  'amount': transfer.amount
	}

	# Transfer money
	response = requests.post( 
		url, 
		data=json.dumps(payload),
		headers={'content-type':'application/json'},
		)

	if response.status_code == 201:
		transfer.delete()
		return 'Transferred money'
	else:
		return 'Failed to transfer money'