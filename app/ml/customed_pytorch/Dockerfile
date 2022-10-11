# FROM gcr.io/deeplearning-platform-release/tf-gpu:latest
FROM gcr.io/deeplearning-platform-release/pytorch-gpu.1-12
# Copy from local file system to container
COPY requirements.txt /usr/src
WORKDIR /usr/src
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y libgl1-mesa-dev && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade setuptools && \
    pip install --no-cache-dir --upgrade wandb && \
    pip install --no-cache-dir -r requirements.txt