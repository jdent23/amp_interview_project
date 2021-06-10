#! /usr/bin/python3
import argparse
import mysql.connector
from mysql.connector.constants import ClientFlag

parser = argparse.ArgumentParser()

def main(args):

    print(args.pics_path)
    print(args.label)

    config = {
        'user': 'root',
        'host': '35.223.194.159',
        'client_flags': [ClientFlag.SSL],
        'ssl_ca': 'security_keys/server-ca.pem',
        'ssl_cert': 'security_keys/client-cert.pem',
        'ssl_key': 'security_keys/client-key.pem'
    }

    # now we establish our connection
    cnxn = mysql.connector.connect(**config)
    cnxn.close()
    print("Connection established")

if __name__ == "__main__":
    parser.add_argument('--pics_path', type=str, default=None, help='Path to the folder containing picture', required=True)
    parser.add_argument('--label', type=int, default=-1, help='Label set for pictures in folder', required=False)

    main(parser.parse_args())