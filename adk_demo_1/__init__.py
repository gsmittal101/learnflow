# Makes this folder an agent ADK can load, so `adk run adk_demo_1` and
# `adk web .` both find it. ADK looks for `root_agent` in agent.py.
from . import agent  # noqa: F401
