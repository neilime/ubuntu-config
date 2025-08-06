# ubuntu-config

My own Ubuntu setup & config. This project uses Ansible to set up and configure a
personal computer running on Ubuntu.

## Prerequisites

- Ubuntu machine for the setup

## Execute installation

```sh
wget -qO- \
"https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh" | sh
```

## Project Structure

The project has the following structure:

```txt
ubuntu-config
├── .github
│   └── workflows: GitHub Actions workflows for CI
├── docker: Dockerfiles to build dev/ci images
├── ansible: Ansible roles and playbooks
├── tests: TestInfra test suite for validation
└── README.md
```

## GPG Key Setup

This project can automatically import your GPG keys from Bitwarden during setup. The GPG keys must be stored in Bitwarden with specific field names to be recognized by the import process.

### Exporting GPG Keys for Import

To export your existing GPG keys in the correct format for this setup:

1. **Export the public key:**

```bash
gpg --export --armor your@email.com > your_email_public.asc
```

2. **Export the private key:**

```bash
gpg --export-secret-keys --armor your@email.com > your_email_private.asc
```

3. **Export the sub-private keys (if your key has subkeys):**

```bash
gpg --export-secret-subkeys --armor your@email.com > your_email_subkeys.asc
```

4. **Export the ownertrust (recommended for preserving trust relationships):**

```bash
gpg --export-ownertrust > your_email_ownertrust.txt
```

### Storing GPG Keys in Bitwarden

For each GPG key you want to import, create a new item in your Bitwarden vault with the following structure:

1. **Item Name:** Use the email address or identifier associated with the GPG key (e.g., `your@email.com`)

2. **Custom Fields:** Add the following custom fields with the content from the exported files:

- `public_key`: Content of the `.asc` file from step 1 (Required if private_key is not provided)
- `private_key`: Content of the `.asc` file from step 2 (Required if public_key is not provided)
- `sub_private_key`: Content of the `.asc` file from step 3 (Optional - only if your key has subkeys)
- `ownertrust`: Content of the `.txt` file from step 4 (Optional but recommended)

3. **Collection:** Make sure the item is in the collection specified by your `setup_keys_bitwarden_gpg_keys_collection_id` variable.

### Key Requirements

- At least one of `public_key` or `private_key` must be provided
- The `name` field should match the email or identifier you want to use for the key
- All fields should contain the complete ASCII-armored content, including the `-----BEGIN PGP...-----` and `-----END PGP...-----` lines
- Sub-private keys and ownertrust are optional but recommended for complete key functionality

### Supported Key Types

This setup supports all standard GPG key types:

- RSA keys (any size)
- DSA keys
- ECDSA keys
- EdDSA keys
- Keys with or without subkeys
- Keys with or without passphrases (passphrases are preserved)

### Key Renewal and Updates

The import process is idempotent and supports key renewal:

- If a key already exists, it will be updated with any new information
- Trust settings will be preserved or updated as needed
- The process can handle both new key imports and key renewals

### Troubleshooting

If GPG key import fails:

1. **Verify the key format:** Ensure the exported keys are in ASCII-armored format (contain `-----BEGIN PGP` headers)
2. **Check field names:** Ensure Bitwarden custom fields use exactly the names specified above
3. **Validate key content:** Test importing the keys manually with `gpg --import keyfile.asc`
4. **Review collection access:** Ensure the Bitwarden item is in the correct collection

Example manual test:

```bash
# Test if your exported key is valid
gpg --import your_email_private.asc
gpg --list-keys your@email.com
```

## Development

1. Clone the repository:

```bash
git clone https://github.com/neilime/ubuntu-config.git
cd ubuntu-config
```

1. Setup the development stack:

```bash
make setup
```

1. Test the install script:

```bash
# On docker container
make test-docker

# Pass env variables to the script
make test-docker -- \
"--env SKIP_INSTALL_REQUIREMENTS=true --env SETUP_TAGS=keys --env SKIP_CLEANUP=true"

# On virtual machine
make test-vm
```

## Continuous Integration

This project uses GitHub Actions to test the Ansible playbook with TestInfra using
a dedicated test service architecture. The workflows are defined in
`.github/workflows/`.

### Test Workflows

- `__tests-docker.yml` - Tests the setup in Docker containers using the test
  service
- `__tests-vm.yml` - Tests the setup in virtual machines using the test service
- `__shared-ci.yml` - Shared CI workflow that builds test images and orchestrates
  tests
- `main-ci.yml` - Main CI workflow that triggers all tests

The TestInfra test suite runs in a dedicated Docker service and provides
comprehensive validation of:

- Package installation and configuration
- Service status and functionality
- File permissions and configurations
- User environment setup
- Development tool installations

Tests are triggered on every push to the repository and provide detailed reports
on the system configuration status.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
