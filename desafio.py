from textwrap import dedent
from abc import ABC, abstractmethod
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

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

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")

        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True

        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
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

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def recover_account_client(user):
    print(user.contas)
    if user.contas:
        account = user.contas[0]
        return account
    
    print("\nUsuário não possui conta!")

def deposit(users):
    cpf = input("Informe seu CPF: ")
    user = filter_users(users, cpf)

    if not user:
        print("\nUsuário não existe!")
        return
    
    value = float(input("Informe o valor do depósito: "))
    operation = Deposito(value)

    account = recover_account_client(user)

    if account:
        user.realizar_transacao(account, operation)

def withdraw(users):
    cpf = input("Informe seu CPF: ")
    user = filter_users(users, cpf)
    
    if not user:
        print("\nUsuário não existe!")
        return

    value = float(input("Informe o valor do saque: "))
    operation = Saque(value)
    account = recover_account_client(user)

    if account:
        user.realizar_transacao(account, operation)


def check_statement(users):
    cpf = input("Informe seu CPF: ")
    user = filter_users(users, cpf)

    if user:
        account = recover_account_client(user)
        if not account:
            return
    else:
        print("\nUsuário não existe!")

    operations = account.historico.transacoes

    withdraw = ""
    if operations:
        for operation in operations:
            withdraw += f"\n\t{operation['tipo']} - R$ {operation['valor']:.2f}"
    else:
        withdraw = "Não houve movimentações na conta"
    
    print(f"\nExtrato da conta:\n{withdraw}")
    print(f"\nSaldo atual: R$ {account.saldo:.2f}")

def create_user(users):
    cpf = input("Informe:\n\tCPF (Apenas numeros): ")
    user = filter_users(users, cpf)

    if user:
        print("\nUsuário já existe!")
        return
    
    name = input("\tNome: ")
    birth_date = input("\tData de nascimento (dd-mm-aaaa): ")
    address = input("\tEndereço (logradouro, nro - bairro - cidade/sigla estado): ")

    user = PessoaFisica(nome=name, data_nascimento=birth_date, cpf=cpf, endereco=address)
    users.append(user)

    print("\nUsuário criado com sucesso!")

def filter_users(users, cpf):
    filtered_user = [user for user in users if cpf == user.cpf]
    return filtered_user[0] if filtered_user else None

def create_current_account(users, accounts, account_number):
    cpf = input("Informe seu CPF: ")
    user = filter_users(users, cpf)

    if user:
        account = ContaCorrente.nova_conta(cliente=user, numero=account_number)
        accounts.append(account)
        user.contas.append(account)
        account_number += 1
        print("\nConta criada com sucesso!") 
    
    else:
        print("\nUsuário não existe!")

    return account_number

def list_accounts(accounts):
    if accounts:
        for account in accounts:
            print(dedent(str(account)))
    else:
        print("Não há contas no banco de dados!")

def main():
    account_number = 1
    users = []
    accounts = []

    text = """
    ===============================
    [1] Depósito
    [2] Saque
    [3] Extrato
    [4] Criar Usuário
    [5] Criar Conta
    [6] Listar Contas
    [7] Sair
    ===============================
    > """

    while True:
        op = input(dedent(text))
        
        if op == "1":
            deposit(users)

        elif op == "2":
            withdraw(users)

        elif op == "3":
            check_statement(users)

        elif op == "4":
            create_user(users)

        elif op == "5":
            account_number = create_current_account(users, accounts, account_number)

        elif op == "6":
            list_accounts(accounts)

        elif op == "7":
            quit()

        else:
            print("Opção inválida!")

main()