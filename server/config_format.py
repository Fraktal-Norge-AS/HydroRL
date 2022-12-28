import numpy as np
from uuid import uuid4


class Config:
    def __init__(self):
        self.projects = []
        self.systems = []


class Project:
    def __init__(self, name):
        self.project_id = str(uuid4())
        self.name = name
        self.system_id = None
        self.inflow_id = None
        self.price_trend_id = None
        self.train_episodes = None
