import random
import time
from bs4 import BeautifulSoup

def fetch_group_posts(client, group_id, limit=5):
    """Fetch group posts (latest few)"""
    url = f"/groups/{group_id}"
    res = client.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    posts = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/story.php" in href or "/permalink/" in href:
            full_url = href.split("&__tn__")[0]
            posts.append(full_url)
        if len(posts) >= limit:
            break
    return posts

def react_to_post(client, post_url, reaction="like"):
    """React to a given post"""
    res = client.get(post_url)
    soup = BeautifulSoup(res.text, "html.parser")
    react_link = None

    for a in soup.find_all("a", href=True):
        if "reaction_type=" in a["href"]:
            if reaction in a.text.lower():
                react_link = a["href"]
                break

    if react_link:
        client.get(react_link)
        print(f"[+] Reacted with {reaction} on {post_url}")
    else:
        print(f"[-] Reaction link not found for {post_url}")

def comment_on_post(client, post_url, text="Nice!"):
    """Comment on a post"""
    res = client.get(post_url)
    soup = BeautifulSoup(res.text, "html.parser")
    form = soup.find("form", action=True)

    if form:
        action = form["action"]
        inputs = {i.get("name"): i.get("value", "") for i in form.find_all("input") if i.get("name")}
        inputs["comment_text"] = text
        client.post(action, data=inputs)
        print(f"[+] Commented: {text}")
    else:
        print(f"[-] Comment form not found for {post_url}")

def engage_group(client, group_id, comments, reactions, settings):
    posts = fetch_group_posts(client, group_id, limit=5)
    for post in posts:
        if reactions:
            react = random.choice(reactions)
            react_to_post(client, post, react)
            time.sleep(settings.get("reaction_delay", 10))

        if comments:
            text = random.choice(comments)
            comment_on_post(client, post, text)
            time.sleep(settings.get("comment_delay", 15))