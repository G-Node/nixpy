workflow "Python 3.7 pycodestyle" {
  on = "push"
  resolves = ["run-pycodestyle37"]
}

action "build-pycodestyle37" {
  uses = "actions/docker/cli@master"
  args = ["build", "-t", "pycodestyle37", "-f", ".github/action-codestyle37/Dockerfile", "."]
}

action "run-pycodestyle37" {
    needs = "build-pycodestyle37"
    uses = "actions/docker/cli@master"
    args = ["run", "pycodestyle37"]
}
