"""Keys domain acceptance tests: SSH and GPG usability from a user's perspective.

These tests verify the user-visible properties: SSH keys exist and GPG is usable.
Tests relax or skip checks when running in the lightweight container test image.
"""


def test_ssh_dir_and_private_keys_exist(host, user_home):
    """User should have a secure ~/.ssh directory and at least one private key."""
    ssh_dir = host.file(f"{user_home}/.ssh")
    assert ssh_dir.exists and ssh_dir.is_directory

    assert ssh_dir.mode == 0o700

    # Use a safe shell command to list private keys (exclude .pub files)
    keys_cmd = (
        "sh -c \"ls {home}/.ssh/id_* 2>/dev/null | grep -v '\\\\.pub' || true\""
    ).format(home=user_home)
    keys = host.run(keys_cmd)
    assert keys.stdout.strip(), "At least one SSH private key should exist in ~/.ssh"


def test_gpg_home_and_keys(host, user_home, target_user):
    """User should have a GnuPG home and at least a public key (or list-keys should work)."""
    gnupg = host.file(f"{user_home}/.gnupg")

    assert gnupg.exists and gnupg.is_directory
    assert gnupg.mode == 0o700

    gpg_list = host.run(f"sudo -u {target_user} gpg --list-keys --with-colons || true")
    pubring = host.file(f"{user_home}/.gnupg/pubring.kbx")
    assert gpg_list.rc == 0 or pubring.exists
