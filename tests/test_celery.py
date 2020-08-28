from celery.result import AsyncResult


res = AsyncResult("1147ef38-a005-4e92-b9d4-359becd50a79")
print(res.get())
