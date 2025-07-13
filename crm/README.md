# CRM Celery Setup Guide

## Prerequisites
- Redis server installed and running
- Python 3.8+
- Django project configured

## Installation
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start Redis server (if not running):
```bash
redis-server
```

## Running Celery
1. Start Celery worker:
```bash
celery -A crm worker -l info
```

2. Start Celery Beat (for scheduled tasks):
```bash
celery -A crm beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Verification
Check the report logs:
```bash
cat /tmp/crm_report_log.txt
```

Example output:
```txt
2024-03-04 06:00:00 - Report: 150 customers, 320 orders, 12500 revenue
```

## Troubleshooting
- Ensure Redis is running
- Check Celery logs for erros
- Verify task is registered in Django admin under "Periodic Tasks"
```txt
This implementation:
1. Sets up Celery with Redis as the broker
2. Creates a scheduled task that runs every Monday at 6 AM
3. Uses GraphQL to fetch CRM data
4. Logs the report to a file
5. Includes proper error handling and logging

The task will automatically generate reports weekly and append them to the log file. You can monitor the task execution through Celery's logs and verify the reports in `/tmp/crm_report_log.txt`.
```