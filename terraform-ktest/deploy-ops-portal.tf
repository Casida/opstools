#test ansible-core by deploying ops-portal


variable "myENV" {
    default {
        ansible_core = "~/git/ansible-engineering-cloud/ansible-core"
    }
}


module "deploy-ops-portal" {
  source  = "terraform-shell-resource"
  command = "cd ${var.myENV["ansible_core"]}; ./aw deploy-ops-portal.yml"
}
output "deploy-ops-portal" {
  value = "${module.deploy-ops-portal.stdout}"
}
