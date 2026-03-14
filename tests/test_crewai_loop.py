"""Test: CrewAI Flow loop pattern — clean single-path loop.

This version merges synthesizer + director into one step per branch to avoid
the or_() deduplication issue. The key insight is:

    @listen(or_(A, B)) fires only ONCE for non-routers (tracked in _fired_or_listeners)
    @router with or_() is EXEMPT from this guard (always fires)

So we need the flow graph to be:

  initialize_setup → execute_first_pass → router → "loop_back" → handle_revision_and_review → router → ...

The router is the only step that needs or_().
"""

from crewai.flow.flow import Flow, start, listen, router, or_
from pydantic import BaseModel


class LoopState(BaseModel):
    loop_count: int = 0
    max_loops: int = 3
    approval: str = "REJECTED"
    version: int = 1


class ReportLoopTestFlow(Flow[LoopState]):
    @start()
    def initialize_setup(self):
        print("[1] initialize_setup")
        self.state.loop_count = 0
        self.state.version = 1

    @listen(initialize_setup)
    def execute_first_pass(self):
        """First pass: synthesizer + director."""
        print(f"[2] execute_first_pass: synthesizer v{self.state.version}")
        self.state.loop_count += 1
        if self.state.loop_count >= self.state.max_loops:
            self.state.approval = "APPROVED"
        else:
            self.state.approval = "REJECTED"
        print(f"    director (loop {self.state.loop_count}): {self.state.approval}")

    @listen("loop_back")
    def handle_revision_and_review(self):
        """Loop-back: re-run synthesizer + director."""
        self.state.version += 1
        print(f"[3] handle_revision_and_review: synthesizer v{self.state.version}")
        self.state.loop_count += 1
        if self.state.loop_count >= self.state.max_loops:
            self.state.approval = "APPROVED"
        else:
            self.state.approval = "REJECTED"
        print(f"    director (loop {self.state.loop_count}): {self.state.approval}")

    @router(or_(execute_first_pass, handle_revision_and_review))
    def evaluate_director_decision(self):
        print(
            f"[4] evaluate: approval={self.state.approval}, loop={self.state.loop_count}"
        )
        if self.state.approval == "APPROVED":
            return "route_to_reporter"
        return "loop_back"

    @listen("route_to_reporter")
    def done(self):
        print(
            f"[5] ✅ DONE — Approved at v{self.state.version}, loop {self.state.loop_count}"
        )


if __name__ == "__main__":
    flow = ReportLoopTestFlow()
    result = flow.kickoff()
    print("\n" + "=" * 50)
    print("Final state:")
    print(f"  approval: {flow.state.approval}")
    print(f"  version:  {flow.state.version}")
    print(f"  loop:     {flow.state.loop_count}")
