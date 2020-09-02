import boto3
import botocore
import click


def filter_instances(project, instance=None):
    """Return filtered list of instances if argument is passed"""
    instances = []
    filters = []

    if project:
        filters.append({'Name':'tag:Project', 'Values':[project]})
    if instance:
        filters.append({'Name':'instance-id', 'Values':[instance]})

    if project or instance:
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances


def has_pending_snapshot(volume):
    """Check if any pending snapshots for given volume"""
    snapshots = list(volume.snapshots.all())

    return snapshots and snapshots[0].state == 'pending'


# CLI GROUP (MAIN)
@click.group()
@click.option('--profile', default=None, help="AWS user")
def cli(profile):
    """snapshotalyzer manages snapshots"""
    global session, ec2

    session = boto3.Session(profile_name=profile)
    ec2 = session.resource('ec2')


# SNAPSHOTS GROUP
@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
    help='List all snapshots for each volume, not just the most recent')
@click.option('--instance', default=None,
    help='If set apply command only for specified instance')
def list_snapshots(project, list_all, instance):
    """List EC2 snapshots"""

    instances = filter_instances(project, instance)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

                if s.state == 'completed' and not list_all: break
    return


# VOLUMES GROUP
@cli.group('volumes')
def volumes():
    """Commands for volumes"""

# list command
@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
@click.option('--instance', default=None,
    help='If set apply command only for specified instance')
def list_volumes(project, instance):
    """List EC2 volumes"""

    instances = filter_instances(project, instance)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted")))
    return


# INCSTANCES GROUP
@cli.group('instances')
def instances():
    """Commands for inctances"""

# instances - snapshot
@instances.command('snapshot', help='Create snapshots of all volumes')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--force', 'force_snapshot', default=False, is_flag=True,
    help="If '--project' isn't set, exit the command immediately with an error message, unless '--force' is set" )
@click.option('--instance', default=None,
    help='If set apply command only for specified instance')
def create_snapshots(project, force_snapshot, instance):
    """Create snapshots for EC2 instances"""

    if not project and not force_snapshot:
        print('"--force" option is required if the project is not specified!')
        exit()

    instances = filter_instances(project, instance)

    for i in instances:
        flag = None
        if i.state['Name'] == 'running': flag = True

        print("Stopping {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print("Skipping {0}, snapshot already in progress".format(v.id))
                continue

            print("Creating snapshot of {0}".format(v.id))
            try:
                v.create_snapshot(Description='Created by snapshotalyzer')
            except botocore.exceptions.ClientError as e:
                print(f"Could not create a snapshot for instance {i.id} volume {v.id}. {str(e)}")
                continue
        if flag:
            print("Starting {0}...".format(i.id))
            i.start()
            i.wait_until_running()

    print("Job's done!")

    return

# instances - list
@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    """List EC2 instances"""


    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']:t['Value'] for t in i.tags or []}
        print( ', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>'))))
    return

# instances - stop
@instances.command('stop')
@click.option('--project', default=None, help='Only instances for project')
@click.option('--force', 'force_stop', default=False, is_flag=True,
    help="If '--project' isn't set, exit the command immediately with \
        an error message, unless '--force' is set" )
@click.option('--instance', default=None,
    help='If set apply command only for specified instance')
def stop_instances(project, force_stop, instance):
    """Stop EC2 instances"""

    if not project and not force_stop:
        print('"--force" option is required if the project is not specified!')
        exit()

    instances = filter_instances(project, instance)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0}. ".format(i.id) + str(e))
            continue

    return

# instances - start
@instances.command('start')
@click.option('--project', default=None, help='Only instances for project')
@click.option('--force', 'force_start', default=False, is_flag=True,
    help="If '--project' isn't set, exit the command immediately \
        with an error message, unless '--force' is set" )
@click.option('--instance', default=None,
    help='If set apply command only for specified instance')
def start_instances(project, force_start, instance):
    """Start EC2 instances"""

    if not project and not force_start:
        print('"--force" option is required if the project is not specified!')
        exit()

    instances = filter_instances(project, instance)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0}. ".format(i.id) + str(e))
            continue

    return

# instances- reboot
@instances.command('reboot')
@click.option('--project', default=None, help='Only instances for project')
@click.option('--force', 'force_reboot', default=False, is_flag=True,
    help="If '--project' isn't set, exit the command immediately  \
        with an error message, unless '--force' is set" )
@click.option('--instance', default=None,
    help='If set apply command only for specified instance')
def reboot_instances(project, force_reboot, instance):
    """Reboot EC2 instances"""

    if not project and not force_reboot:
        print('"--force" option is required if the project is not specified!')
        exit()

    instances = filter_instances(project, instance)

    for i in instances:
        print("Rebooting {0}...".format(i.id))
        try:
            i.reboot()
        except botocore.exceptions.ClientError as e:
            print("Could not reboot {0}. ".format(i.id) + str(e))
            continue


if __name__ == '__main__':
    cli()
