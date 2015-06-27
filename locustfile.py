import json
import random

from locust import HttpLocust, TaskSet, task

class ScheduleTaskSet(TaskSet):
    @task
    def load_slots_of_room(self):
        room_response = self.client.get("/rooms")
        if not room_response.content: return

        rooms = json.loads(room_response.content)['items']
        room = random.choice(rooms)

        self.client.get("/rooms/{}/slots".format(room['id']))

class MyLocust(HttpLocust):
    host = "http://localhost/api"
    task_set = ScheduleTaskSet
    min_wait = 1000
    max_wait = 3500
