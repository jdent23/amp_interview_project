#! /usr/bin/python3

import os
import argparse
import mysql.connector
from mysql.connector.constants import ClientFlag
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './credentials/google-storage-cred.json'
storage_client = storage.Client()

parser = argparse.ArgumentParser()

def init_db():

    config = {
        'user': 'root',
        'host': '35.223.194.159',
        'client_flags': [ClientFlag.SSL],
        'ssl_ca': 'credentials/server-ca.pem',
        'ssl_cert': 'credentials/client-cert.pem',
        'ssl_key': 'credentials/client-key.pem'
    }

    cnxn = mysql.connector.connect(**config)
    cursor = cnxn.cursor()
    cursor.execute('CREATE DATABASE db')
    cnxn.close()

    config['database'] = 'db'
    cnxn = mysql.connector.connect(**config)
    cursor = cnxn.cursor()
    cursor.execute("CREATE TABLE images ("
                    "name VARCHAR(255),"
                    "label INT )"
    )
    cnxn.commit()
    cnxn.close()

def add_to_db(args, filenames):

    config = {
        'user': 'root',
        'host': '35.223.194.159',
        'client_flags': [ClientFlag.SSL],
        'ssl_ca': 'credentials/server-ca.pem',
        'ssl_cert': 'credentials/client-cert.pem',
        'ssl_key': 'credentials/client-key.pem',
        'database': 'db'
    }

    cnxn = mysql.connector.connect(**config)

    cursor = cnxn.cursor()

    for filename in filenames:
        cursor.execute("INSERT INTO images VALUES ('" + filename + "', " + str(args.label) + ")")

    cnxn.commit()
    cnxn.close()

def list_db():

    config = {
        'user': 'root',
        'host': '35.223.194.159',
        'client_flags': [ClientFlag.SSL],
        'ssl_ca': 'credentials/server-ca.pem',
        'ssl_cert': 'credentials/client-cert.pem',
        'ssl_key': 'credentials/client-key.pem',
        'database': 'db'
    }

    cnxn = mysql.connector.connect(**config)

    cursor = cnxn.cursor()

    cursor.execute("SELECT * FROM images")
    out = cursor.fetchall()
    print(out)
    cnxn.close()

def upload_to_bucket(args, filenames):
    for filename in filenames:
        try:
            bucket = storage_client.get_bucket('amp_interview_project_images')
            blob = bucket.blob(filename)
            blob.upload_from_filename(os.path.join(args.pics_path, filename))
        except Exception as e:
            print(e)


def main(args):

    print(args.pics_path)
    print(args.label)

    if args.init:
        init_db()
        print("Database initialized")

    filenames = os.listdir(args.pics_path)
    add_to_db(args, filenames)
    upload_to_bucket(args, filenames)



if __name__ == "__main__":
    parser.add_argument('--pics_path', type=str, default=None, help='Path to the folder containing picture', required=True)
    parser.add_argument('--label', type=int, default=-1, help='Label set for pictures in folder', required=False)
    parser.add_argument('--init', action='store_true', default=False, help='Marker for whether database needs initialization before operation', required=False)

    main(parser.parse_args())
    list_db()