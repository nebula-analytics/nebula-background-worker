import sys

from Analytics import get_available_views, get_current_account
from utils.argument_parser import receive_arguments


@receive_arguments
def main(view_id):
    display_welcome()
    if view_id is None:
        view_selection_help()
    else:
        pass


def display_welcome():
    user = get_current_account()
    message = f"Welcome to the Nebula Background worker, {user['username']}"
    print(message)
    print("=" * len(message))
    print()


def view_selection_help():
    views = list(get_available_views())
    if not views:
        print("The current account is not authorized to access any analytics data", file=sys.stderr)
        return
    print("Available Views:\n")
    layout = "%-4s | %-12s | %-15s | %-12s"
    print(layout % ("", "Account ID", "Profile ID", "View ID"))
    print("-" * len(layout % ("", "", "", "")))
    for index, view in enumerate(views):
        view_id = view["id"]
        profile_id = view["webPropertyId"]
        account_id = view["accountId"]

        print(layout % (index, account_id, profile_id, view_id))

    print("\nTo complete setup please provide the view_id "
          "argument to this script (We've inserted an example id for you).")
    print(build_run_command(view_id=views[0]["id"]))


@receive_arguments
def build_run_command(path_to_token: str, view_id: str):
    return f"\npython '{__file__}' '{path_to_token}' --view_id '{view_id}'\n"


if __name__ == '__main__':
    main()
