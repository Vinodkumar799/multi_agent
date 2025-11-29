import redis



r = redis.Redis(host='localhost', port=6379, decode_responses=True)


import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

r.set('foo', 'bar')
# True
r.get('foo')
# bar

r.hset('user-session:132', mapping={
    'name': 'John',
    "surname": 'Smith',
    "company": 'Redis',
    "age": 25
})
# True

print(r.hgetall('user-session:132'))
# {'surname': 'Smith', 'name': 'John', 'company': 'Redis', 'age': '29'}

r.close()

