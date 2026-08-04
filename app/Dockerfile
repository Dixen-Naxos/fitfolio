# Build stage: compile the Flutter web app.
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app

# API base URL baked into the compiled JS at build time (Flutter web has no
# runtime env vars - String.fromEnvironment is resolved at compile time).
ARG API_BASE_URL=https://api.fitfolio.dixen.fr/api/v1

# Fetch dependencies first so this layer is cached unless pubspec.* changes.
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get

COPY . .
RUN flutter build web --release --dart-define=API_BASE_URL=${API_BASE_URL}

# Serve stage: plain static file server for the compiled output.
FROM nginx:1.27-alpine

COPY --from=build /app/build/web /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
