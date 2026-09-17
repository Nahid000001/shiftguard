from datetime import date


def tax_year_start_year(for_date=None):
    """The starting calendar year of the UK tax year containing for_date.

    The UK tax year runs 6 Apr (year) -> 5 Apr (year+1).
    """
    for_date = for_date or date.today()
    if (for_date.month, for_date.day) >= (4, 6):
        return for_date.year
    return for_date.year - 1


def tax_year_label(start_year):
    return f"{start_year}/{str(start_year + 1)[-2:]}"


def parse_start_year(request):
    year = request.GET.get("year")
    if year and year.isdigit():
        return int(year)
    return tax_year_start_year()


def tax_quarters(start_year):
    """Return the four UK tax quarters for the tax year beginning `start_year`.

    Each item: {"label", "start", "end"}.
    """
    bounds = [
        (date(start_year, 4, 6), date(start_year, 7, 5)),
        (date(start_year, 7, 6), date(start_year, 10, 5)),
        (date(start_year, 10, 6), date(start_year + 1, 1, 5)),
        (date(start_year + 1, 1, 6), date(start_year + 1, 4, 5)),
    ]
    return [
        {"label": f"Q{i + 1} ({start.strftime('%d %b %Y')} – {end.strftime('%d %b %Y')})", "start": start, "end": end}
        for i, (start, end) in enumerate(bounds)
    ]
