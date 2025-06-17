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

"""Defines tools for brand search optimization agent"""

from google.cloud import bigquery
from google.adk.tools import ToolContext


# Initialize the BigQuery client outside the function
try:
    client = bigquery.Client()  # Initialize client once
except Exception as e:
    print(f"Error initializing BigQuery client: {e}")
    client = None  # Set client to None if initialization fails


def get_data_from_big_query(tool_context: ToolContext, sql_query: str):
    """
    Retrieves all job records scheduled for the current day and formats them as a markdown table.

    This function queries the database for all entries where the 'Received Date'
    matches today's date. It is designed to be called by an orchestrator agent.

    Args:
        tool_context (ToolContext): The exact SQL query to execute.
        sql_query (str): The SQL query string to execute against the BigQuery database, the query should be exactly what the user has requested for and should not be deviated in any kind, retriving relevant information based on date range queries or task name based query.
        
    Table Name : techolution-agentspace.vehicledataset.vehiclescheduledataset

    Returns:
        str: A markdown-formatted string representing a table of job records.
             The table includes the columns: 'Job_ID', 'Task_Name',
             'Received_Date', and 'Delivery_Date'.
             Returns only the table header if no jobs are found or if an error occurs.

    * Always use table name as techolution-agentspace.vehicledataset.vehiclescheduledataset
    * If the user asks about the job being processed, if `requested date` is between `Received_Date` and `Delivery_Date` both dates inclusive, then job is being currently processed, else it will be taken up on the recieved date, or it has already been delivered.
    * The vehicles that are currently being processed are those vehicles that the workers would be currently working on, these include repair jobs, etc.
             
    Example:
        >>> get_data_from_big_query(tool_context : ToolContext, sql_query : str)
        '| Job_ID | Task_Name | Received_Date | Delivery_Date |\\n|---|---|---|---|\\n| J456 | Server Maintenance | 2025-06-13 | 2025-06-14 |\\n| J457 | Database Backup | 2025-06-13 | 2025-06-13 |\\n'
    """
    # from colorama import Fore
    # print(Fore.GREEN + "Executing SQL Query: " + str(sql_query) + Fore.RESET)
    print("Executing SQL Query: ", sql_query)

    if client is None:  # Check if client initialization failed
        return "BigQuery client initialization failed. Cannot execute query."

    query_job = client.query(sql_query)
    results = query_job.result()

    markdown_table = "| Job_ID | Task_Name | Received_Date | Delivery_Date |\n"
    markdown_table += "|---|---|---|---|\n"

    for row in results:
            Job_ID = row.Job_ID if row.Job_ID else "N/A"
            Task_Name = row.Task_Name if row.Task_Name else "N/A"
            Received_Date = row.Received_Date if row.Received_Date else "N/A"
            Delivery_Date = row.Delivery_Date if row.Delivery_Date else "N/A"

            markdown_table += (
                f"| {Job_ID} | {Task_Name} | {Received_Date} | {Delivery_Date}\n"
            )
    
    print("Markdown Table: ", markdown_table)
    return markdown_table

