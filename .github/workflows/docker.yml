name: Build and push Docker images

on:
  push:
    branches:
      - master

jobs:
  apache:
    name: Build apache image
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v2.1.0

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2.1.0

      - name: Login to DockerHub
        uses: docker/login-action@v2.0.0
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build image
        uses: docker/build-push-action@v3.2.0
        with:
          context: .
          push: true
          file: extras/docker/demo/Dockerfile
          platforms: linux/amd64,linux/arm64
          tags: wger/demo:latest,wger/demo:2.2-dev,wger/apache:latest,wger/apache:2.2-dev

  prod:
    name: Build production image
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v2.1.0

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2.1.0

      - name: Login to DockerHub
        uses: docker/login-action@v2.0.0
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build image
        uses: docker/build-push-action@v3.2.0
        with:
          context: .
          push: true
          file: extras/docker/development/Dockerfile
          platforms: linux/amd64,linux/arm64
          tags: wger/server:latest,wger/server:2.2-dev,wger/devel:latest,wger/devel:2.2-dev
