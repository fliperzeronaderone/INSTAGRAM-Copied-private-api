import hashlib
import hmac
import json
import time
import uuid
import requests
# Discord @9li2  PRIVATE APIS FOR S3LL
# --- Constants extracted from ig api  internals ---
IG_SIG_KEY = b"[INSTAGRAM_SIG_KEY_HERE]"
IG_APP_ID = "936619743392459"
IG_MODEL = "FLIPERZEROONE" # CORRECT
IG_ANDROID_VERSION = "No-One"
IG_VERSION_CODE = "200.0.0.27.121"
SIG_VERSION = "4"
USER_AGENT = f"Instagram {IG_VERSION_CODE} Android ({IG_ANDROID_VERSION}/29; 420dpi; 1080x1920; samsung; {IG_MODEL}; {IG_MODEL}; exynos9810; en_US)"

class FLIPERZEROONE :
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "X-IG-App-ID": IG_APP_ID,
            "Accept": "*/*",
        })
        self.uuid = str(uuid.uuid4())
        self.phone_id = str(uuid.uuid4())
        self.advertising_id = str(uuid.uuid4())
        self.device_id = f"android-{uuid.uuid4().hex[:16]}"
        self.csrf_token = None
        self.sessionid = None

    def _signature(self, data: dict) -> str:
        body = json.dumps(data, separators=(',', ':'))
        hash_sig = hmac.new(IG_SIG_KEY, body.encode('utf-8'), hashlib.sha256).hexdigest()
        return f"{hash_sig}.{body}"

    def _post(self, endpoint: str, data: dict) -> dict:
        url = f"https://i.instagram.com/api/{endpoint}"
        signed_body = self._signature(data)
        payload = {
            "signed_body": signed_body,
            "ig_sig_key_version": SIG_VERSION
        }
        resp = self.session.post(url, data=payload)
        resp.raise_for_status()
        return resp.json()

    def login(self, username: str, password: str):
        data = {
            "username": username,
            "password": password,
            "device_id": self.device_id,
            "uuid": self.uuid,
            "phone_id": self.phone_id,
            "adid": self.advertising_id,
            "login_attempt_count": "0"
        }
        result = self._post("v1/accounts/login/", data)
        if 'logged_in_user' in result:
            self.sessionid = self.session.cookies.get_dict().get('sessionid')
            self.csrf_token = self.session.cookies.get_dict().get('csrftoken')
            print("[+] Login successful")
        else:
            print("[!] Login failed:", result)
        return result

    def user_info(self, user_id: int):
        resp = self.session.get(
            f"https://i.instagram.com/api/v1/users/{user_id}/info/"
        )
        resp.raise_for_status()
        return resp.json()

    def follow(self, user_id: int):
        return self._post(f"v1/friendships/create/{user_id}/", {})

    def unfollow(self, user_id: int):
        return self._post(f"v1/friendships/destroy/{user_id}/", {})

    def like(self, media_id: str):
        return self._post(f"v1/media/{media_id}/like/", {})

    def comment(self, media_id: str, text: str):
        data = {"comment_text": text}
        return self._post(f"v1/media/{media_id}/comment/", data)

    def upload_photo(self, photo_path: str, caption: str = ""):
        
        raise NotImplementedError("Photo upload requires multipart logic")

    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="FL_Py", description="FLIPERZEROONE  Instagram Private API Client")
    parser.add_argument("action", choices=["login","userinfo","follow","unfollow","like","comment"], help="Action to perform")
    parser.add_argument("--username", help="Instagram username")
    parser.add_argument("--password", help="Instagram password")
    parser.add_argument("--user_id", type=int, help="Target user ID")
    parser.add_argument("--media_id", help="Target media ID")
    parser.add_argument("--text", help="Comment text")
    args = parser.parse_args()

    client = FLIPERZEROONE ()
    if args.action == "login":
        assert args.username and args.password
        client.login(args.username, args.password)
    elif args.action == "userinfo":
        assert args.user_id
        print(client.user_info(args.user_id))
    elif args.action == "follow":
        assert args.user_id
        print(client.follow(args.user_id))
    elif args.action == "unfollow":
        assert args.user_id
        print(client.unfollow(args.user_id))
    elif args.action == "like":
        assert args.media_id
        print(client.like(args.media_id))
    elif args.action == "comment":
        assert args.media_id and args.text
        print(client.comment(args.media_id, args.text))
    else:
        parser.print_help()
