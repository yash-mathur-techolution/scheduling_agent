from google.adk.agents import Agent
import re


from drive_service.tools.rag_tool import tickets_tool, articles_tool


def after_model_callback(callback_context, llm_response):
    # print("LLM Response in after model callback: ", llm_response.content.parts)
    # print("LLM Response in after model callback [LENGTH]: ", len(llm_response.content.parts))
    if llm_response.content.parts[0].text:
        print("Replacing nested: ", llm_response.content.parts[0].text)
        new_text = re.sub(r"<article: (\d+)>", r"[View Article](https://coupa.freshservice.com/a/solutions/articles/\1)", llm_response.content.parts[0].text)
        new_text = re.sub(r"<ticket: (\d+)>", r"[View Ticket](https://coupa.freshservice.com/a/tickets/\1)", new_text)
        llm_response.content.parts[0].text = new_text
    return llm_response


# Respond to the user query, STRICTLY using the information returned by the tickets_tool and articles_tool. Do not answer the queries based on you existing or general knowledge. Ensure that all answers are based upon information explicitly provided to you. Ensure you always give the article id as <article: __> and ticket_id as <ticket: __> in your responses.

INSTRUCTIONS_RAG = """## AI Assistant Prompt

**Primary Directive:** Your primary function is to answer user queries using **only** the information retrieved from the `articles_tool` and `tickets_tool`. You are strictly forbidden from using any pre-existing or general knowledge.

**Response Guidelines:**

1.  **Exclusive Sourcing:** Every piece of information in your response must be directly traceable to the content provided by the tools for the current query. If the tools do not provide an answer, state that you do not have enough information.
2.  **Mandatory Citations:** You must cite the source for each piece of information you provide.
    * Place the citation tag at the end of the relevant sentence or paragraph.
    * If a section draws from multiple sources, list all relevant citation tags at the end of that section.

**Citation Formatting:**
* **Articles:** `<article: [Insert Article ID here]>`
* **Tickets:** `<ticket: [Insert Ticket ID here]>`

**Example:**

If the user asks, "What is the status of my order?", your response should look like this:

> Your order #12345 has been shipped <ticket: 56789>. For more details on our shipping policy, you can refer to our guide on shipping times <article: 345>."""

rag_agent = Agent(
    model="gemini-2.0-flash-001",
    instruction=INSTRUCTIONS_RAG,
    name="tickets_and_articles_agent",
    tools=[tickets_tool, articles_tool],
    # after_agent_callback=after_agent_callback,
    after_model_callback=after_model_callback,
    # after_tool_callback=after_tool_callback,
)

