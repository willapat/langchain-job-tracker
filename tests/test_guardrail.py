from langchain_core.messages import AIMessage, HumanMessage

from middleware.guardrails import TopicGuardrail


def _state(content):
    return {"messages": [HumanMessage(content=content)]}


def test_on_topic_message_passes_through():
    guardrail = TopicGuardrail()
    assert guardrail.before_agent(_state("show me my applications"), runtime=None) is None


def test_off_topic_message_is_blocked():
    guardrail = TopicGuardrail()
    result = guardrail.before_agent(_state("what's the weather today?"), runtime=None)
    assert result is not None
    assert result["jump_to"] == "end"
    assert "job application tracking" in result["messages"][0]["content"]


def test_off_topic_keyword_with_job_keyword_present_passes():
    guardrail = TopicGuardrail()
    # "job" keyword should win even if an off-topic word is also present
    assert guardrail.before_agent(_state("any news about my job application?"), runtime=None) is None


def test_list_content_is_handled():
    guardrail = TopicGuardrail()
    state = {"messages": [HumanMessage(content=[{"type": "text", "text": "recommend me a recipe"}])]}
    result = guardrail.before_agent(state, runtime=None)
    assert result is not None
    assert result["jump_to"] == "end"


def test_non_human_last_message_passes_through():
    guardrail = TopicGuardrail()
    state = {"messages": [HumanMessage(content="hi"), AIMessage(content="hello")]}
    assert guardrail.before_agent(state, runtime=None) is None


def test_empty_messages_passes_through():
    guardrail = TopicGuardrail()
    assert guardrail.before_agent({"messages": []}, runtime=None) is None
