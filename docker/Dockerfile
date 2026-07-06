FROM python:3.12-slim

RUN pip install \
    pandas \
    numpy \
    scikit-learn \
    pydantic-ai 

# Create an unprivileged user
RUN useradd --create-home agent
USER agent
WORKDIR /workspace