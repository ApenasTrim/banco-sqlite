import sqlite3

#criacao do banco e tabela
def iniciar_banco():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    
    #criar tabela contas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contas_bancarias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titular TEXT NOT NULL,
        saldo REAL NOT NULL DEFAULT 0.0,
        cpf TEXT NOT NULL UNIQUE,
        CHECK (length(cpf) = 11),
        CHECK (saldo >= 0.0)
    )""")
    
    #criar historico
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico_transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conta_origem_id INTEGER NOT NULL,
        conta_destino_id INTEGER NOT NULL,
        valor REAL NOT NULL
    )""")
    conexao.commit()
    conexao.close()

#cadastro
def criar_conta():
    print("\nCADASTRO DE CONTA")
    titular = input("Nome do Titular: ")
    cpf = input("Digite o CPF (Apenas 11 números): ")
    
    if len(cpf) != 11:
        print("ERRO: O CPF precisa ter exatamente 11 dígitos!")
        return

    saldo_inicial = float(input("Saldo Inicial: R$ "))

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "INSERT INTO contas_bancarias (titular, cpf, saldo) VALUES (?, ?, ?)",
            (titular, cpf, saldo_inicial)
        )
        conexao.commit()
        print(f"CONCLUÍDO: Conta criada para {titular}!")
    except sqlite3.IntegrityError:
        print("ERRO: Este CPF já está cadastrado no sistema.")
    finally:
        conexao.close()

#ver saldo e dados
def consultar_saldo():
    print("\nCONSULTAR SALDO E EXTRATO")
    conta_id = int(input("Digite o ID da Conta: "))

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    
    cursor.execute("SELECT titular, saldo, cpf FROM contas_bancarias WHERE id = ?", (conta_id,))
    conta = cursor.fetchone()
    
    if not conta:
        print("ERRO: Conta não encontrada.")
        conexao.close()
        return

    titular, saldo, cpf = conta
    print("\n")
    print(f"EXTRATO DA CONTA ID: {conta_id}")
    print("\n")
    print(f"Titular: {titular}")
    print(f"CPF:     {cpf[0:3]}.***.***-{cpf[-2:]}") #privacidade
    print(f"Saldo:   R$ {saldo:.2f}")
    print("\n")
    
    #ultimas transacoes
    cursor.execute("""
        SELECT id, conta_origem_id, conta_destino_id, valor 
        FROM historico_transacoes 
        WHERE conta_origem_id = ? OR conta_destino_id = ?
        ORDER BY id DESC LIMIT 5
    """, (conta_id, conta_id))
    
    historico = cursor.fetchall()
    if historico:
        print("Últimas movimentações:")
        for log in historico:
            if log[1] == conta_id:
                print(f"  - Enviou um Pix de R$ {log[3]:.2f} para a Conta ID {log[2]}")
            else:
                print(f"  + Recebeu um Pix de R$ {log[3]:.2f} da Conta ID {log[1]}")
    else:
        print("Nenhuma movimentação recente.")
    print("\n")
    conexao.close()

#transferencia
def transferir():
    print("\nREALIZAR TRANSFERÊNCIA")
    origem = int(input("ID da Conta de Origem (Quem vai pagar): "))
    destino = int(input("ID da Conta de Destino (Quem vai receber): "))
    valor = float(input("Valor do Pix: R$ "))

    if valor <= 0:
        print("ERRO: O valor deve ser maior que zero.")
        return

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    try:
        #verificacao de existencia e saldo
        cursor.execute("SELECT saldo FROM contas_bancarias WHERE id = ?", (origem,))
        resultado_origem = cursor.fetchone()
        
        cursor.execute("SELECT id FROM contas_bancarias WHERE id = ?", (destino,))
        resultado_destino = cursor.fetchone()
        
        if not resultado_origem:
            print("ERRO: Conta de origem não encontrada.")
            return
        if not resultado_destino:
            print("ERRO: Conta de destino não encontrada.")
            return
            
        saldo_atual = resultado_origem[0]
        if saldo_atual < valor:
            print(f"ERRO: Saldo insuficiente! Você tem apenas R$ {saldo_atual:.2f}")
            return

        #executa transacao
        cursor.execute("UPDATE contas_bancarias SET saldo = saldo - ? WHERE id = ?", (valor, origem))
        cursor.execute("UPDATE contas_bancarias SET saldo = saldo + ? WHERE id = ?", (valor, destino))
        cursor.execute("INSERT INTO historico_transacoes (conta_origem_id, conta_destino_id, valor) VALUES (?, ?, ?)", (origem, destino, valor))
        
        conexao.commit()
        print("TRANSAÇÃO REALIZADA COM SUCESSO!")
        
    except sqlite3.Error:
        conexao.rollback()
        print("ERRO CRÍTICO: A transação falhou e foi cancelada por segurança.")
    finally:
        conexao.close()

#apagar contas
def apagar_conta():
    print("\nENCERRAMENTO DE CONTA")
    conta_id = int(input("Digite o ID da conta que deseja apagar: "))
    
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    
    #existencia da conta e se existe saldo
    cursor.execute("SELECT titular, saldo FROM contas_bancarias WHERE id = ?", (conta_id,))
    conta = cursor.fetchone()
    
    if not conta:
        print("ERRO: Conta não encontrada.")
        conexao.close()
        return
        
    titular, saldo = conta
    
    #verificar se ainda existe dinheiro dentro da conta
    if saldo > 0:
        print(f"ERRO: A conta de {titular} possui um saldo de R$ {saldo:.2f}.")
        print("Saque ou transfira o dinheiro antes de encerrar a conta.")
        conexao.close()
        return

    #confirmacao
    confirmacao = input(f"Tem certeza que deseja apagar a conta de {titular}? (S/N): ").upper()
    
    if confirmacao == "S":
        try:
            #deletar sql
            cursor.execute("DELETE FROM contas_bancarias WHERE id = ?", (conta_id,))
            conexao.commit()
            print(f"CONTA ID {conta_id} APAGADA COM SUCESSO!")
        except sqlite3.Error:
            conexao.rollback()
            print("ERRO: Não foi possível apagar a conta devido a um erro no banco.")
    else:
        print("Operation cancelada.")
        
    conexao.close()

#menu
def menu():
    iniciar_banco()
    while True:
        print("\n")
        print("BANCO")
        print("\n")
        print("[1] Criar Nova Conta")
        print("[2] Consultar Saldo/Extrato")
        print("[3] Transferir")
        print("[4] Apagar Conta")
        print("[5] Sair do Sistema")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            criar_conta()
        elif opcao == "2":
            consultar_saldo()
        elif opcao == "3":
            transferir()
        elif opcao == "4":
            apagar_conta()
        elif opcao == "5":
            print("Encerrando o sistema... Até logo!")
            break
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    menu()
