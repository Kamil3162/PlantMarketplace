import base64

client_id='ru3YdkL1gkNFTnqFhD23w8lQEhWkj4bn8WlZ0ER8'
secret='28P0qmUvXKXM0M6pf4NwJbdmessfRF4GXSh7RqkTAXCDEt2c7of7jBhGQ2kbmnxe09SGWyO0R0sPCzwrJCIs7w5Kaoru1M00UHwKL8navW1RbFWAFURDPNIoFy78AYoo'
credentials=f"{client_id}:{secret}"
variable = base64.b64encode(credentials.encode('utf-8'))
print(variable)