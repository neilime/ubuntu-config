# ubuntu-config

My own Ubuntu setup &amp; config. This project uses Ansible to set up and configure a personal computer running on Ubuntu.

## Prerequisites

- Ubuntu machine for the setup

## Execute installation

```sh
wget -qO- "https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh" | sh
```

## Project Structure

The project has the following structure:

```txt
ubuntu-config
├── .github
│   └── workflows: GitHub Actions workflows for CI
├── docker: Dockerfiles to build dev/ci images
├── ansible: Ansible roles and playbooks
└── README.md
```

## Development

1. Clone the repository:

```bash
git clone https://github.com/neilime/ubuntu-config.git
cd ubuntu-config
```

2. Setup the development stack:

```bash
make setup
```

3. Run the Ansible playbook:

```bash
make test
```

This will run the setup role on your Ubuntu machine.

## Continuous Integration

This project uses GitHub Actions to test the Ansible playbook. The workflow is defined in `.github/workflows/main-ci.yml`. It checks out the code and runs the Ansible playbook on a Ubuntu machine.

The workflow is triggered on every push to the repository.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
