FROM python:3.7-alpine

LABEL "com.github.actions.name"="NIXPy Codestyle 3.7"
LABEL "com.github.actions.description"="Check NIXPy source with pycodestyle (Python 3.7)"
LABEL "com.github.actions.color"="purple"

LABEL "repository"="http://github.com/G-Node/nixpy"
LABEL "maintainer"="Achilleas Koutsou"

RUN pip install --upgrade pip
RUN pip install pycodestyle

COPY . /nixpy

ENTRYPOINT ["pycodestyle", "/nixpy/nixio"]
