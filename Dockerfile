# build
FROM node:11.12.0-alpine as build-vue
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend .
RUN npm run build

# production
FROM nginx:stable-alpine as production
WORKDIR /app
RUN echo "@community http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories && \
    apk add --no-cache py3-pandas@community py3-numpy@community
RUN apk --update add --no-cache python3 g++ python3-dev musl-dev libxslt-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache
# RUN apk add --no-cache g++ python3-dev musl-dev libxslt-dev
COPY --from=build-vue /app/dist /usr/share/nginx/html
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ./backend/requirements.txt ./
RUN pip install --no-cache -r requirements.txt && \
    pip install --no-cache gunicorn
COPY ./backend .
CMD gunicorn -b 0.0.0.0:5000 -t 150 --graceful-timeout 150 tch_portal:app --daemon && \
      sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf && \
      nginx -g 'daemon off;'
