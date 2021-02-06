import hashlib
import re
import sys
import urllib

if int(sys.version[0]) > 2:
    import urllib.parse


def get_gravatar_url(email, size=30):
    default = "identicon"

    if int(sys.version[0]) > 2:
        url = "https://www.gravatar.com/avatar/" + hashlib.md5(email.lower().encode('utf-8')).hexdigest() + "?"
        url += urllib.parse.urlencode({'d':default, 's':str(size)})
    else:
        url = "https://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        url += urllib.urlencode({'d':default, 's':str(size)})

    return url


def get_gravatars(developers, size=40):
    EMAIL_RE = re.compile(r".*<(.*)>$")

    gravatars = {}
    for developer in developers:
        match = EMAIL_RE.match(developer.name)
        if match:
            email = match.group(1)
            gravatars[developer] = get_gravatar_url(email, size=size)
        else:
            gravatars[developer] = None

    return gravatars
