### Sử dụng vectorDB Pinecone AWS khu vực us-east-1(free) - index237 - model: text-embedding-ada-002(1536)

***
# Cài và tạo thư mục chứa môi trường ảo
```
pip install virtualenv
```

```
python -m venv venv
```

***
# Chạy app với local
# Kích hoạt môi trường ảo với windows
```
.\venv\Scripts\activate
```

# Out env
```
deactivate
```

# Cài thư viện
```
pip install -r requirements.txt 
```

```
pip install [name-library]
```

# Run
```
python main.py
```

***
# Chạy app với Docker
# Hướng dẫn chạy với docker 
```
docker run --name rag -p 5000:5000 --env-file .env myhgan1/rag
```

# Lệnh chạy Redis container nếu cần 
```
docker run --name redis -p 6379:6379 -d redis
```