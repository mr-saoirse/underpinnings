def docker_default(template, path, entry_point=""):
    """
    We are generating a docker file and its important to know the context in which it will be run to determine paths etc.
    Best practice is t run context from the repo base and then use absolute paths here

    We do not generate docker files in the general case, this is just a special helper to allow for containerless apps in the monorepo
    We may also be able to touch up apps that are managed in this way of the base container changes
    """
    # requirements may exist
    requirements = ""
    requirements = """
COPY ./requirements.txt /app/
RUN pip install -U pip && pip install --no-cache-dir -r /app/requirements.txt 
"""

    DOCKERFILE = f"""
FROM {template.image}

#setup the base
RUN apt update && apt install -y git gh;

#app
COPY {path} /app 
#install some requirements
WORKDIR /app
{requirements}

#ready
ENV PYTHONPATH "${{PYTHONPATH}}:/app"
ENV PYTHONUNBUFFERED=0
{entry_point}
    """

    return DOCKERFILE
