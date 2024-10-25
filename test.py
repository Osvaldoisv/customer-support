import uuid
from langchain_core.messages.tool import ToolMessage
from get_db import update_dates, db
from graphs.primary_assistant import part_4_graph
from utilities import _print_event


# Update with the backup file so we can restart from the original place in each section
db = update_dates(db)
thread_id = str(uuid.uuid4())

tutorial_questions = [
    "Hi, what time is my flight?",
    "Am I allowed to upgrade my flight to something later? I want to check out later today.",
    "Update my flight to sometime next week then.",
    "The next available option is great.",
    "What about accommodation and transportation?",
    "Yes, I think I'd like an affordable hotel for my week-long stay (7 days). And I'll want to rent a car.",
    "Okay, could you make a reservation at your recommended hotel? Sounds nice.",
    "Yeah, go ahead and book anything that's moderately priced and has availability.",
    "Now, as for a car, what are my options?",
    "Great, let's just pick the cheapest option. Go ahead and book for 7 days.",
    "Great, what recommendations do you have for tours?",
    "Are they available while I'm there?",
    "Interesting, I like museums, what options are there?",
    "Okay, great, pick one and I'll save it for my second day there."
]


config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        "passenger_id": "3442 587242",
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}

_printed = set()
# We can reuse the tutorial questions from part 1 to see how it does.
for question in tutorial_questions:
    events = part_4_graph.stream(
        {"messages": ("user", question)}, config, stream_mode="values"
    )
    for event in events:
        _print_event(event, _printed)
    snapshot = part_4_graph.get_state(config)
    while snapshot.next:
        # We have an interrupt! The agent is trying to use a tool, and the user can approve or deny it
        # Note: This code is all outside of your graph. Typically, you would stream the output to a UI.
        # Then, you would have the frontend trigger a new run via an API call when the user has provided input.
        try:
            user_input = input(
                "Do you approve of the above actions? Type 'y' to continue;"
                " otherwise, explain your requested changed.\n\n"
            )
        except:
            user_input = "y"
        if user_input.strip() == "y":
            # Just continue
            result = part_4_graph.invoke(
                None,
                config,
            )
        else:
            # Satisfy the tool invocation by
            # providing instructions on the requested changes / change of mind
            result = part_4_graph.invoke(
                {
                    "messages": [
                        ToolMessage(
                            tool_call_id=event["messages"][-1].tool_calls[0]["id"],
                            content=f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input.",
                        )
                    ]
                },
                config,
            )
        snapshot = part_4_graph.get_state(config)
