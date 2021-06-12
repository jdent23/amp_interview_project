FROM tensorflow/tensorflow:2.5.0-gpu

ADD credentials $HOME/credentials
ADD requirements.txt $HOME/requirements.txt
ADD train.py $HOME/train.py

RUN python3 -m pip install -r requirements.txt

CMD python3 train.py