# Auth templates

ESTELA_AUTH_NAME = ".estela.yaml"

ESTELA_AUTH = """\
token: $estela_token
host: $estela_host
"""


# Init project templates

ESTELA_DIR = ".estela"

DATA_DIR = "project_data"

DOCKER_APP_DIR = "/usr/src/app"

DOCKER_DEFAULT_PYTHON_VERSION = "3.9"

DOCKER_DEFAULT_REQUIREMENTS = "requirements.txt"

DOCKER_DEFAULT_ENTRYPOINT = "git+https://github.com/bitmakerla/estela-entrypoint.git"

DOCKER_REQUESTS_ENTRYPOINT = "git+https://github.com/bitmakerla/estela-requests-entrypoint"

DOCKERFILE_NAME = "Dockerfile-estela"

PROXY_CA_NAME = "bitmaker-proxy-ca.crt"

DOCKERFILE = """\
FROM python:$python_version

RUN apt-get update \\
    && apt-get install -y --no-install-recommends ca-certificates \\
    && rm -rf /var/lib/apt/lists/*
COPY .estela/{proxy_ca_name} /usr/local/share/ca-certificates/bitmaker-proxy.crt
RUN update-ca-certificates
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \\
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \\
    CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# must be in base image
RUN pip install $entrypoint
RUN mkdir -p {app_dir}
WORKDIR {app_dir}
COPY . {app_dir}

RUN pip install --no-cache-dir -r $requirements_path
RUN mkdir /fifo-data
""".format(
    app_dir=DOCKER_APP_DIR,
    proxy_ca_name=PROXY_CA_NAME,
)

DOCKERFILE_SELENIUM = """\
FROM python:$python_version-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install Chrome, Xvfb, dbus, and X11 dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    wget gnupg2 ca-certificates git \\
    xvfb xdg-utils dbus \\
    fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 \\
    libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \\
    libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 \\
    libxrandr2 libxss1 libxtst6 \\
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub \\
       | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \\
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \\
       http://dl.google.com/linux/chrome/deb/ stable main" \\
       > /etc/apt/sources.list.d/google-chrome.list \\
    && apt-get update \\
    && apt-get install -y --no-install-recommends google-chrome-stable \\
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY .estela/{proxy_ca_name} /usr/local/share/ca-certificates/bitmaker-proxy.crt
RUN update-ca-certificates
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \\
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \\
    CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

RUN pip install $entrypoint
RUN mkdir -p {app_dir}
WORKDIR {app_dir}
COPY . {app_dir}

RUN pip install --no-cache-dir mitmproxy==9.0.1 --ignore-requires-python
RUN pip install --no-cache-dir -r $requirements_path

# Pre-install chromedriver and fix permissions
RUN sbase install chromedriver \\
    && chmod -R 777 /usr/local/lib/python$python_version/site-packages/seleniumbase/drivers/

# Prepare dbus runtime directory
RUN mkdir -p /run/dbus && chmod 777 /run/dbus

# Entrypoint starts Xvfb and dbus before running the spider
COPY .estela/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
""".format(
    app_dir=DOCKER_APP_DIR,
    proxy_ca_name=PROXY_CA_NAME,
)

SELENIUM_ENTRYPOINT_SH = """\
#!/bin/bash
# Start Xvfb for headed Chrome (UC mode needs a display)
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp -ac &
sleep 2

# Start dbus to suppress Chrome dbus errors
mkdir -p /run/dbus
dbus-daemon --system --nopidfile 2>/dev/null || true

exec "$@"
"""

ESTELA_YAML_NAME = "estela.yaml"

ESTELA_YAML = """\
project:
  pid: "$project_pid"
  python: "$python_version"
  requirements: "$requirements_path"
  entrypoint: "$entrypoint"
deploy:
  ignore: ["$project_data_path",".git"]
"""

# General templates

OK_EMOJI = "\U00002705"
BAD_EMOJI = "\U0000274C"
CLOCK_EMOJI = "\U000023F3"
