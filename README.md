# notes world 
This is a website for users to create notes, work on them, collaborate with friends(other users).  
The site is served [here](https://notesworld.pythonanywhere.com).

made in [**Django 2.0**](https://djangoproject.com  "Django website")

> **requires python 3.x**

**Note**
the frontend requires [**Bootstrap framework**](http://getbootstrap.com "Bootstrap website") 5.x and [ReactJs](http://react.me, "React website")

> dropped use of JQuery.
 - - -
## Features
1. User can ***sign* up** or ***sign in***.
2. Users can <span style="color: yellow;">send</span>, <span style="color: yellow;">accept</span> or <span style="color: yellow;">deny</span> connection requests from other users just like **<span style="color: blue;">facebook</span> friend requests** or **LinkedIn connections.**
3. User can create notes in **Markdown**.
4. Users can add their connections to collaborate on notes
5. Users receive notifications for comments or replies they're mentioned in, when they get requests, when their requests are accepted and when they are added as collaborators to a note.
6. Notes are either ***private*** (only the owner can see it), ***connected*** (only your connections can see them) and ***Public*** (anyone can see them).
7. A note being for connected users does not mean others can edit it. It has to be collaborative.
8. The comment section is made in **ReactJS**. The source code of the comment section can be found [here](https://github.com/muremwa/notes-world-comment).
9. You can mention a user in the comment sections using *@username* for them to receive a notification.
10. You can edit and delete your own comments.
11. A note user can delete comments they don't like no matter the owner of the comment.  

- - -
**The source code of the comment section can be found [here](https://github.com/muremwa/notes-world-comment).**

- - - 
## getting started

1. Clone the repo
    ```bash
        git clone https://github.com/muremwa/notes-world.git
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
