ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-aiohttp \
    py3-requests \
    ffmpeg

# Copy service files
COPY rootfs /

# Make scripts executable
RUN chmod a+x /etc/services.d/azure_foundry/run
RUN chmod a+x /usr/bin/azure_foundry_service.py