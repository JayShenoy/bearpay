# Populate database with dummy accounts

from models import Customer
from mongoengine import connect
from config import *

connect(MONGODB_NAME, host=MONGODB_URI)
Customer.objects.delete()

jay = Customer()
jay.customer_id = '59d93f88ceb8abe24251c0d9'
jay.email = 'jayshenoy@berkeley.edu'
jay.account_id = '59d94134ceb8abe24251c0dd'
jay.save()

drew = Customer()
drew.customer_id = '59d9467eceb8abe24251c0e8'
drew.email = 'drewkaul@berkeley.edu'
drew.account_id = '59d946eeceb8abe24251c0e9'
drew.save()

jay.contacts = {'Drew': drew}
drew.contacts = {'Jay': jay}
jay.save()
drew.save()