# Use the Nginx image
FROM nginx:1.25.2
# Remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf && ln -sf /usr/share/zoneinfo/Europe/Athens /etc/localtime && dpkg-reconfigure -fnoninteractive tzdata
# Replace with our own nginx.conf
COPY nginx.conf /etc/nginx/conf.d/
