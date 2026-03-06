from stockiv.crews.orchestrator.orchestrator import RouterCrew


def run():
    try:
        router = RouterCrew()
        result = router.crew().kickoff(inputs={"request": "analyze FPT"})
        print(result)
    except Exception as e:
        print("FOUND ERROR:", str(e))
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run()
