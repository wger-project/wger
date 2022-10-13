name: Build and push base Docker images

on:
  push:
    branches:
      - "master"
    paths:
        - 'extras/docker/base/Dockerfile'
  schedule:
    - cron: '0 5 1 * *'

jobs:
  path-context:
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

      - name: Build base image
        uses: docker/build-push-action@v3.2.0
        with:
          context: .
          push: true
          file: extras/docker/base/Dockerfile
          platforms: linux/amd64,linux/arm64
          tags: wger/base:latest,wger/base:2.1-dev
