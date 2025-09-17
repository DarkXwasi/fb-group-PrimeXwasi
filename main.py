from modules.utils import load_config
from modules.fb_client import FBClient
from modules.group_actions import engage_group

def main():
    config = load_config()
    accounts = config.get("accounts", [])
    groups = config.get("groups", [])
    settings = config.get("settings", {})

    for acc in accounts:
        if not acc.get("active"):
            continue
        print(f"\n=== Using account {acc['uid']} ===")
        client = FBClient(acc["cookie"])

        for g in groups:
            print(f"\n[Group {g['id']}] Engaging...")
            engage_group(client, g["id"], g.get("comment_texts", []), g.get("reactions", []), settings)

if __name__ == "__main__":
    main()