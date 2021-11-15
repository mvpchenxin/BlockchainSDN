import blockpcaapi
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


with open("public_key.pub", "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )

with open("private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=b'test',
        backend=default_backend()
    )



medical_data_sign = private_key.sign(
    medical_data_hash,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)


public_key_in_bytes = public_key.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo)

print("medical_data_hash:")
print(medical_data_hash)
print("medical_data_sign:")
print(medical_data_sign)
print("public_key_in_bytes")
print(public_key_in_bytes)

