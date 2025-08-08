from abc import ABC, abstractmethod
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco
        self._contas = []
    
    @property
    def contas(self):
        return self._contas
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento
    
    @property
    def nome(self):
        return self._nome

    @property
    def cpf(self):
        return self._cpf

    def __str__(self):
        return f"""
        Nome: {self._nome}
        CPF: {self._cpf}
        Data de Nascimento: {self._data_nascimento}
        Endereço: {self._endereco}
        Contas vinculadas: {len(self.contas)}
        """

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "7777"
        self._cliente = cliente
        self._historico = Historico()
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    @property
    def historico(self):
        return self._historico
    
    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)
    
    def sacar(self, valor):
        if valor > 0:
            if valor > self._saldo:
                print("[ERRO] >> Você não possui saldo suficiente para realizar o saque.")
            
            self._saldo -= valor
            print("[SUCESSO] >> Saque realizado com sucesso!.")
            return True
        else:
            print("[ERRO] >> O valor de saque especificado é inválido.")

        return False

    def depositar(self, valor):
        if valor > 0:            
            self._saldo += valor
            print("[SUCESSO] >> Depósito realizado com sucesso!.")
            return True
        else:
            print("[ERRO] >> O valor de depósito especificado é inválido.")
            return False

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 500, limite_saques = 3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        num_saques = len([tr for tr in self._historico._transacoes if tr["tipo"] == "Saque"])

        if valor > self._limite:
            print("[ERRO] >> O valor de saque excede seu limite.")
        elif num_saques >= self._limite_saques:
            print("[ERRO] >> O limite de saques diário foi atingido.")
        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return f"""
        Agência: {self.agencia}
        C/C: {self.numero}
        Titular: {self.cliente.nome}
        Saldo: R$ {self.saldo:.2f}
        """

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @classmethod
    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso = conta.depositar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso = conta.sacar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)

def menu():
    return """
        ======= BANCO PYTHON =======
        Seja bem-vindo(a), qual
        operação deseja fazer?

        1. Depositar
        2. Sacar
        3. Ver extrato
        4. Criar novo usuário
        5. Criar conta corrente
        6. Listar usuários
        7. Listar contas
        8. Sair
        ============================
    """

def filtra_cliente(cpf, clientes):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

def depositar(clientes):
    cpf = input("Informe o CPF do titular =>  ").strip()
    cliente = filtra_cliente(cpf, clientes)
    
    if not cliente:
        print("[ERRO] >> Não foi encontrado um cliente com o CPF informado.")
        return
    
    montante = float(input("Informe o valor do depósito => "))

    if montante > 0:
        transacao = Deposito(montante)
        conta = cliente.contas[0]

        if not conta:
            print("[ERRO] >> O cliente ainda não possui uma conta própria.")
            return

        cliente.realizar_transacao(conta, transacao)
    else:
        print("[ERRO] >> O valor de depósito informado é inválido.")

def sacar(clientes):
    cpf = input("Informe o CPF do titular =>  ").strip()
    cliente = filtra_cliente(cpf, clientes)

    if not cliente:
        print("[ERRO] >> Não foi encontrado um cliente com o CPF informado.")
        return
    
    montante = float(input("Informe o valor do saque => "))

    if montante > 0:
        transacao = Saque(montante)
        conta = cliente.contas[0]

        if not conta:
            print("[ERRO] >> O cliente ainda não possui uma conta própria.")
            return

        cliente.realizar_transacao(conta, transacao)
    else:
        print("[ERRO] >> O valor de saque informado é inválido.")

def exibe_extrato(clientes):
    cpf = input("Informe o CPF do titular =>  ").strip()
    cliente = filtra_cliente(cpf, clientes)
    if not cliente:
        print("[ERRO] >> Não foi encontrado um cliente com o CPF informado.")
        return

    conta = cliente.contas[0]
    if not conta:
            print("[ERRO] >> O cliente ainda não possui uma conta própria.")
            return
    
    print("\n============= EXTRATO =============")
    transacoes = cliente.historico.transacoes
    extrato = ""

    if not transacoes:
        print("N/A")
    else:
        for transacao in transacoes:
            extrato += f"{transacao["tipo"]}: R${transacao["valor"]:.2f}"
    
    print(extrato)
    print(f"SALDO: R${conta.saldo:.2f}")
    print("\n===================================")
    
def verifica_usuario(cpf, lista_usuarios):
    for usuario in lista_usuarios:
        if usuario["cpf"] == cpf:
            return usuario
    return None

def cria_usuario(clientes):
    cpf = input("Informe seu CPF:  ").strip()
    cliente = filtra_cliente(cpf, clientes)

    if not cliente:
        nome = input("Informe seu nome completo: ").strip()
        data_nasc = input("Informe sua data de nascimento (dia/mês/ano): ").strip()
        endereco = input("Informe seu endereço (logradouro, número - bairro - cidade/sigla - estado): ").strip()

        cliente = PessoaFisica(endereco, cpf, nome, data_nasc)
        clientes.append(cliente)

        print("*** Usuário cadastrado com sucesso! ***")
    else:
        print("[ERRO] >> Já foi encontrado um cliente com o CPF informado.")
        return

def cria_conta_corrente(num_conta, clientes, contas):
    cpf = input("Informe o CPF do titular =>  ").strip()
    cliente = filtra_cliente(cpf, clientes)

    if not cliente:
        print("[ERRO] >> Não foi encontrado um cliente com o CPF informado.")
        return
    
    conta = ContaCorrente.nova_conta(numero = num_conta, cliente = cliente)
    contas.append(conta)
    cliente.contas.append(conta)

    print("*** Conta corrente registrada com sucesso! ***")

def listar_clientes(clientes):
    print("\n====== USUÁRIOS CADASTRADOS ======")
    if clientes:
        for cliente in clientes:
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
            print(cliente)
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    else:
        print("N/A")
    print("=" * 34)

def listar_contas(contas):
    print("\n====== CONTAS REGISTRADAS ======")
    if contas:
        for conta in contas:
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
            print(conta)
            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    else:
        print("N/A")
    print("=" * 32)

def main():
    clientes = []
    contas = []

    while True:
        print(menu())
        operacao = input().strip()

        if operacao == "1":     ## Depósito
            depositar(clientes)
        
        elif operacao == "2":       ## Saque
            sacar(clientes)

        elif operacao == "3":       ## Ver extrato
            exibe_extrato(clientes)

        elif operacao == "4":       ## Cria novo usuário
            cria_usuario(clientes)

        elif operacao == "5":       ## Cria conta corrente
            num_conta = len(contas) + 1
            cria_conta_corrente(num_conta, clientes, contas)

        elif operacao == "6":       ## Lista usuários
            listar_clientes(clientes)

        elif operacao == "7":       ## Lista contas
            listar_contas(contas)

        elif operacao == "8":       ## Sair
            print("*** Obrigado pela confiança, até a próxima! ***")
            break

        else:
            print("[ERRO] >> Opção inválida, escolha novamente!")

main()