import logging
from celery import shared_task
from datetime import datetime
from graphene_django.utils.testing import graphql_query

logger = logging.getLogger(__name__)

@shared_task
def generate_crm_report():
    # GraphQL query to fetch CRM data
    query = """
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """
    
    try:
        # Execute GraphQL query
        response = graphql_query(query)
        data = response.json()['data']
        
        # Extract metrics
        customers = data.get('totalCustomers', 0)
        orders = data.get('totalOrders', 0)
        revenue = data.get('totalRevenue', 0)
        
        # Format log message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"
        
        # Write to log file
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(log_message)
            
        logger.info("Successfully generated CRM report")
        
    except Exception as e:
        logger.error(f"Failed to generate CRM report: {str(e)}")
        raise