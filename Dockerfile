FROM python:3.10

#setup the base
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg;
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null;
RUN apt update && apt install -y git gh;

#add kubectl / kustomize

#nstall some requirements
WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install -U pip && pip install --no-cache-dir -r /app/requirements.txt 

#ready
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV PYTHONUNBUFFERED=0