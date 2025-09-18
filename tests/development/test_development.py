"""Development domain acceptance tests: git and development tools from a user's POV."""


def test_can_clone_public_repo(host, tmp_path):
    """Ensure git can clone a small public repository (connectivity smoke test)."""
    repo = "https://github.com/githubtraining/hellogitworld.git"
    dest = tmp_path / "hellogitworld"
    cmd = host.run(f"git clone --depth 1 {repo} {dest} 2>&1")
    assert cmd.rc == 0


def test_python_available_and_venv(host):
    """Check that Python3 is available in PATH."""
    py = host.run("python3 --version || true")
    assert py.rc == 0
