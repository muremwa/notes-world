# notes world 
This is a website for users to create notes, work on them, collaborate with friends(other users)

made in [**Django 2.0**](https://djangoproject.com  "Django website")

> **requires python 3.x**

**Note**
the frontend requires [**Bootstrap framework**](http://getbootstrap.com "Bootstrap wesite") 4.x and [JQuery](http://jquery.com "JQuery website")

## getting started

1. Clone the repo
    ```bash
        git clone https://www.github.com/muremwa/notes-world
    ```

2. Install the requirements
    ```bash
        pip install requirements.txt
    ```

3. Make migartions
    ```bash
        python manage.py makemigartions notes
        python manage.py makemigartions account
        python manage.py migrate
    ```

4. Run Local server 
    ```bash
        python manage.py runserver
    ```

5. Browse

    Psing your browser navigate to your local server at [port 8000](http://127.0.0.1:8000)
