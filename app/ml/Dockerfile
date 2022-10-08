# FROM gcr.io/deeplearning-platform-release/tf-gpu:latest
FROM gcr.io/deeplearning-platform-release/pytorch-gpu.1-12
# Copy from local file system to container

RUN pip install -y timm && \
    pip install -y --upgrade wandb && \
    pip install -y pip3 install opencv-python
    