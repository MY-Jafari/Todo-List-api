# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

ARG USE_IRAN_MIRRORS=false

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Replace Debian repositories with Megan mirror if requested
RUN if [ "$USE_IRAN_MIRRORS" = "true" ]; then \
        echo "Types: deb" > /etc/apt/sources.list.d/debian.sources && \
        echo "URIs: https://hub.megan.ir/debian" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Suites: trixie trixie-updates trixie-security" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Components: main contrib non-free non-free-firmware" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg" >> /etc/apt/sources.list.d/debian.sources; \
    fi

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies (always from PyPI)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: Production image
FROM python:3.12-slim

ARG USE_IRAN_MIRRORS=false

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Replace Debian repositories with Megan mirror if requested
RUN if [ "$USE_IRAN_MIRRORS" = "true" ]; then \
        echo "Types: deb" > /etc/apt/sources.list.d/debian.sources && \
        echo "URIs: https://hub.megan.ir/debian" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Suites: trixie trixie-updates trixie-security" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Components: main contrib non-free non-free-firmware" >> /etc/apt/sources.list.d/debian.sources && \
        echo "Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg" >> /etc/apt/sources.list.d/debian.sources; \
    fi

# Install runtime system libraries only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "core.wsgi:application"]
