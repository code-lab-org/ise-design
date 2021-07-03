FROM tiangolo/uvicorn-gunicorn-fastapi

RUN apt-get update && apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash
RUN apt-get install -y nodejs

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY ./requirements.txt .
RUN python -m pip install -r requirements.txt

COPY ./package*.json .
RUN npm install

COPY ./resources /app/resources
COPY ./webpack.config.js .
COPY ./src /app/src
COPY ./app /app/app
RUN npm run build

ENV ISE_REGISTER_PASSCODE=passcode
ENV ISE_DATABASE_URL=sqlite:///data.db
ENV ISE_SECRET="change me"

ENV ISE_ADMIN_EMAIL="admin@example.com"
ENV ISE_ADMIN_PASSWORD=admin
