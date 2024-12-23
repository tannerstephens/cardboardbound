FROM node AS vite-app

WORKDIR /app/client
COPY ./frontend .

RUN ["npm", "install"]
RUN ["npm", "run", "build"]

FROM nginx:alpine

WORKDIR /usr/share/nginx/

RUN rm -rf html
RUN mkdir html

WORKDIR /

COPY ./nginx/nginx.conf /etc/nginx
COPY --from=vite-app ./app/client/build /usr/share/nginx/html

EXPOSE 80
ENTRYPOINT ["nginx", "-g", "daemon off;"]
