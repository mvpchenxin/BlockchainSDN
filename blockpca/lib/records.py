import blockpcaapi
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization as serial
from blockpca.lib import blockchain


def store_record(data_bytes, user_password_hash):


    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend(),
    )

    serialized_private_key = private_key.private_bytes(
        serial.Encoding.PEM,
        serial.PrivateFormat.PKCS8,
        serial.BestAvailableEncryption(user_password_hash),
    )

    public_key = private_key.public_key()

    serialized_public_key = public_key.public_bytes(
        serial.Encoding.PEM,
        serial.PublicFormat.SubjectPublicKeyInfo,
    )

    ciphertext = public_key.encrypt(
        data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )

    with open('/tmp/encrypted.txt', 'wb') as encrypted_file:
        encrypted_file.write(ciphertext)



    blockpca_api = blockpcaapi.connect('127.0.0.1', 5001)
    blockpca_file_handle = blockpca_api.add('/tmp/encrypted.txt')
    blockpca_hash = blockpca_file_handle['Hash']
    medical_data_hash = blockpca_hash.encode(encoding='UTF-8')



    medical_data_sign = private_key.sign(
        medical_data_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    public_key_in_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    blockchain_id = blockchain.add_blockchain_entry(medical_data_hash,
                                                    medical_data_sign,
                                                    public_key_in_bytes,
                                                    public_key_in_bytes)

    os.remove('/tmp/encrypted.txt')
    return (serialized_private_key, blockchain_id)


def retrieve_record(blockchain_id, serialized_private_key, user_password_hash):
    data = blockchain.lookup_blockchain_entry(blockchain_id)
    blockpca_hash = data['blockpca_hash']

    blockpca_api = blockpcaapi.connect('127.0.0.1', 5001)

    encrypted_file = blockpca_api.cat(blockpca_hash)

    private_key = serialization.load_pem_private_key(
        serialized_private_key,
        password=user_password_hash,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    public_key.verify(
        data['user_sig'],
        data['blockpca_hash'],
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return private_key.decrypt(
        encrypted_file,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )
