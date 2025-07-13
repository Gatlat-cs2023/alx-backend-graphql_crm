from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Setup GraphQL client (local endpoint)
    transport = RequestsHTTPTransport(url='http://localhost:8000/graphql', verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Simple query to check GraphQL server responsiveness
    query = gql("""
    {
        hello
    }
    """)

    try:
        result = client.execute(query)
        status = "OK"
    except Exception as e:
        status = f"Error: {e}"

    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(f"{now} CRM is alive - GraphQL status: {status}\n")
