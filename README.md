# TR_EC Backend Server

This is the Backend for TR_EC, the TRanscription Edit and Correction tool.

## Setup
### Create a new virtual environment
python3 -m venv TR_EC_Backend/venv
### Activate the virtual environment
#### Linux/MacOS
source TR_EC_Backend/venv/bin/activate
#### Windows
TR_EC_Backend\venv\Scripts\activate.bat
### Install the dependencies
pip3 install -r TR_EC_Backend/requirements.txt
### Prepare your settings.py and localsettings.py
In TR_EC/setup_templates you will find templates for the requires localsettings.py file. This file is gitignored and holds settings which are specific to your local project. Place it next to settings.py. A random secret key ycan be generated using the command "python manage.py newsecretkey". More Information is in the template files.
### Prepare the database models
python3 manage.py makemigrations usermgmt\
python3 manage.py makemigrations transcriptmgmt\
python3 manage.py makemigrations editmgmt\
python3 manage.py migrate
### Setup Publisher group and a superuser
#### Automatically 
Use the command "python manage.py setup". It will do the following:
1. Get or create the publisher group
2. Guide you through creating a superuser
3. Gives you the option to add the superuser to the publisher group
#### Manually
creating a superuser can be done via the createsuperuser utility.
You can also create a user via the shell like so:
```
python3 manage.py shell
from usermgmt.models import CustomUser
CustomUser.objects.create_superuser('username', password='password')
```
Next, create a publisher group. This can be done in the admin interface or in the shell with for example:
```
from django.contrib.auth import models as auth_models
auth_models.Group.objects.get_or_create(name='Publisher')
```
### Run the server
python3 manage.py runserver
## Testing
### Run all tests
python3 manage.py test
## Python setup
if the python3 name doesnt work on your machine try python instead but make sure (with python --version) that this calls a 3.x python. Same goes for pip3 and pip
