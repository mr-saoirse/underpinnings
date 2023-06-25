import re


def split_string_with_quotes(string):
    pattern = r'"([^"]*)"'
    quoted_substrings = re.findall(pattern, string)
    placeholder = "<<<<  >>>>"
    modified_string = re.sub(pattern, placeholder, string)
    split_parts = modified_string.split()
    result = []
    for part in split_parts:
        if placeholder in part:
            # Replace the placeholder with the quoted substring
            part = part.replace(placeholder, quoted_substrings.pop(0))
        result.append(part)

    return result


def generate_markdown_table(data, title=None):
    if not data:
        return ""

    headers = list(data[0].keys())
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for row in data:
        table += (
            "| " + " | ".join(str(row.get(header, "")) for header in headers) + " |\n"
        )
    return f"""  ### {title}\n{table} """


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
