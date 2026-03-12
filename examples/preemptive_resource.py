"""Preemptive resource: higher-priority jobs interrupt lower-priority users."""

from asimpy import Environment, Interrupt, Process
from asimpy import Preempted, PreemptiveResource


class Job(Process):
    def init(self, name: str, priority: int, arrive: float, service: float,
             resource: PreemptiveResource):
        self.name = name
        self.priority = priority
        self.arrive = arrive
        self.service = service
        self.resource = resource

    async def run(self):
        await self.timeout(self.arrive)
        print(f"{self.now:>4}: {self.name} (priority {self.priority}) arrives")
        remaining = self.service
        while remaining > 0:
            await self.resource.acquire(priority=self.priority)
            print(f"{self.now:>4}: {self.name} starts (remaining={remaining:.0f})")
            try:
                await self.timeout(remaining)
                remaining = 0
                self.resource.release()
                print(f"{self.now:>4}: {self.name} finishes")
            except Interrupt as intr:
                if isinstance(intr.cause, Preempted):
                    elapsed = self.now - intr.cause.usage_since
                    remaining -= elapsed
                    print(f"{self.now:>4}: {self.name} preempted "
                          f"(remaining={remaining:.0f})")
                else:
                    self.resource.release()
                    raise


env = Environment()
resource = PreemptiveResource(env, capacity=1)

Job(env, "Low",  priority=2, arrive=0,  service=10, resource=resource)
Job(env, "High", priority=1, arrive=3,  service=4,  resource=resource)

env.run()
