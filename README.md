# aws_snapshotalyzer

Demo project to manage AWS EC2 instance snapshot

##

This project is a demo, and uses boto3 to manage AWS EC2 instance snapshots.

## Configuring

snapshotalyzer uses the configuration file created by the AWS clie. e.g.

'aws configure --profile snapshotalyzer'

## Running

'pipenv run python snapshotalyzer\snapshotalyzer.py <command> <--project=PROJECT>'

*command*: list, start, stop
*project* is optional
