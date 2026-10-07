"""
Nessa prática o objetivo é praticar python para entender conceitos e criar um sisteminha de estacionamento simples.

O projeto simula uma situação real em que o sistema recebe informações de entrada do usuário,
como o nome do cliente, o número da placa do veículo e o tempo de permanência no estacionamento, se o plano é
avulso ou mensal.

Com essas informações o sistema exibirá aquilo que sairia por exemplo em uma nota fiscal, como o nome do cliente,
 a placa do veículo, o tempo de permanência e o valor a ser pago pelo estacionamento.
 
Tendo acesso as informações, o sistema calcula o valor a ser pago pelo estacionamento e exibe o resultado
para o usuário automaticamente.

Regras do sistema:
- Até 1 hora o valor é de R$ 5,00.
- Acima de 1 até 3 horas o valor é de R$ 10,00.
- Acima de 3 horas até 5 horas o valor é de R$ 15,00.
- Acima de 5 horas o valor é de R$ 20,00.
- Para clientes que forem mensalistas é aplicado desconto de 20% sobre o valor total.
- Para clientes que forem avulsos não há desconto. O valor é normal.
- O sistema deve apresentar NOTA FISCAL com as informações do cliente, placa do veículo, tipo do cliente 
(mensalista = SIM, avulso = NÃO), tempo de permanência e o valor do desconto caso se encaixe na categoria mensalista, e o
valor a ser pago.

Let's go!
"""

print("Bem-vindo ao sistema de estacionamento PAGPARK!")

nome_cliente = input("Informe seu nome: ")
placa_veiculo = input("Informe a placa do seu veículo: ")
tempo_permanencia = float(input("Informe o tempo de permanência em horas: "))
tipo_cliente = input("Você é mensalista? (SIM/NÃO): ").strip().upper()

if tempo_permanencia <= 1:
    valor = 5.00
elif tempo_permanencia <= 3:
    valor = 10.00
elif tempo_permanencia <= 5:
    valor = 15.00

else:
    valor = 20.00

if tipo_cliente == "SIM":
    desconto = valor * 0.20
    valor = valor - desconto
else: 
    desconto = 0.00
    valor = valor

print("----------------------------------------------------")
print("------NOTA FISCAL DE SERVIÇO DE ESTACIONAMENTO------")
print("---------------RESUMO DO SERVIÇO--------------------")
print("------Cliente: ", nome_cliente, "-------------------")
print("------Placa do veículo: ", placa_veiculo, "---------")
print("------Tempo de permanência: ", tempo_permanencia, "-")
print("------Mensalista?: ", tipo_cliente, "---------------")
print("------Valor do desconto: ", desconto, "-------------")
print("------Valor Total: ", valor, "----------------------")
print("----------------------------------------------------")