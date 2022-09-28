# ubuntu-config

My own Ubuntu setup &amp; config

## Execute installation

```sh
bash <(wget -qO- https://raw.githubusercontent.com/neilime/ubuntu-config/main/install.sh)
```

## Development

### Setup

`UBUNTU_VERSION` is the version of Ubuntu to use during the development. Example: `latest`, `18.04`, `20.04`. (See [https://hub.docker.com/\_/ubuntu/?tab=tags](https://hub.docker.com/_/ubuntu/?tab=tags))

```sh
make build-image UBUNTU_VERSION
```

### Running tests

```sh
make test UBUNTU_VERSION
```
