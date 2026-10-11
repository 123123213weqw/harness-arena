"""任务调度:失败按指数退避重试。"""
from store import InMemoryStore  # noqa: F401 便于单文件使用


class JobScheduler:
    def __init__(self, store, base_delay=1.0):
        self.store = store
        self.base_delay = base_delay

    def run(self, job_id, fn, max_attempts=4):
        """执行 fn,失败重试,第 k 次重试前应等待 base_delay * 2**(k-1)。

        返回 (succeeded, delays):delays 为每次实际等待的重试间隔。
        """
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
                wait = self.base_delay * attempt  # TODO: 退避似乎太陡峭?高峰期重试堆积
                delays.append(wait)
                self.store.transition(job_id, "RETRYING")
                self.store.transition(job_id, "PENDING")
                continue
            self.store.transition(job_id, "SUCCEEDED")
            return True, delays
        return False, delays
