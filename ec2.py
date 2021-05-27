#!/bin/python3.7

import boto3
import sys
from prettytable import PrettyTable


## Default Values
account = ""
ubuntu16 = "ami-048bb32b1fb7c36b7"
ubuntu20 = "ami-0cda377a1b884a1bc"
rhel8 = "ami-052c08d70def0ac62"
amazon = "ami-0e306788ff2473ccb"
default_image = ubuntu20
default_count = 1
default_keyname = 'devops'
default_sec_group = 'personal'
default_type = 't2.micro'
default_status = ''
default_tag = 'Nodes'
instancename = ''

def change_tags():
    user_choice = input("Do you want to change tags [Y/N]: ")
    if user_choice.upper() == 'Y':
        total_tags = []
        total_tags.append(input("Enter tags: "))
    elif user_choice.upper() == 'N':
        print("Ok it's fine")
    else:
        print("Invalid Choice")


## Fetch Arguements
def fetch_args():
    global instancename, default_image, default_count, default_keyname, default_sec_group, default_type, default_status, account, ec2
    all_args = sys.argv
    try:
        default_status = all_args.pop(1)
    except:
        print("Please provide Valid Input:\nExample:\n[Create | Stop | Status | Terminate]")
        exit(1)
    else:
        for i in all_args:
            if i == 'CT':
                account = "CT"
            elif 'allport' in i.lower():
                default_sec_group = 'all expose'
            elif 'ubuntu16' in i.lower():
                default_image = ubuntu16
            elif 'rhel' in i.lower():
                default_image = rhel8
            elif 'amazon' in i.lower():
                default_image = amazon
            elif i.isdigit():
                default_count = int(i)
            elif 'type=' in i.lower():
                default_type = i.split("=")[-1]
            elif 'name=' in i.lower():
                instancename= i.split("=")[-1]

        if account == "CT":
            session = boto3.Session(profile_name='CT')
            ec2 = session.resource('ec2')
        else:
            ec2 = boto3.resource("ec2")


## Create ec2 instance
def create_instance():
    instances = ec2.create_instances(
        ImageId=default_image,
        MinCount=default_count,
        MaxCount=default_count,
        InstanceType=default_type,
        KeyName=default_keyname,
        SecurityGroupIds=[default_sec_group,],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags':[
                    {
                        'Key': 'Name',
                        'Value': default_tag
                    },]},]
        )

def stop_instance():
    if instancename != '':
        for i in ec2.instances.all():
            try:
                if i.tags[0]["Value"].lower() == instancename.lower():
                    ec2.Instance(i.id).stop()
                    print(f'{i.id} {i.tags[0]["Value"]} Stop SuccessFully')
                    break
            except:
                pass

    else:
        for i in ec2.instances.all():
            try:
                if i.state["Name"] == 'running':
                    ec2.Instance(i.id).stop()
                    print(f'{i.id} {i.tags[0]["Value"]} Stop SuccessFully')
            except:
                pass

def start_instance():
    if instancename != '':
        for i in ec2.instances.all():
            try:
                if i.tags[0]["Value"].lower() == instancename.lower():
                    ec2.Instance(i.id).start()
                    print(f'{i.id} {i.tags[0]["Value"]} Start SuccessFully')
                    break
            except:
                print('Instance Without Tag Found', i.id)
    else:
        for i in ec2.instances.all():
            try:
                if i.state["Name"] == 'stopped':
                    ec2.Instance(i.id).start()
                    print(f'{i.id} {i.tags[0]["Value"]} Start SuccessFully')
            except:
                print('Instance Without Tag Found', i.id)
            

# create table for print
def tableprint(field_names, rows):
    table = PrettyTable()
    table.field_names = field_names
    table.align[field_names[0]] = 'l'
    for row in rows:
        table.add_row(row)
    print(table)


# status of instance
def status_instance():
    temp = []
    fields = ("Name", "Status", "Type", "Public IP", "Private IP", "Image")
    for instance in ec2.instances.all():
        try:
            temp.append((instance.tags[0]["Value"], 
                         instance.state["Name"], 
                         instance.instance_type, 
                         instance.public_ip_address,
                         instance.private_ip_address,
                         instance.image.description[:30]))
        except:
            print('Instance Without Tag Found', instance.id)
    tableprint(fields, temp)


# terminate instance
def terminate_instance():
    for i in ec2.instances.all():
        if i.state['Name'] in ('running', 'stopped'):
            ec2.Instance(i.id).terminate()
            print(f'{i.id} Terminate SuccessFully')




if __name__ == "__main__":
    fetch_args()
    if default_status.lower() == 'create':
        create_instance()
    elif default_status.lower() == 'status':
        status_instance()
    elif default_status.lower() == 'terminate':
        terminate_instance()
    elif default_status.lower() == 'stop':
        stop_instance()
    elif default_status.lower() == 'start':
        start_instance()
    else:
        print("Please provide Valid Input:\nExample:\n[Create | Start | Stop | Status | Terminate]")
