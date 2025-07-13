#!/usr/bin/env python3

import asyncio
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup GraphQL client
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Define date range (last 7 days)
today = datetime.now()
week_ago = today - timedelta(days=7)

# GraphQL query
query = gql("""
query GetRecentOrders($startDate: DateTime!) {
  orders(orderDate_Gte: $startDate) {
    id
    customer {
      email
    }
  }
}
""")

# Main logic
async def main():
    try:
        variables = {"startDate": week_ago.isoformat()}
        result = await client.execute_async(query, variable_values=variables)

        orders = result.get("orders", [])
        with open("/tmp/order_reminders_log.txt", "a") as log_file:
            for order in orders:
                line = f"{datetime.now().isoformat()} - Order ID: {order['id']} - Email: {order['customer']['email']}\n"
                log_file.write(line)

        print("Order reminders processed!")

    except Exception as e:
        print(f"Error: {e}")

# Run the script
asyncio.run(main())
