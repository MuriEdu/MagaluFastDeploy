


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


  ssh_key_name = "zapzap"

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
