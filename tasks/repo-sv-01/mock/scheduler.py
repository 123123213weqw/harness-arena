"""任务调度:失败按指数退避重试。(mock 参考解)"""
from store import InMemoryStore  # noqa: F401


class JobScheduler:
    def __init__(self, store, base_delay=1.0):
        self.store = store
        self.base_delay = base_delay

    def run(self, job_id, fn, max_attempts=4):
        delays = []
        attempt = 0
        while attempt < max_attempts:
            self.store.transition(job_id, "RUNNING")
            try:
                fn()
            except Exception:
                attempt += 1
                if attempt >= max_attempts:
                    self.store.transition(job_id, "FAILED")
                    return False, delays
                wait = self.base_delay * 2 ** (attempt - 1)
                delays.append(wait)
                self.store.transition(job_id, "RETRYING")
                self.store.transition(job_id, "PENDING")
                continue
            self.store.transition(job_id, "SUCCEEDED")
            return True, delays
        return False, delays
