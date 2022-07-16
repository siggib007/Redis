import redis

r = redis.Redis(host='localhost', port=6379, db=0)
r.set('foo', 'bar')
print("The result of {} is {}".format('foo',r.get('foo').decode('ascii')))