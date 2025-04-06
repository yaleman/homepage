FROM python:3.12-slim

########################################
# add a user so we're not running as root
########################################
RUN useradd homepage

RUN mkdir -p /home/homepage/
RUN chown homepage /home/homepage -R

RUN mkdir -p build/homepage

WORKDIR /build

COPY homepage homepage
COPY uv.lock .
COPY pyproject.toml .

RUN chown homepage /build -R
WORKDIR /
USER homepage

RUN python -m pip install --upgrade --no-warn-script-location pip
RUN python -m pip install --no-cache --no-warn-script-location /build
USER root
RUN rm -rf /build
USER homepage
COPY ./homepage/static /homepage/static
RUN rm -rf /home/homepage/.cache/

# to allow xff headers from docker IPs
ENV FORWARDED_ALLOW_IPS="*"
EXPOSE 8000

HEALTHCHECK --interval=30s --retries=1 \
  CMD [ "/home/homepage/.local/bin/homepage", "--healthcheck" ]

CMD [ "/home/homepage/.local/bin/uvicorn", "--factory", "homepage:get_app", "--host","0.0.0.0", "--port","8000"]
