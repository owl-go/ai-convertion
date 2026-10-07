class TaskService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, title):
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 80:
            raise ValueError("标题需为 1–80 个字符")
        return self.repository.create(title.strip())

    def list_tasks(self):
        return self.repository.list_tasks()

    def complete(self, task_id):
        task = self.repository.complete(task_id)
        if task is None:
            raise LookupError("任务不存在")
        return task
