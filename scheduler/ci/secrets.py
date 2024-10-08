"""
Automatic `pip.conf` file generation.

"""

import os
from pathlib import Path


def main():
    prot = os.getenv("PIP_PROTOCOL")
    repo = os.getenv("PIP_REPOSITORY")
    user = os.getenv("PIP_USERNAME")
    passw = os.getenv("PIP_PASSWORD")
    configpath = os.path.expanduser("~/.config/pip")
    print(os.getcwd())

    if prot is repo is user is passw is None:
        print("No secrets provided, doing nothing.")
    elif None in [prot, repo, user, passw]:
        raise Exception("PIP environment variables incomplete.")
    else:
        if os.path.exists(f"{configpath}/pip.conf"):
            raise Exception(f"{configpath}/pip.conf exists, refusing to overwrite.")
        Path(configpath).mkdir(parents=True, exist_ok=True)
        with open(f"{configpath}/pip.conf", "w") as outfile:
            outfile.write(
                f"[global]\n"
                f"index = {prot}://{user}:{passw}@{repo}/pypi\n"
                f"index-url = {prot}://{user}:{passw}@{repo}/simple\n"
            )
            if prot == "http":
                outfile.write(f"trusted-host = {repo.split('/')[0]}")
        print("Created config ~/.config/pip/pip.conf")


if __name__ == "__main__":
    main()
