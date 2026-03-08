from crewai.flow.flow import Flow, start, listen, router, or_
from pydantic import BaseModel


class MyState(BaseModel):
    count: int = 0


class MyFlow(Flow[MyState]):
    @start()
    def initialize(self):
        self.state.count = 0

    @listen(or_("loop_back", initialize))
    def do_work(self):
        self.state.count += 1
        print(f"Doing work (Node)... count: {self.state.count}")

    @router(do_work)
    def check_work(self):
        print(f"Checking work... count: {self.state.count}")
        if self.state.count < 3:
            return "loop_back"
        return "finish"

    @listen("finish")
    def done(self):
        print("Done!")


if __name__ == "__main__":
    flow = MyFlow()
    flow.plot()
    flow.kickoff()
