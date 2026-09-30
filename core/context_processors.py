from datetime import datetime
from .models import SiteSettings, SocialLink, CurrentlyBuilding


def site_context(request):
    """
    Global context processor injecting singleton site settings, active social links,
    and active status into all template renderings.
    """
    settings = SiteSettings.get_settings()
    social_links = SocialLink.objects.filter(is_active=True).order_by("display_order")
    currently_building = CurrentlyBuilding.objects.filter(is_active=True).order_by("display_order")[:4]

    return {
        "site_settings": settings,
        "global_socials": social_links,
        "global_hero_socials": [s for s in social_links if s.show_in_hero],
        "global_nav_socials": [s for s in social_links if s.show_in_nav],
        "global_footer_socials": [s for s in social_links if s.show_in_footer],
        "global_currently_building": currently_building,
        "current_year": datetime.now().year,
    }
