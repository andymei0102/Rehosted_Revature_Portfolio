# Andyrew_Project3

SET UP instructions:

download ultralytics with
pip install -U ultralytics


pip install -r requirements.txt


** you need to do the -U flag for ultralytics because you won't find it otherwise



==========Common Commands==========
 * run uvicorn *

py -m uvicorn api.api:app --reload

* run tensorboard *

py -m tensorboard --logdir=runs --port=6006

==========Pytorch==========
you will need to install pytorch on your own, depending on your cuda versions, so we did not include that in the requirements.txt
