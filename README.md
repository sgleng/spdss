# Setup Klompé

1. Clone the project. Alternatively, you can also download the full source from GitHub.
> git clone https://github.com/sgleng/spdss.git
2. Install Python 3 and pip.
> sudo apt-get install python3-pip
3. Consider a virtual environment to prevent conflicts with other tools. For Mac, use the following terminal command **in the correct folder**:
> sudo pip3 install virtualenv 

> virtualenv venv

> source venv/bin/activate
4. Install requirements via pip
> pip install -r requirements.txt
5. This projects uses **cbc** as a solver. Follow the instructions [on their website](https://github.com/coin-or/Cbc) to install it. The following instructions are for MacOS:
> brew tap coin-or-tools/coinor

> brew install cbc
6. Run the server using the following command:
> python manage.py runserver

## Heroku-specific instructions
When using Heroku, make sure to use Python. Furthermore, add the [cbc buildpack](https://github.com/wspringer/heroku-buildpack-cbc) to the app.
1. Go to the app in Heroku, and go to its settings.
2. Click 'Add buildpack' and enter the following URL:
> https://github.com/wspringer/heroku-buildpack-cbc.git
3. Deploy and it should work.

**Note:** SQLite does not work on Heroku, as Heroku is reset after every hour. That means that you should use PostreSQL for database management. Curently, this is not in place. However, this can be achieved easily. Alternatively, you can choose not to use Heroku.

## Setting up the admin
Open the terminal, go to the directory and perform the following commands:
> python manage.py makemigrations

> python manage.py migrate

> python manage.py createsuperuser

# Additional information
* It is possible to use the solver without Django. The solver then has input parameters several dictionaries and lists. Please refer to solver.py for more information.  
