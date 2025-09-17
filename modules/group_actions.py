# modules/group_actions.py
import random
import time
from bs4 import BeautifulSoup

def fetch_group_posts(client, group_id, limit=5):
    resp = client.get(f"/groups/{group_id}")
    if resp is None:
        return False, "no_response", []
    if "login" in resp.url.lower() or resp.status_code != 200:
        return False, "login_required_or_bad_status", []
    html = resp.text
    posts = []
    soup = BeautifulSoup(html, "lxml")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        postid = None
        if "/story.php" in href and "story_fbid=" in href:
            try:
                from urllib.parse import parse_qs, urlparse
                q = parse_qs(urlparse(href).query)
                postid = q.get("story_fbid", [None])[0]
            except:
                postid = None
        elif "/permalink/" in href or "/posts/" in href:
            parts = href.rstrip("/").split("/")
            for p in reversed(parts):
                if p.isdigit():
                    postid = p
                    break
        if postid:
            full_url = href if href.startswith("http") else ("https://mbasic.facebook.com" + href)
            entry = {"post_id": postid, "post_url": full_url}
            if entry not in posts:
                posts.append(entry)
        if len(posts) >= limit:
            break
    return True, "ok", posts

def react_post_simple(client, post_id, reaction_preference=None):
    post_url = f"https://mbasic.facebook.com/story.php?story_fbid={post_id}"
    r = client.get(post_url)
    if r.status_code != 200:
        return False, f"status_{r.status_code}"
    soup = BeautifulSoup(r.text, "lxml")
    like_link = None
    for a in soup.find_all("a", href=True):
        text = (a.get_text() or "").strip().lower()
        if "like" == text or "like this" in text or text.startswith("like"):
            like_link = a["href"]
            break
    if not like_link:
        for a in soup.find_all("a", href=True):
            if "reaction" in a["href"] or "ufi/reaction" in a["href"]:
                like_link = a["href"]
                break
    if not like_link:
        return False, "no_like_link"
    target = like_link if like_link.startswith("http") else ("https://mbasic.facebook.com" + like_link)
    r2 = client.get(target)
    return (r2.status_code == 200), f"followed:{r2.status_code}"

def comment_on_post(client, post_id, text):
    post_url = f"https://mbasic.facebook.com/story.php?story_fbid={post_id}"
    r = client.get(post_url)
    if r.status_code != 200:
        return False, f"status_{r.status_code}"
    soup = BeautifulSoup(r.text, "lxml")
    form = None
    for f in soup.find_all("form", action=True):
        if f.find("input", {"name": "comment_text"}) or "comment" in (f.get("action") or ""):
            form = f
            break
    if form is None:
        form = soup.find("form", action=True)
    if form is None:
        return False, "no_comment_form"
    action = form.get("action")
    if not action.startswith("http"):
        action = "https://mbasic.facebook.com" + action
    data = {}
    for inp in form.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        value = inp.get("value", "")
        data[name] = value
    data["comment_text"] = text
    r2 = client.post(action, data=data)
    if r2.status_code == 200:
        if text in r2.text:
            return True, "posted"
        return True, "posted_but_not_verified"
    return False, f"status_{r2.status_code}"

def engage_group(client, group_id, comments, reactions, settings, logger):
    ok, status, posts = fetch_group_posts(client, group_id, limit=settings.get("max_posts", 5))
    if not ok:
        logger.error(f"[Group {group_id}] fetch failed: {status}")
        return
    logger.info(f"[Group {group_id}] Found {len(posts)} posts")

    for idx, p in enumerate(posts, start=1):
        post_id = p.get("post_id")
        post_url = p.get("post_url")
        logger.info(f"[{idx}/{len(posts)}] Processing post {post_id} - {post_url}")

        # React
        if reactions:
            chosen = random.choice(reactions)
            try:
                r_ok, r_info = react_post_simple(client, post_id, reaction_preference=chosen)
                if r_ok:
                    logger.info(f"Reacted ({chosen}) on post {post_id} -> {r_info}")
                else:
                    logger.warning(f"React failed on post {post_id} -> {r_info}")
            except Exception as e:
                logger.exception(f"Exception reacting on post {post_id}: {e}")

            wait = settings.get("reaction_delay", 5)
            logger.info(f"Waiting {wait}s before next action...")
            time.sleep(wait)

        # Comment
        if comments:
            chosen_c = random.choice(comments)
            try:
                c_ok, c_info = comment_on_post(client, post_id, chosen_c)
                if c_ok:
                    logger.info(f"Commented on post {post_id}: {chosen_c} -> {c_info}")
                else:
                    logger.warning(f"Comment failed on post {post_id}: {c_info}")
            except Exception as e:
                logger.exception(f"Exception commenting on post {post_id}: {e}")

            wait = settings.get("comment_delay", 8)
            logger.info(f"Waiting {wait}s before next post...")
            time.sleep(wait)

    logger.info(f"[Group {group_id}] Done engaging {len(posts)} posts")