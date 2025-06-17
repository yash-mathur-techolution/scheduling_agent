# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import warnings
from typing import Optional, Union, List

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

from drive_service.shared_libraries.atlassian_api_toolset_new import JiraApiToolset
from drive_service.shared_libraries.constants.confluence_tool_filters import user_tools, content_access_tools, space_tools, template_tools, core_workflow_tools, knowledge_extraction_tools

from drive_service.tools import bq_connector
# from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION

# Environment configuration
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") or "DEFAULT"


confluence_tool_filter = [*user_tools, *content_access_tools, *space_tools, *template_tools, *core_workflow_tools, "download_attachment", *knowledge_extraction_tools,"search_for_issues_using_jql","parse_jql_queries","sanitise_jql_queries"]

# Initialize Jira toolset and attach token
jira_tool_set = JiraApiToolset(
    access_token=ACCESS_TOKEN,
    tool_filter=confluence_tool_filter#["search_content_by_cql","get_current_user","get_audit_records"]
)
jira_tool_set.configure_access_token_auth(ACCESS_TOKEN)

# Configure logging and warnings
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

# Define callbacks to refresh token if session state updates

def after_agent_callback(callback_context: CallbackContext):
    print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT [STATE] (After agent):\n{callback_context._invocation_context.session.state}\n\n{'*'*60}\n{'*'*60}\n")
    if callback_context._invocation_context.session.state:
        state = callback_context._invocation_context.session.state.copy()
        # for key, value in state.items():  
            # if 'temp:jiraAuthRush7' in key:
            #     print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
            #     jira_tool_set.configure_access_token_auth(value)
            #     tools = jira_tool_set.get_tools()[:10]
            #     callback_context._invocation_context.agent.tools = tools
            #    print("REINITIALIZED TOOLS 1")
            # if 'temp:jira' in key:
            #     print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
            #     jira_tool_set.configure_access_token_auth(value)
            #     tools = jira_tool_set.get_tools()[:10]
            #     callback_context._invocation_context.agent.tools = tools
            #     print("REINITIALIZED TOOLS 2")
            # elif "openIdConnect" in key:
            #     access_token = ACCESS_TOKEN
            #     jira_tool_set.configure_access_token_auth(access_token)
            #     tools = jira_tool_set.get_tools()[:10]
            #     callback_context._invocation_context.agent.tools = tools
            #     print("REINITIALIZED TOOLS 3")

def before_agent_callback(callback_context: CallbackContext):
    print(f"\n{'*'*60}\n{'*'*60}\n\nCALLBACK_CONTEXT [STATE] (Before agent):\n{callback_context._invocation_context.session.state}\n\n{'*'*60}\n{'*'*60}\n")
    if callback_context._invocation_context.session.state:
        state = callback_context._invocation_context.session.state.copy()
        for key, value in state.items():  
            # if 'temp:jiraAuthRush7' in key:
            #     print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
            #     jira_tool_set.configure_access_token_auth(value)
            #     tools = jira_tool_set.get_tools()[:10]
            #     callback_context._invocation_context.agent.tools = tools
            #     print("REINITIALIZED TOOLS 1")
            if 'temp:jira' in key:
                print(f"\n{'*'*60}\nUPDATED ACCESS TOKEN STATE:\n{value}\n{'*'*60}\n")
                jira_tool_set.configure_access_token_auth(value)
                tools = jira_tool_set.get_tools()[:10]
                tools.append(bq_connector.get_data_from_big_query)
                callback_context._invocation_context.agent.tools = tools
                print("REINITIALIZED TOOLS 2")
            # elif "openIdConnect" in key:
            #     access_token = ACCESS_TOKEN
            #     jira_tool_set.configure_access_token_auth(access_token)
            #     tools = jira_tool_set.get_tools()[:10]
            #     callback_context._invocation_context.agent.tools = tools
            #     print("REINITIALIZED TOOLS 3")
                # callback_context._invocation_context.session.state["temp:jiraAuth"] = ACCESS_TOKEN

# Build the agent with Jira tools

tools = jira_tool_set.get_tools()[:10]  # Limit to first 10 tools for performance
tools.append(bq_connector.get_data_from_big_query)  # Add BigQuery tool

root_agent = Agent(
    model="gemini-2.0-flash-001",
    global_instruction="You are a Jira and Bigquery Agent",
    # instruction="You have access to tools for being a Jira Agent",
    name="jira_agent",
    tools=tools,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)