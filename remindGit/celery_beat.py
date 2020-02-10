from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send_reminder': {
        'task': 'reminder.tasks.send_reminders',
        'schedule': crontab(minute='*/1')
    }
}