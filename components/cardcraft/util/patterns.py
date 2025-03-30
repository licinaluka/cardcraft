#!/usr/bin/python3
from semver import Version

capped = Version.parse("v0.107.0".lstrip("v"))  # comes from ENV var or is hardcoded


def version(doc):
    since = next(filter(lambda e: e.lstrip().startswith("@since"), doc.split("\n")))
    if since is None:
        return Version.parse("0")

    return Version.parse(since.split(" ")[-1].lstrip("v"))


def some_new_func():
    """?

    @since v0.107.1
    """
    if capped < version(some_new_func.__doc__):
        raise NotImplementedError("Attempt to run disabled code!")

    print("ran code!")


some_new_func()
