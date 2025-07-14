
from google.adk.tools.function_tool import FunctionTool
import psycopg2

from vertexai.preview.language_models import TextEmbeddingModel
model = TextEmbeddingModel.from_pretrained("text-embedding-005")

def find_similar_articles(query_text: str):
    """
    Connects to the PostgreSQL database, generates an embedding for the query text,
    and finds articles with the most similar embeddings.

    Args:
        query_text (str): The user's query as a string.

    Returns:
        list: A list of dictionaries, where each dictionary contains the article's ID,
              title, created_at, modified_at, description, and similarity score. Returns an empty list on error.
    """
    conn = None
    similar_articles = []
    limit = 25
    try:
        # --- 1. Generate embedding for the user's query ---
        # The model.encode() method converts the text into a 384-dimension vector (for this model).
        # Ensure your table's VECTOR dimension matches your model's output.
        print(f"Generating embedding for query: '{query_text}'")
        query_embedding =model.get_embeddings([query_text])[0].values

        # Establish a connection to the database
        conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="v1Mk9g>be]*hG(d>",
            host="34.132.230.3",
            port="5432"
        )
        cur = conn.cursor()

        # --- 2. The Cosine Similarity SELECT Query ---
        # The '<=>' operator calculates the cosine distance (1 - cosine similarity).
        # We calculate '1 - (embedding <=> %s)' to get the cosine similarity score.
        select_query = f"""
            SELECT
                article_id,
                title,
                description_text,
                created_at,
                modified_at,
                1 - (embedding <=> %s::vector) AS similarity
            FROM
                articles
            ORDER BY
                similarity DESC
            LIMIT %s;
        """

        # Execute the query with the generated embedding and the limit
        cur.execute(select_query, (query_embedding, limit))

        # Fetch all the results
        results = cur.fetchall()
        for row in results:
            similar_articles.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "similarity": row[3]
            })

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while searching for similar articles: {error}")
    finally:
        # Close the database connection
        if conn is not None:
            conn.close()

    return similar_articles


def find_similar_tickets(query_text: str):
    """
    Connects to the PostgreSQL database, generates an embedding for the query text,
    and finds tickets relevant to the user query.

    Args:
        query_text (str): The user's query as a string.

    Returns:
        list: A list of dictionaries, where each dictionary contains the tickets's ID,
              subject, created_at, updated_at, description, and similarity score. Returns an empty list on error.
    """
    conn = None
    similar_articles = []
    limit = 25
    try:
        # --- 1. Generate embedding for the user's query ---
        # The model.encode() method converts the text into a 384-dimension vector (for this model).
        # Ensure your table's VECTOR dimension matches your model's output.
        print(f"Generating embedding for query: '{query_text}'")
        query_embedding =model.get_embeddings([query_text])[0].values

        # Establish a connection to the database
        conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="v1Mk9g>be]*hG(d>",
            host="34.132.230.3",
            port="5432"
        )
        cur = conn.cursor()

        # --- 2. The Cosine Similarity SELECT Query ---
        # The '<=>' operator calculates the cosine distance (1 - cosine similarity).
        # We calculate '1 - (embedding <=> %s)' to get the cosine similarity score.

        select_query = f"""
            SELECT
                ticket_id,
                subject,
                description_text,
                created_at,
                updated_at,
                1 - (embedding <=> %s::vector) AS similarity
            FROM
                tickets
            ORDER BY
                similarity DESC
            LIMIT %s;
        """

        # Execute the query with the generated embedding and the limit
        cur.execute(select_query, (query_embedding, limit))

        # Fetch all the results
        results = cur.fetchall()
        for row in results:
            similar_articles.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "similarity": row[3]
            })

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while searching for similar articles: {error}")
    finally:
        # Close the database connection
        if conn is not None:
            conn.close()

    return similar_articles


def find_service_items(query_text: str):
    """
    Connects to the PostgreSQL database, generates an embedding for the query text,
    and finds service catalog items relevant to the user query.

    Args:
        query_text (str): The user's query as a string.

    Returns:
        list: A list of dictionaries, where each dictionary contains the service catalog item's enteries
    """
    conn = None
    service_items = []
    limit = 5
    try:
        # --- 1. Generate embedding for the user's query ---
        # The model.encode() method converts the text into a 384-dimension vector (for this model).
        # Ensure your table's VECTOR dimension matches your model's output.
        print(f"Generating embedding for query: '{query_text}'")
        query_embedding =model.get_embeddings([query_text])[0].values

        # Establish a connection to the database
        conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="v1Mk9g>be]*hG(d>",
            host="34.132.230.3",
            port="5432"
        )
        cur = conn.cursor()

        # --- 2. The Cosine Similarity SELECT Query ---
        # The '<=>' operator calculates the cosine distance (1 - cosine similarity).
        # We calculate '1 - (embedding <=> %s)' to get the cosine similarity score.

        select_query = f"""
            SELECT
                catalog_id,
                name,
                display_id,
                created_at,
                updated_at,
                1 - (embedding <=> %s::vector) AS similarity
            FROM
                service_items
            ORDER BY
                similarity DESC
            LIMIT %s;
        """

        # Execute the query with the generated embedding and the limit
        cur.execute(select_query, (query_embedding, limit))

        # Fetch all the results
        results = cur.fetchall()
        for row in results:
            service_items.append({
                "id": row[0],
                "title": row[1],
                "display_id": row[2],
                "similarity": row[4]
            })

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while searching for similar articles: {error}")
    finally:
        # Close the database connection
        if conn is not None:
            conn.close()

    return service_items


articles_tool = FunctionTool(
    func = find_similar_articles
)

tickets_tool = FunctionTool(
    func = find_similar_tickets
)

service_catalog_tool = FunctionTool(
    func = find_service_items
)