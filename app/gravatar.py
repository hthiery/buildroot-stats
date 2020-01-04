import re
import urllib, hashlib
import urllib.parse


def get_gravatar_link(developer, size=30):
    EMAIL_RE = re.compile(r".*<(.*)>$")
    default = "identicon"

    match = EMAIL_RE.match(developer)
    if match:
        email = match.group(1)

    url = "https://www.gravatar.com/avatar/" + hashlib.md5(email.lower().encode('utf-8')).hexdigest() + "?"
    url += urllib.parse.urlencode({'d':default, 's':str(size)})
    return url


def get_gravatars(developers, size=40):
    gravatars = {}
    for developer in developers:
        gravatars[developer] = get_gravatar_link(developer, size=size)
    return gravatars
