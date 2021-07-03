# ISE Design Module

Industrial and Systems Engineering Design Module

Paul Grogan <pgrogan@stevens.edu>

## Usage (Direct)

This application can be used directly with Python and Node.js.

### Requirements

The following are required prior to installing or using this application.
 - Python 3
 - Node.js v14

### Dependencies

To install Python dependencies, run the following from the project root.
```shell
python -m pip install -r requirements.txt
python -m pip install uvicorn
```

To install Node.js dependencies, run the following from the project root.
```shell
npm install
```

To build the application, run the following from the project root.
```shell
npm run build
```

### Execution

To use the application, run the following from the project root.
```shell
npm run start
```

The application is available via a web browser at http://localhost. The default admin username is `admin@example.com` with password `admin`. The default registration passcode is `passcode`.

### Customization

The following settings are configurable either via environment variables or using a `.env` file in the project root:
 - ISE_SECRET: server-side authorization secret (default: `change me`)
 - ISE_DATABASE_URL: database connection string (default: `sqlite:///./data.db`)
 - ISE_ADMIN_EMAIL: default admin username (default: `admin@example.com`)
 - ISE_ADMIN_PASSWORD: default admin password (default: `admin`)
 - ISE_REGISTER_PASSCODE: default registration passcode (default: `passcode`)
 - ISE_LOGIN_LIFETIME_SECONDS: default login lifetime in seconds (default: `7200`)

## Usage (Docker)

This application can also be used as a Docker image/container.

### Requirements

The following are required to use this application in Docker mode.
 - Docker

### Build Image

```shell
docker build -t code-lab/ise-design .
```

### Run Container

Simple.
```shell
docker run -it code-lab/ise-design
```
The application is available via a web browser at http://localhost. The default admin username is `admin@example.com` with password `admin`. The default registration passcode is `passcode`.

Advanced.
```shell
docker volume create ise_data
docker run --name ise-design --restart always --volume ise_data:/data --env "ISE_DATABASE_URL=sqlite:////data/data.db" --env "ISE_SECRET=secret" --env "ISE_ADMIN_EMAIL=admin@example.com" --env "ISE_ADMIN_PASSWORD=admin" --env "ISE_REGISTER_PASSCODE=passcode" code-lab/ise-design
```
The application is available via a web browser at http://localhost.
