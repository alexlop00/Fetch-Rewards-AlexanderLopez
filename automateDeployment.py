import boto3

client = boto3.client('cloudformation')

template = """---
Resources:
  ############################# VPC ###########################  
  VPC1: #Logical ID
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 192.168.2.0/24
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags: 
        - Key: "Name"
          Value: "Fetch Rewards VPC"
  ############################# Subnet ###########################
  Subnet1: #Logical ID
    Type: AWS::EC2::Subnet
    Properties:
      AvailabilityZone: us-east-2a #Adjust Value
      CidrBlock: 192.168.2.0/26
      Tags:
        - Key: "Name"
          Value: "Fetch Rewards Subnet"
      VpcId: 
        Ref: VPC1 #References the VPC resource by logical ID
  ########################### Internet Gateway #######################
  InternetGateway1: #Logical ID
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: "Name"
          Value: "Fetch Rewards InternetGateway"
  ########################### Attach Internet Gateway to VPC ############
  AttachInternetGateway1: #Logical ID
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      InternetGatewayId:
        Ref: InternetGateway1 #References InternetGateway
      VpcId: 
        Ref: VPC1 #References VPC
  ######################### Create Route Table #######################        
  RouteTable1: #Logical ID
    Type: AWS::EC2::RouteTable
    Properties:
      Tags:
        - Key: "Name"
          Value: "Fetch Rewards RouteTable"
      VpcId:
        Ref: VPC1 #References VPC by logical ID
  ####################### Create Route ##############################
  RouteToAllowTraffic1: #Logical ID
    Type: AWS::EC2::Route
    Properties:
      RouteTableId:
        Ref: RouteTable1 #References RouteTable1 by logical ID
      GatewayId:
        Ref: InternetGateway1
      DestinationCidrBlock: "0.0.0.0/0" #WARNING
  ####################### Associate Route Table to Subnet ##############
  AssociateRouteTabletoSubnet1: #Logical ID
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId:
        Ref: RouteTable1 #References Route Table
      SubnetId:
        Ref: Subnet1 #References SubnetId
  ##################### Create Network ACL #############################
  NetworkACL1: #Logical ID
    Type: AWS::EC2::NetworkAcl
    Properties:
      Tags:
        - Key: "Name"
          Value: "Fetch Rewards ACL"
      VpcId:
        Ref: VPC1
  ##################### Create Network ACL Entry 1########################
  NetworkACLEntry1: #Logical ID
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId: 
        Ref: NetworkACL1
      RuleNumber: 1
      Protocol: 6 #TCP
      RuleAction: allow
      CidrBlock: "0.0.0.0/0" #WARNING
      PortRange:
        From: 22 
        To: 22
  ###################### Create Network ACL Entry 2 ########################
  NetworkACLEntry2: #Logical ID
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId:
        Ref: NetworkACL1
      Egress: true
      RuleNumber: 1
      Protocol: -1 #Refers to All
      RuleAction: allow
      CidrBlock: "0.0.0.0/0" #WARNING
  ###################### Associate Subnet to Network ACL####################
  AssociateSubnetToNetworkACL1: #Logical ID
    Type: AWS::EC2::SubnetNetworkAclAssociation
    Properties:
      NetworkAclId:
        Ref: NetworkACL1
      SubnetId:
        Ref: Subnet1
  ######################## Create Security Group ###########################
  SecurityGroup1: #Logical ID
    Type: AWS::EC2::SecurityGroup
    Properties:
      VpcId: 
        Ref: VPC1 
      GroupDescription: "Enable SSH Access"
      GroupName: "Open SSH Access"
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: "0.0.0.0/0" #WARNING
  ######################## Create EC2 Instance #############################
  EC2Instance1: #Logical ID
    Type: AWS::EC2::Instance
    Properties:
      AvailabilityZone: us-east-2a #Adjust Value
      SubnetId:
        Ref: Subnet1 
      Tags:
        - Key: "Name"
          Value: "Fetch Rewards Server"
      InstanceType: t2.micro
      ImageId: ami-07a0844029df33d7d 
      SecurityGroupIds:
        [Ref: SecurityGroup1]
      BlockDeviceMappings:
        - DeviceName: "/dev/xvda"
          Ebs:
            VolumeSize: "10"
        - DeviceName: "/dev/xvdf"
          Ebs:
            VolumeSize: "100"
      UserData:
        Fn::Base64:
           !Sub | 
              #!/bin/bash
              cd ~/.ssh/
              ssh-keygen -f users-key
              cd /etc/skel
              mkdir .ssh
              cd .ssh
              cp ~/.ssh/users-key.pub authorized_keys
              adduser user1
              adduser user2
              sudo mkfs /dev/xvdf -t xfs
              sudo mkdir /data
              sudo mount /dev/xvdf /data
              sudo mkfs /dev/xvda -t ext4
              sudo mount /dev/xvda /
  ####################### Associate Public IP Address to EC2 Instance#####
  PublicIPAddress1: #LogicalID
    Type: AWS::EC2::EIP
    Properties:
      Domain: vpc 
      InstanceId: 
        Ref: EC2Instance1 #Associate Elastic IP to EC2
"""

response = client.create_stack(
    StackName='FetchRewardsStack',
    TemplateBody=template,
    DisableRollback=True,
    RoleARN='',#Adjust Value
    )

