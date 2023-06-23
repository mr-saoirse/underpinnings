import re


def is_valid_kubernetes_resource_name(s):
    valid_job_key = r"[a-z0-9]([-a-z0-9]*[a-z0-9])?"
    return re.compile(valid_job_key).fullmatch(s)


def coerce_kubernetes_name(name):
    # Remove leading and trailing whitespaces
    name = name.strip()
    name = re.sub(r"[^a-zA-Z0-9.-]", "-", name)
    # Remove consecutive dashes
    name = re.sub(r"-+", "-", name)
    # Remove leading dashes
    name = re.sub(r"^-", "", name)
    # Remove trailing dashes
    name = re.sub(r"-$", "", name)
    # Ensure the name is not empty
    if not name:
        raise ValueError("Invalid name after coercion")
    return name
