FROM ubuntu:20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    zip \
    unzip \
    openjdk-8-jdk \
    python3 \
    python3-pip \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install buildozer cython

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Build APK
RUN buildozer android debug

# Create output directory
RUN mkdir -p /output

# Copy APK to output directory
RUN cp bin/*.apk /output/

# Default command
CMD ["ls", "-la", "/output/"]
