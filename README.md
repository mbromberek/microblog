
tutorial
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

Uses Flask and Jinja2 to build a dynamic webpage with Python handling the backend

### Create Virtual Environment and install libraries
```
mkvirtualenv microblog
pip install -r requirements.txt
pip install Flask
deactivate
workon microblog
export FLASK_APP=microblog.py
flask run
```


### Reindex Posts Elasticsearch
```
flask shell
from app.models import User, Post
Post.reindex()

# search from command line
query, total = Post.search('food', 1, 5)
total
query.all()
```
