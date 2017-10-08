# Populate database with dummy accounts

from models import Customer
from mongoengine import connect
from config import *

connect(MONGODB_NAME, host=MONGODB_URI)
Customer.objects.delete()

jay = Customer()
jay.customer_id = '59d93f88ceb8abe24251c0d9'
jay.email = 'jayrshenoy@gmail.com'
jay.account_id = '59d94134ceb8abe24251c0dd'
jay.password = 'edison'
jay.save()

drew = Customer()
drew.customer_id = '59d9467eceb8abe24251c0e8'
drew.email = 'dkaul888@gmail.com'
drew.account_id = '59d946eeceb8abe24251c0e9'
drew.password = 'texas'
drew.save()

jay.contacts = {'drew': drew}
drew.contacts = {'jay': jay}
jay.save()
drew.save()