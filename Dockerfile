FROM --platform=linux/amd64 ubuntu:20.04

# ตั้งค่า non-interactive mode สำหรับ apt-get
ENV DEBIAN_FRONTEND=noninteractive

# ติดตั้ง locale และ dependencies
RUN apt-get update && apt-get install -y \
    locales \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    gdal-bin \
    grass \
    wget \
    && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# ตั้งค่า locale เป็น en_US.UTF-8
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# ติดตั้ง Python dependencies
COPY requirements.txt /tmp/
RUN python3 -m venv /env && /env/bin/pip install --no-cache-dir --upgrade pip && \
    /env/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# ตั้งค่า GRASS GIS environment
ENV GRASS_HOME=/usr/lib/grass
ENV PATH=$GRASS_HOME/bin:$PATH
ENV GRASS_DATA_DIR=/grassdata
ENV GRASS_PYTHON=/env/bin/python

# สร้างโฟลเดอร์สำหรับ GRASS data
RUN mkdir -p /grassdata/nc_spm_08_grass7
RUN mkdir -p /app/static

# เพิ่มไฟล์ FastAPI เข้าไปใน container
COPY ./app /app
WORKDIR /app

# เปิดพอร์ตสำหรับ FastAPI
EXPOSE 8000

# รัน Uvicorn server
CMD ["/env/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]