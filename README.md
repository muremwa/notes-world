# notes world 
This is a website for users to create notes, work on them, collaborate with friends(other users)

made in [**Django 2.0**](https://djangoproject.com  "Django website")

> **requires python 3.x**

**Note**
the frontend requires [**Bootstrap framework**](http://getbootstrap.com "Bootstrap website") 4.x and [JQuery](http://jquery.com "JQuery website")
 - - -
## Features
1. User can ***sign* up** and ***sign in***.
2. users can <span style="color: yellow;">send</span>, <span style="color: yellow;">accept</span> or <span style="color: yellow;">deny</span> connection requests from other users just like **<span style="color: blue;">facebook</span> friend requests.**
3. User can create notes in **Markdown**
4. Added notifications for users.

- - -
## getting started

1. Clone the repo
    ```bash
        git clone https://www.github.com/muremwa/notes-world.git
    ```

1. Install the requirements
    ```bash
        pip install requirements.txt
    ```

1. Make migrations
    ```bash
        python manage.py makemigrations notes
        python manage.py makemigrations account
        python manage.py makemigrations notifications
        python manage.py migrate
    ```

1. Run Local server 
    ```bash
        python manage.py runserver
    ```

2. Browse

    Using your browser navigate to your local server at [port 8000](http://127.0.0.1:8000)
