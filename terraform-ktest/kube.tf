# make IAM ROLE for kube 
resource "aws_iam_role" "kube" {
    name = "kube@${var.myVPC["region"]}.${var.myVPC["env"]}"
    assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
resource "aws_iam_instance_profile" "kube" {
  name = "${aws_iam_role.kube.name}"
  role = "${aws_iam_role.kube.name}"
}


# make SG for kube 
resource "aws_security_group" "kube" {
    name        = "kube@${var.myVPC["region"]}.${var.myVPC["env"]}"
    description = "kubernetes talk to itself"
    vpc_id      = "${module.vpc.vpc_id}"
      ingress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        self = true 
      }
}


# kube master launch 
resource "aws_instance" "kube-masterA" {
# TODO: look up this AMI dynamically by tag
    ami                     = "ami-61921205"
    instance_type           = "t2.medium"
    iam_instance_profile    = "${aws_iam_role.kube.name}"
    vpc_security_group_ids  = [ "${aws_security_group.managed-ops.id}" ]
    subnet_id               = "${module.vpc.public_subnets[0]}"
    root_block_device       = {
                                volume_size = "8"
                                volume_type = "gp2"
                              }
    tags {
        Name = "bastion@${var.myVPC["region"]}.${var.myVPC["env"]}"
        role = "bastion"
        env  = "${var.myVPC["env"]}"
    }
}


#assign the EIP
data "aws_eip" "bastion_eip" {
  public_ip = "${var.myVPC["bastion_eip"]}"
}
resource "aws_eip_association" "bastion_eip_assoc" {
  instance_id   = "${aws_instance.bastion.id}"
  allocation_id = "${data.aws_eip.bastion_eip.id}"
}
