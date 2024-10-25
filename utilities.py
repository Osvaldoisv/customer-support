from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from state.state import State
# from langchain.schema import HumanMessage
from typing import Callable
from langchain_core.messages import ToolMessage


def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    else:
        print("Currently in: primary_assistant")
    message = event.get("messages")
    context = event.get("context")
    if context and context not in _printed:
        print("================================= Context Extracted =================================")
        print(context)
        _printed.add(context)
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)


def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    def entry_node(state: State) -> dict:

        if len(state["messages"][-1].tool_calls) > 1:
            # limit the tool calls to one element
            state["messages"][-1].tool_calls = state["messages"][-1].tool_calls[:1]
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]

        return {
            "messages": [
                ToolMessage(
                    content=f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user."
                    f" The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name},"
                    " and the booking, update, other other action is not complete until after you have successfully invoked the appropriate tool."
                    " If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary host assistant take control."
                    " Do not mention who you are - just act as the proxy for the assistant.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

    return entry_node

    # def __init__(self, assistant_name: str):
    #     self.assistant_name = assistant_name

    # def __call__(self, state: State):
    #     last_human_message = None
    #     for message in reversed(state["messages"]):
    #         if isinstance(message, HumanMessage):
    #             last_human_message = message.content
    #             break

    #     if last_human_message:
    #         if self.assistant_name == "property_informer":
    #             query_result = context_information.invoke({"query": last_human_message})
    #         else:
    #             query_result = context_information_primary_assistant.invoke({"query": last_human_message})
    #         return {"context": query_result}
    #     else:
    #         return {"context": ""}
