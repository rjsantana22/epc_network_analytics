# Terraform

Execute the services that you define in main.tf

```Shell

terraform init

terraform plan

terraform apply

terraform destroy

```

alias terra-init='terraform -chdir=/home/rsantana/one_project/terraform-env/ init'
alias terra-plan='terraform -chdir=/home/rsantana/one_project/terraform-env/ plan'
alias terra-apply='terraform -chdir=/home/rsantana/one_project/terraform-env/ apply'
alias terra-destroy='terraform -chdir=/home/rsantana/one_project/terraform-env/ destroy'