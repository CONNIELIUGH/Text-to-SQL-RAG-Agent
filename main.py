from src.agent import run_agent


def main():
    print("Tesla Demand Planning Agent")
    print("Type 'exit' to quit.\n")

    while True:
        user_question = input("You: ").strip()

        if user_question.lower() in {"exit", "quit"}:
            break

        result = run_agent(user_question)

        if result["status"] == "done":
            print("\nAgent:", result["answer"], "\n")

        elif result["status"] == "needs_clarification":
            print("\nAgent:", result["message"], "\n")

        else:
            print("\nAgent:", result.get("answer") or result.get("message"), "\n")


if __name__ == "__main__":
    main()