from django.utils import timezone


def year(request):
    """Add variable with current year."""
    return {
        'year': timezone.now().year,
    }
