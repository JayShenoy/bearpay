from flask import Flask, render_template, request, redirect, url_for, make_response, session
from flask_cors import CORS, cross_origin
import os
import requests
import json
from config import *
from models import *
from mongoengine import connect
from sparkpost import SparkPost

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

connect(MONGODB_NAME, host=MONGODB_URI)
sp = SparkPost(SPARKPOST_API_KEY)

@app.route('/')
def home():
	return 'Welcome to Bear Pay!'

@app.route('/customer/<customer_id>')
def customer_page(customer_id):
	customer = Customer.objects(customer_id=customer_id).first()
	
	if customer is not None:
		# Get customer name
		url = 'http://api.reimaginebanking.com/customers/{0}?key={1}'.format(customer_id, C1_API_KEY)
		response = requests.get(url)
		response_body = json.loads(response.content)
		name = '{0} {1}'.format(response_body['first_name'], response_body['last_name'])

		# Get account balance
		url = 'http://api.reimaginebanking.com/accounts/{0}?key={1}'.format(customer.account_id, C1_API_KEY)
		response = requests.get(url)
		response_body = json.loads(response.content)
		balance = response_body['balance']

		return render_template('index.html', transfers=customer.transfer_messages, name=name, balance=balance)
	else:
		return 'No customer with this ID'

@app.route('/email-transfer', methods=['POST'])
@cross_origin()
def email_transfer():
	password, amount, recipient_name = request.json['password'], request.json['amount'], request.json['recipient_name']
	sender = Customer.objects(password=password.lower()).first()

	if sender is None:
		return json.dumps('The password you provided is invalid')

	recipient = sender.contacts[recipient_name.lower()]

	pending_transfer = PendingTransfer()
	pending_transfer.sender_account = sender.account_id
	pending_transfer.amount = amount
	pending_transfer.recipient_account = recipient.account_id
	pending_transfer.save()

	transfer_id = str(pending_transfer.id)

	# Get information about sender
	url = 'http://api.reimaginebanking.com/customers/{0}?key={1}'.format(sender.customer_id, C1_API_KEY)
	response = requests.get(url)
	response_body = json.loads(response.content)

	if response.status_code == 200:
		full_name = '{0} {1}'.format(response_body['first_name'], response_body['last_name'])

		# Values to fill in template
		substitutions = {
			'sender': full_name,
			'amount': amount,
			'transfer_id': transfer_id
		}

		# Send email via SparkPost
		sp_response = sp.transmissions.send(
			recipients=[recipient.email],
			from_email='jay@jayshenoy.com',
			template=SPARKPOST_TEMPLATE_ID,
			substitution_data=substitutions
			)

		return json.dumps('Sent transfer email')
	else:
		return json.dumps('Failed to find information about sender')

@app.route('/transfer-money/<transfer_id>')
def transfer_money(transfer_id):
	transfer = PendingTransfer.objects(id=transfer_id).first()

	if transfer is None:
		return 'Cannot transfer funds'

	url = 'http://api.reimaginebanking.com/accounts/{0}/transfers?key={1}'.format(transfer.sender_account, C1_API_KEY)
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
		# Get information about sender
		url = 'http://api.reimaginebanking.com/accounts/{0}?key={1}'.format(transfer.sender_account, C1_API_KEY)
		response = requests.get(url)
		response_body = json.loads(response.content)
		sender_customer_id = response_body['customer_id']
		url = 'http://api.reimaginebanking.com/customers/{0}?key={1}'.format(sender_customer_id, C1_API_KEY)
		response = requests.get(url)
		response_body = json.loads(response.content)
		sender_name = '{0} {1}'.format(response_body['first_name'], response_body['last_name'])
		sender = Customer.objects(customer_id=sender_customer_id).first()

		# Get information about recipient
		url = 'http://api.reimaginebanking.com/accounts/{0}?key={1}'.format(transfer.recipient_account, C1_API_KEY)
		response = requests.get(url)
		response_body = json.loads(response.content)
		recipient_customer_id = response_body['customer_id']
		url = 'http://api.reimaginebanking.com/customers/{0}?key={1}'.format(recipient_customer_id, C1_API_KEY)
		response = requests.get(url)
		response_body = json.loads(response.content)
		recipient_name = '{0} {1}'.format(response_body['first_name'], response_body['last_name'])
		recipient = Customer.objects(customer_id=recipient_customer_id).first()

		# Add message about transaction to customer logs
		sender.transfer_messages.insert(0, 'To {0}: ${1}'.format(recipient_name, transfer.amount))
		recipient.transfer_messages.insert(0, 'From {0}: ${1}'.format(sender_name, transfer.amount))
		sender.save()
		recipient.save()

		transfer.delete()
		return redirect(url_for('customer_page', customer_id=recipient_customer_id, new=1))
	else:
		return 'Failed to transfer money'

if __name__ == '__main__':
    app.run(debug=True)
