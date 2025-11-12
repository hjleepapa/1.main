import secrets

# Generate a 256-bit random number and convert to a string
secret_key = str(secrets.SystemRandom().getrandbits(256))
print(secret_key)