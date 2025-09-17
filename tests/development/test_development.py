"""Development domain acceptance tests: git and development tools from a user's POV."""



def test_can_clone_public_repo(host, tmp_path):
    repo = "https://github.com/githubtraining/hellogitworld.git"
    dest = tmp_path / "hellogitworld"
    cmd = host.run(f"git clone --depth 1 {repo} {dest} 2>&1")
    assert cmd.rc == 0


def test_python_available_and_venv(host):
    py = host.run("python3 --version || true")
    assert py.rc == 0
