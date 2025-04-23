# OPNSense+Kubernetes Firewall Integration

A simple script, primarily designed for use with [Agones](https://agones.dev/) game servers, to handle automatically configuring the OPNSense firewall as game server instances are started and stopped.

Currently, OPNSense's firewall API is very poor and unfinished, so this script only attempts to configure aliases at the moment. The firewall rules and port forwards that point to these aliases still need to be added by hand.

## Configuration

A [sample config file](config.sample.json) is provided with sample configurations for running in a Kubernetes cluster.

Additionally, a [development sample config file](config.sample.dev.json) is provided with extra options intended for use during local development and testing.

## Runtime Options

Environment variables:

| ENV | Description |
| -- | -- |
| CONFIG_PATH | Path to the config file |
| API_KEY | OPNSense API key |
| API_SECRET | OPNSense API secret |

Command-line flags:

| Long Form | Short Form | Description |
| -- | -- | -- |
| --dryrun | -d | Outputs the computed firewall settings without actually updating OPNSense |
| --verbose | -v | Outputs extra details while running |
| --config | -c | Path to the config file |
