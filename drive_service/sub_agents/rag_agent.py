from google.adk.agents import Agent
from google.genai import types
import re


from drive_service.tools.rag_tool import tickets_tool, articles_tool, service_catalog_tool


def after_model_callback(callback_context, llm_response):
    # print("LLM Response in after model callback: ", llm_response.content.parts)
    # print("LLM Response in after model callback [LENGTH]: ", len(llm_response.content.parts))
    if llm_response.content.parts[0].text:
        print("Replacing nested: ", llm_response.content.parts[0].text)
        new_text = re.sub(r"<article: (\d+)>", r"[View Article](https://coupa.freshservice.com/a/solutions/articles/\1)", llm_response.content.parts[0].text)
        new_text = re.sub(r"<ticket: (\d+)>", r"[View Ticket](https://coupa.freshservice.com/a/tickets/\1)", new_text)
        new_text = re.sub(r"<service: (\d+)>", r"[View Service Catalog](https://servicedesk.coupa.com/support/catalog/items/\1)", new_text)

        llm_response.content.parts[0].text = new_text
    return llm_response

INSTRUCTIONS_RAG = """
***
**Primary Directive:** Your primary function is to answer user queries using **only** the information retrieved from the `find_similar_articles`, `find_similar_tickets`, and `service_catalog_tool` tools. You are strictly forbidden from using any pre-existing or general knowledge.

**Response Guidelines:**

1.  **Exclusive Sourcing:** Every piece of information in your response must be directly traceable to the content provided by the tools for the current query. If the tools do not provide a sufficient answer, clearly state that you do not have enough information to help.
2.  **Comprehensive Answers:** Strive to synthesize the information from the provided tools into a complete and direct answer to the user's question. Do not simply list the articles or tickets that might be relevant.
3.  **Prioritize Articles and Service Catalog:** To best help the user, you should primarily use information from articles and the service catalog. Referencing information from tickets is appropriate only when the user specifically asks about an existing ticket or if the information in the articles or service catalog is insufficient to resolve the user's query.
4.  **Service Catalog Integration:** If the user's query can be answered or solved by a service catalog item, provide its link along with the display_id.
5.  **Mandatory Citations:** You must cite the source for each piece of information you provide. Place the citation tag at the end of the relevant sentence or paragraph. If a section draws from multiple sources, list all relevant citation tags at the end of that section.

**Citation Formatting:**
* **Articles:** `<article: [Insert Article ID here]>`
* **Tickets:** `<ticket: [Insert Ticket ID here]>`
* **Service Catalog:** `<service: [Insert Display ID here]>`
* **Important:** Each citation tag must refer to only **one** article ID, ticket ID, or service catalog display ID.

**Example:**
# If the user asks, "What is the status of my order?", your response should look like this:
# > Your order #12345 has been shipped <ticket: 56789>. For more details on our shipping policy, you can refer to our guide on shipping times <article: 345>. You can also request a status update through our "Order Status Inquiry" service <service: OS-INQ-001>.
"""


rag_agent = Agent(
    model="gemini-2.0-flash-001",
    instruction=INSTRUCTIONS_RAG,
    name="tickets_and_articles_agent",
    tools=[tickets_tool, articles_tool, service_catalog_tool],
    after_model_callback=after_model_callback,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,
    )
)

