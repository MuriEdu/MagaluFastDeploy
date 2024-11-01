yes yes | terraform destroy

rm -rf .t*
rm terr*

yes yes | terraform init
yes yes | terraform plan
yes yes | terraform apply

echo "Clique abaixo para obter informacoes (IP) sobre sua maquina"
echo "https://console.magalu.cloud/virtual-machine/details?id=`mgc vm instances list --control.limit 400 | grep zap2 | cut -d " " -f2`"