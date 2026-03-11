from crewai.flow.flow import Flow, start, listen, router, or_
from pydantic import BaseModel


class MyState(BaseModel):
    count: int = 0


class MyFlow(Flow[MyState]):
    @start()
    def initialize(self):
        self.state.count = 0

    @listen(initialize)
    def do_work(self):
        self.state.count += 1
        print(f"Doing Analysis (Node)... count: {self.state.count}")
        return
    @listen("loop_back")
    def evaluate_director_decision(self):
        print(f"Re evaluate (Node)... count: {self.state.count}")
        self.state.count += 1

    @listen(or_(do_work, evaluate_director_decision))
    def do_report(self):
        print(f"Doing Report (Node)... count: {self.state.count}")
        return
    
    @router(or_(do_report,evaluate_director_decision))
    def check_work(self):
        print(f"Checking work... count: {self.state.count}")
        if self.state.count < 3:
            print(f"Failed approved")

            return "loop_back"
        return "finish"

    @listen("finish")
    def done(self):
        print("Done!")


if __name__ == "__main__":
    flow = MyFlow()
    flow.plot()
    flow.kickoff()
