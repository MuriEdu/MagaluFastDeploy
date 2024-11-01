#!/usr/bin/python3
import shutil
import argparse
import os
import sys
import platform

MAIN_TF = """


terraform {
  required_providers {
    mgc = {
      source = "magalucloud/mgc"
    }
  }
}

provider "mgc" {
  alias  = "sudeste"
  region = "br-se1"
}

provider "mgc" {
  alias  = "nordeste"
  region = "br-ne1"
}

resource "mgc_virtual_machine_instances" "zapQuadrado" {
  provider = mgc
  name     = "html"
  machine_type = {
    name = "cloud-bs1.xsmall"
  }
  image = {
    name = "cloud-ubuntu-24.04 LTS"
  }

  network = {
    associate_public_ip = true # If true, will create a public IP
    delete_public_ip    = false
  }


  ssh_key_name = \""""
MAIN_TF_END = """"

  provisioner "file" {
    source      = "src"
    destination = "/tmp/src"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo mv /tmp/src /srv/src",

      "chmod +x /srv/src/install-docker.sh",
      "chmod +x /srv/src/run-docker.sh",
      "/srv/src/install-docker.sh",
      "/srv/src/run-docker.sh"
    ]
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/id_rsa")
    host = self.network.public_address
  }
}
"""

def check_config():
    mgc_status = os.system("mgc -v")
    if mgc_status != 0:
        anws = input("O mgc não foi corretamente configurado, você deseja configurar automaticamente [Y/n]: ")

        if anws == "n":
            exit(-1)
        
        # instalar mgcli
        _os = platform.system().lower()
        if _os != "linux":
            print("Apenas o linux eh suportado!")
            exit(-2)
        
        os.system("wget https://github.com/MagaluCloud/mgccli/releases/download/v0.29.0/mgccli_0.29.0_linux_amd64.deb")
        os.system("sudo dpkg -i ./mgccli_0.29.0_linux_amd64.deb")
        os.system("rm mgccli_0.29.0_linux_amd64.deb")

    terraform_status = os.system("terraform -v")
    if terraform_status != 0:
        anws = input("O terraform não foi corretamente configurado, você deseja configurar automaticamente [Y/n]: ")

        if anws == "n":
            exit(-1)

        # instalar mgcli
        _os = platform.system().lower()
        if _os != "linux":
            print("Apenas o linux eh suportado!")
            exit(-2)
        
        os.system("chmod +x install-terraform.sh")
        os.system("sudo ./install-terraform.sh")

    return

def up():
    # precisa chamar pra garantir que nao ha nenhuma maquina rodando
    down()
    os.system("chmod +x up.sh")
    os.system("./up.sh")

def down():
    os.system("chmod +x down.sh")
    os.system("./down.sh")

def main():
    parser = argparse.ArgumentParser(description="Ferramenta MFD para deploy automático")
    
    # Definindo os argumentos `--up` e `--down`
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--up', action='store_true', help="Realiza o deploy (sobe a aplicação)")
    group.add_argument('-d', '--down', action='store_true', help="Derruba a aplicação (faz o undeploy)")

    # Argumento obrigatório para o caminho do diretório
    parser.add_argument('directory', type=str, help="Caminho do diretório onde está a aplicação")
    parser.add_argument('sshKeyName', type=str, help="Nome da chave SSH")

    args = parser.parse_args()

    # Verifica se o caminho é um diretório válido
    if not os.path.isdir(args.directory):
        print(f"Erro: {args.directory} não é um diretório válido.")
        sys.exit(1)

    # Verificar se o usuario esta logado no mgc
    if args.up or args.down:
        check_config()
        #os.system("mgc auth login")

        try:
            shutil.rmtree("./src/html")
        except Exception as ex:
            print(ex)
        shutil.copytree(args.directory, "./src/html")


        with open("main.tf", "w") as file:
            file.write(MAIN_TF + args.sshKeyName + MAIN_TF_END)

        # Verificando as opções selecionadas
        if args.up:
            up()
        elif args.down:
            down()

if __name__ == "__main__":
    main()
