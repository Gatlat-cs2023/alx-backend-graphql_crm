"""
Cron jobs for CRM:
- log_crm_heartbeat: logs a heartbeat every 5 minutes.
- update_low_stock: runs a mutation to restock low stock products every 12 hours.
"""

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

def update_low_stock():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql("""
    mutation {
        updateLowStockProducts {
            updatedProducts {
                id
                name
                stock
            }
            message
        }
    }
    """)

    try:
        result = client.execute(mutation)
        updated_products = result["updateLowStockProducts"]["updatedProducts"]
        message = result["updateLowStockProducts"]["message"]

        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(f"{now} - {message}\n")
            for product in updated_products:
                log_file.write(f"    Product: {product['name']} - Stock: {product['stock']}\n")

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(f"{now} - ERROR running update_low_stock: {e}\n")

if __name__ == "__main__":
    log_crm_heartbeat()
    update_low_stock()
