import asyncio
from typing import Callable, Dict


class TaskScheduler:
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}

    def is_running(self, name: str) -> bool:
        return name in self.tasks and not self.tasks[name].done()

    def add_task(self, name: str, coro: Callable, *args, **kwargs):
        """Добавляет задачу, если её ещё нет"""
        if self.is_running(name):
            print(f"⚠️ Задача '{name}' уже запущена.")
            return

        task = asyncio.create_task(coro(*args, **kwargs))
        self.tasks[name] = task
        print(f"✅ Задача '{name}' добавлена.")

    async def stop_task(self, name: str):
        """Останавливает задачу"""
        task = self.tasks.pop(name, None)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            print(f"❌ Задача '{name}' остановлена.")

    async def stop_all(self):
        """Останавливает все задачи"""
        names = list(self.tasks.keys())
        for name in names:
            await self.stop_task(name)
