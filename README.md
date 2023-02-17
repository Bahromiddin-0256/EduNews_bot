"# EduNews_bot 2.0" 


**Deployment process**

**Prepare to upload to GitHub**

`pip freeze > requirements.txt`

**Setup database on the server**

Install Redis [Source](https://www.hostinger.com/tutorials/how-to-install-and-setup-redis-on-ubuntu/)

* `sudo apt install redis`

* `redis-cli --version` - check installation

* `sudo systemctl status redis` - check if redis is running


Install Postgresql [Source](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart)

* `sudo apt install postgresql postgresql-contrib`

* `sudo systemctl start postgresql.service`

* `sudo -i -u postgres` - switch to **postgres** user

* `psql` - open **psql** shell,  `\q` - close shell

* `exit` - return tu regular user

* `sudo -u postgres psql` - run the psql command as the postgres account directly with sudo

* `createuser --interactive` - create new user while logged in

* `createdb 'Datamabase name'` - create database with the name

**Clone project from GitHub and configure**

* `git clone project_address`

* `python -m venv venv`
* `source venv/bin/activate` - create and activate venv inside project

* `pip install -r requirements.txt` - install requirements

* `cp env_dict .env`
* `nano .env` - configure environments

**Install Telegram Bot API server**

_Setup Docker and docker compose_ [Source](https://docs.docker.com/engine/install/ubuntu/)

* `curl -fsSL https://get.docker.com -o get-docker.sh`

* `DRY_RUN=1 sudo sh ./get-docker.sh` - install docker

* `sudo apt-get install docker-compose-plugin` - install docker compose

* `docker compose version` - check installation

_Install api server image_ [Source](https://hub.docker.com/r/aiogram/telegram-bot-api)

`docker pull aiogram/telegram-bot-api` - pull the image

_Configure docker compose_

`nano docker-compose.yml` - open editor

_Configuration sample:_

```
version: '3.7'
 
services:
  telegram-bot-api:
    image: aiogram/telegram-bot-api:latest
    environment:
      TELEGRAM_API_ID: "<api-id>"
      TELEGRAM_API_HASH: "<api-hash>"
      TELEGRAM_LOCAL: "1"
    volumes:
      - telegram-bot-api-data:/var/lib/telegram-bot-api
    ports:
      - 8081:8081

volumes:
  telegram-bot-api-data:
```

`docker-compose up -d` - run docker image in the background

`curl localhost:8081` - check api server

**Create service for project**

`sudo nano /etc/systemd/system/bot.service` - open editor to create service

_Configuration sample:_

```
[Unit]
Description=Gunicorn Daemon for FastAPI
After=network.target

[Service]
User=username
Group=www-data
WorkingDirectory=<directory_of_script e.g. /ubuntu/MyProject>
ExecStart=/home/ubuntu/MyProject/venv/bin/gunicorn -c core/gunicorn_conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

_Service management commands:_


* `sudo systemctl start bot` - start bot
* `sudo systemctl stop bot` - stop bot
* `sudo systemctl enable bot` - enable bot restart on reboot
* `sudo service bot restart` - restart bot


**Setup nginx** [Source](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-20-04)

* `sudo apt install nginx` - install nginx
* `systemctl status nginx` - check status

_Edit configuration:_

* `sudo nano /etc/nginx/sites-enabled/default`

_Configuration sample_
```
upstream app_server {
    server unix:/tmp/gunicorn.sock fail_timeout=0;
  }

  server {
    listen 80;
    server_name _;

    root /home/ubuntu/Feedback_bot/static/;

    location / {
      try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Host $http_host;
      proxy_redirect off;
      proxy_pass http://app_server;
    }
  }
```

_Basic nginx commands:_

* `sudo service nginx start` - start nginx
* `sudo service nginx stop` - stop nginx
* `sudo service nginx restart` - restart nginx
* `sudo service nginx reload` - reload nginx without loosing connection