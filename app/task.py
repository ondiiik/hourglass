# MIT license; Copyright (c) 2023 Ondrej Sienczak
class Task:
    tasks = dict()

    def __init__(self, name: str):
        """Async application task

        This is abstraction for any application related task. This can be even
        application component without task body (with empty :meth:`__call__` method).

        Task is registered to set of application tasks and then it is launched automatically
        form application main. It persists in application tasks table even when task body
        is returned. This resolves peer dependencies between application tasks (there is
        no problem with circular dependency as it can be by simple importing of submodules).
        """
        cls = type(self)
        cls.tasks[name] = self

    async def __call__(self):
        """Method to be called asynchronously as task"""
