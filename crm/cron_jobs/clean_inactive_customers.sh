#!/bin/bash

# Run the Django command to delete inactive customers
DELETED_COUNT=$(python3 manage.py shell -c "
import django
django.setup()
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

cutoff = timezone.now() - timedelta(days=365)
customers_to_delete = Customer.objects.filter(orders__isnull=True, created_at__lt=cutoff).distinct()
count = customers_to_delete.count()
customers_to_delete.delete()
print(count)
")

# Log the result with a timestamp
echo \"$(date '+%Y-%m-%d %H:%M:%S') - Deleted $DELETED_COUNT inactive customers\" >> /tmp/customer_cleanup_log.txt
