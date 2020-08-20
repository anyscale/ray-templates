import argparse
import numpy as np
import os
import random
import ray
import time

info = ray.init(webui_host="0.0.0.0")
print("info", info)

@ray.remote
class User:
    def __init__(self, index, model_manager):
        self.index = index
        self.model_manager = model_manager
    
    def run(self):
        result = self.model_manager.run.remote()
        ray.get(result)
    
    def ping(self):
        pass

@ray.remote
class UserManager:
    def __init__(self, users, model_manager):
        self.users = users
        self.model_manager = model_manager
        
    def run(self):
        for i in range(500):
            [user.run.remote() for user in self.users]
            time.sleep(0.4)

@ray.remote
class Model:
    def __init__(self, name):
        print("Model {} actor pid {}".format(name, os.getpid()))

    def evaluate(self, size):
        A = np.ones([size, size])
        B = np.ones([size, size])
        return A.dot(B)

@ray.remote
class ModelManager:
    def __init__(self):
        self.model1 = Model.remote("model1")
        self.model2 = Model.remote("model2")
    
    def run(self):
        a = self.model1.evaluate.remote(1000)
        # b = self.model2.evaluate.remote(1000)
        # ray.get([a, b])
        b = self.model2.evaluate.remote(1000)
        ray.get([a, b])
        # ray.get(a)

parser = argparse.ArgumentParser(description='Server')
parser.add_argument('--num-users', type=int)
args = parser.parse_args()

model_manager = ModelManager.remote()
users = [User.remote(index, model_manager) for index in range(args.num_users)]
user_manager = UserManager.remote(users, model_manager)

user_manager.run.remote()

for i in range(200):
    user = random.choice(users)
    a = time.time()
    response = user.ping.remote()
    ray.get(response)
    b = time.time() - a
    print("Pinging user took {}".format(b))
    # ray.timeline(filename="timeline-{}.json".format(i))
    time.sleep(1.0)
