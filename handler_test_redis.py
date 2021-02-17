import redis, os

def integrate(event, context):
    url = os.environ.get('redis_url')
    port = os.environ.get('redis_port')
    connection = redis.Redis(host= url, port= port)
    save_test = connection.setex("prueba_redis_agustin", 10, "fucniona")
    print({"Test Save Redis Response" : save_test})
    get_redis_test = connection.get("prueba_redis")
    print({"Test Get Redis Response" : get_redis_test})
    return {"statusCode": 200}