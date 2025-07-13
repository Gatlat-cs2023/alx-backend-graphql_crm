# crm/tasks.py
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

@shared_task
def generate_crm_report():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transport = RequestsHTTPTransport(url='http://localhost:8000/graphql', verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query {
        customers { id }
        orders { id totalAmount }
    }
    """)

    try:
        result = client.execute(query)
        total_customers = len(result["customers"])
        total_orders = len(result["orders"])
        total_revenue = sum(float(order["totalAmount"]) for order in result["orders"])

        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{now} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue\n")

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{now} - ERROR: {e}\n")
