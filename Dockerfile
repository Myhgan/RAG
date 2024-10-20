FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/venv

# Tạo virtual environment
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file requirements.txt
COPY requirements.txt .

# Cài đặt các dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Expose port 5000
EXPOSE 5000

# Chạy Flask app
CMD ["python", "main.py"]
