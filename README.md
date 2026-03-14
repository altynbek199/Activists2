ab:

```
ab -k -c 5 -n 20000 'http://localhost:8000/' & \
ab -k -c 5 -n 2000 'http://localhost:8000/event/get?page=1' & \
ab -k -c 5 -n 3000 'http://localhost:8000/chat/history?limit=50' & \
ab -k -c 5 -n 5000 'http://localhost:8000/user/users' 
```