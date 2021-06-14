from flask import Flask, render_template, request, redirect
import mysql.connector
from mysql.connector.constants import ClientFlag
from googleapiclient import discovery
import os

app = Flask(__name__)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './credentials/google-storage-cred.json'
  
@app.route('/', methods=["GET", "POST"])
def landing_page():

    if request.method == "GET":
        return render_template('landing_page.html')

    if request.method == "POST":
        if request.form['password'] == "BubbleTea23!":

            job_spec = {
                "jobId": request.form['job_name'],
                "trainingInput": {
                    "scaleTier": "BASIC_GPU",
                    "region": "us-east1",
                    "pythonModule": "trainer.task",
                    "masterConfig": {
                        "imageUri": "gcr.io/amp-interview-project/ml_trainer"
                    }
                }
            }

            project_id = 'projects/amp-interview-project'

            cloudml = discovery.build('ml', 'v1')

            req = cloudml.projects().jobs().create(body=job_spec, parent=project_id)

            response = req.execute()

            '''
            try:
                response = request.execute()
                # You can put your code for handling success (if any) here.

            except errors.HttpError, err:
                # Do whatever error response is appropriate for your application.
                # For this example, just send some text to the logs.
                # You need to import logging for this to work.
                logging.error('There was an error creating the training job.'
                            ' Check the details:')
                logging.error(err._get_reason())
            '''

            return render_template('confirm_start_training.html')

        return redirect('/')

@app.route('/request_label/<topic>', methods=["GET", "POST"])
def request_label_for_picture(topic):
    if request.method == "GET":
        return render_template('request_label.html', image=topic)

    if request.method == "POST":
        label = -1
        if request.form['action'] == 'cat':
            label = 0
        elif request.form['action'] == 'dog':
            label = 1

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

        cursor.execute("UPDATE images SET label=" + str(label) + " WHERE name='" + topic + "';")
        cnxn.commit()
        cnxn.close()

        return redirect('/request_label')


@app.route('/request_label', methods=["GET", "POST"])
def request_label():

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

    cursor.execute("SELECT name FROM images WHERE label=-1 LIMIT 1")
    out = cursor.fetchall()
    cnxn.close()

    if len(out) <= 0:
        return render_template('no_picture_to_label.html')

    return redirect('/request_label/' + out[0][0])
  
  
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)