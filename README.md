# aws_snapshotalyzer

Demo project to manage AWS EC2 instance snapshot

##

This project is a demo, and uses boto3 to manage AWS EC2 instance snapshots.

## Configuring

snapshotalyzer uses the configuration file created by the AWS cli. e.g.

'aws configure --profile snapshotalyzer'

## Running

'pipenv run python snapshotalyzer\snapshotalyzer.py <command> <subcommand> <--project=PROJECT>'

*command*: instances, volumes, snapshots
*subcommand*: depends on command
*project* is optional
