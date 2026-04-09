FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom config template
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy website files
COPY . /usr/share/nginx/html

# Railway sets PORT env var dynamically
ENV PORT=80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
