"""内存任务存储。(mock 参考解)"""
from state import transition


class InMemoryStore:
    def __init__(self):
        self._jobs = {}

    def set(self, job_id, state):
        self._jobs[job_id] = state

    def get(self, job_id):
        return self._jobs.get(job_id, "PENDING")

    def transition(self, job_id, new):
        current = self.get(job_id)
        self._jobs[job_id] = transition(current, new)
        return self._jobs[job_id]

    def snapshot(self):
        return dict(self._jobs)
