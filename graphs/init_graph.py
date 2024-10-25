# from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
# from langgraph.prebuilt import tools_condition

from state.state import State
from tools.flights import fetch_user_flight_information

builder = StateGraph(State)


def user_info(state: State):
    return {"user_info": fetch_user_flight_information.invoke({})}


builder.add_node("fetch_user_info", user_info)
builder.add_edge(START, "fetch_user_info")
