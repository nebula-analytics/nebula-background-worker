from Analytics.authentication import GAuth
from utils import receives_config, ConfigMap


@GAuth.require("analytics", "v3")
@receives_config("analytics")
def generate_view_rows(since, analytics, config: ConfigMap):
    """
        Args:
            since (int): period of time from last search
            analytics : the google analytics object passed in by @GAuth.require()
            config (ConfigMap): get configuration setting from ConfigMap(config.yaml)
        Raises:
        Returns:
            list of rows from a view from Google Analytics
    """
    if since is None:
        since = 30
    result = analytics.data().realtime().get(
        ids=f"ga:{config.view_id}",
        metrics='rt:pageviews',
        dimensions='rt:pagePath,rt:minutesAgo,rt:country,rt:city,rt:pageTitle',
        filters=f"rt:pagePath=~/primo-explore/.*docid.*;rt:minutesAgo=~{generate_less_than_re(since)}",
        sort="rt:minutesAgo"
    ).execute()

    if result["totalResults"] > 0:
        return result["rows"]
    return ()


def generate_less_than_re(value: int):
    """
        Args:
            value (int): period of time from last search
        Raises:
        Returns:
            //TODO
    """
    as_string = "%.2d" % value
    n1 = int(as_string[0])
    n2 = int(as_string[1])

    sub = f"[0-9]", f"[0-{n2}]"
    expressions = f"[0-{n1-1}]{sub[0]}", f"[{n1}]{sub[1]}"
    if n1 == 0:
        return expressions[1]
    return "|".join(expressions)


@GAuth.require("analytics", "v3")
def get_available_views(analytics):
    """
        Args:
            analytics : the google analytics object passed in by @GAuth.require()
        Raises:
        Yield:
            list of views from Google Analytics
    """
    accounts = analytics.management().accounts().list().execute()
    for account in accounts["items"]:
        account_id = account["id"]
        properties = analytics.management().webproperties().list(accountId=account_id).execute()
        for webp in properties["items"]:
            web_id = webp["id"]
            views = analytics.management().profiles().list(
                accountId=account_id,
                webPropertyId=web_id).execute()
            for view in views["items"]:
                yield view


@GAuth.require("analytics", "v3")
def get_current_account(analytics):
    """
        Args:
            analytics : the google analytics object passed in by @GAuth.require()
        Raises:
        Returns:
            current logged in account
    """
    return analytics.management().accounts().list().execute()
