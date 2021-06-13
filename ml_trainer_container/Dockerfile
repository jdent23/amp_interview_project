FROM nvidia/cuda:11.3.1-runtime

ADD credentials $HOME/credentials
ADD requirements.txt $HOME/requirements.txt
ADD /trainer/task.py $HOME/trainer/task.py
ADD /trainer/__init__.py $HOME/trainer/__init__.py

RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN python3 -m pip install -r requirements.txt

ENTRYPOINT python3 -m trainer.task 