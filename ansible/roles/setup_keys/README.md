# Setup Keys

This role sets up SSH and GPG keys for the user by importing them from Bitwarden. It ensures that the keys are properly configured and available for use.

## Role Variables

See [./vars/main.yml](./vars/main.yml) for a complete list of role variables.

## GPG Key Setup

This project can automatically import your GPG keys from Bitwarden during setup. The GPG keys must be stored in Bitwarden with specific field names to be recognized by the import process.

### Creating GPG Keys

If you don't have GPG keys yet, you can create them using the following command:

```bash
gpg --full-generate-key
```

Follow the prompts to create your key pair.

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

- `public_key`: Content of the `your_email_public.asc` file from step 1 (Required if private_key is not provided)
- `private_key`: Content of the `your_email_private.asc` file from step 2 (Required if public_key is not provided)
- `sub_private_key`: Content of the `your_email_subkeys.asc` file from step 3 (Optional - only if your key has subkeys)
- `ownertrust`: Content of the `your_email_ownertrust.txt` file from step 4 (Optional but recommended)

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
