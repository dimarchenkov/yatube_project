from datetime import date


def year(request):
    """Add variable with current year."""
    return {
        'year': date.today().year,
    }
