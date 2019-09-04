from utils.argument_parser import receive_arguments
from Analytics.authentication import GAuth


@GAuth.require("analytics", "v3")
@receive_arguments
def generate_view_rows(analytics, view_id):
    result = analytics.data().realtime().get(
        ids=f"ga:{view_id}",
        metrics='rt:pageviews',
        dimensions='rt:pagePath,rt:minutesAgo,rt:country,rt:city,rt:pageTitle',
        filters=r"rt:pagePath=~/primo-explore/.*docid.*",
        sort="rt:minutesAgo"
    ).execute()

    rows = result["rows"]
    return rows


@GAuth.require("analytics", "v3")
def get_available_views(analytics):
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
    return analytics.management().accounts().list().execute()
