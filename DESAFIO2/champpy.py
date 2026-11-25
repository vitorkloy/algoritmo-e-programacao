"""
ChampPy - Sistema de Gerenciamento de Campeonatos Esportivos
Desafio 2 - Lógica de Programação - Tema 4 (Etapas 1 e 2)

Campeonato de futebol em pontos corridos, executado no terminal.
Os dados ficam apenas em memória. Requer Python 3.10 ou superior.
"""

import unicodedata

# ---------------------------------------------------------------------------
# Variáveis globais
# ---------------------------------------------------------------------------
# Constantes (em maiúsculas): valores fixos, apenas lidos pelas funções.
PONTOS_VITORIA = 3
PONTOS_EMPATE = 1
SEM_RESULTADO = -1  # posição da matriz sem partida registrada

# "Banco de dados" em memória. As funções recebem estas listas por parâmetro.
equipes = []   # lista de dicionários: cadastro + indicadores
partidas = []  # lista de dicionários: códigos das equipes + gols


# ---------------------------------------------------------------------------
# Entrada de dados e funções auxiliares
# ---------------------------------------------------------------------------
def ler_texto(mensagem):
    """
    Lê um texto obrigatório, removendo espaços sobrando.

    Parâmetros:
        mensagem (str): texto exibido ao usuário.
    Retorna:
        str: texto não vazio.
    """
    while True:
        # split() + join() elimina espaços nas pontas e espaços duplicados
        texto = " ".join(input(mensagem).split())
        if texto:
            return texto
        print("Erro: este campo é obrigatório.")


def ler_inteiro(mensagem, minimo=0):
    """
    Lê um número inteiro maior ou igual ao mínimo informado.

    Parâmetros:
        mensagem (str): texto exibido ao usuário.
        minimo (int): menor valor aceito.
    Retorna:
        int: número validado.
    """
    while True:
        try:
            numero = int(input(mensagem).strip())
        except ValueError:
            print("Erro: informe um número inteiro.")
            continue

        if numero >= minimo:
            return numero
        print(f"Erro: o valor deve ser maior ou igual a {minimo}.")


def confirmar(mensagem):
    """
    Faz uma pergunta de sim ou não.

    Parâmetros:
        mensagem (str): pergunta exibida ao usuário.
    Retorna:
        bool: True para sim, False para não.
    """
    while True:
        resposta = input(f"{mensagem} (s/n): ").strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "não", "nao"):
            return False
        print("Erro: responda com 's' ou 'n'.")


def exibir_titulo(titulo):
    """
    Exibe um título entre linhas separadoras.

    Parâmetros:
        titulo (str): texto do título.
    """
    print("\n" + "=" * 50)
    print(titulo)
    print("=" * 50)


def chave_alfabetica(equipe):
    """
    Gera a chave de ordenação alfabética, ignorando maiúsculas e acentos
    (assim "Águia" vem antes de "Bahia").

    Parâmetros:
        equipe (dict): equipe a ser ordenada.
    Retorna:
        tuple: (nome sem acentos, nome original em minúsculas).
    """
    nome = equipe["nome"].casefold()
    decomposto = unicodedata.normalize("NFD", nome)
    sem_acentos = ""
    for caractere in decomposto:
        if not unicodedata.combining(caractere):
            sem_acentos += caractere
    return (sem_acentos, nome)


def calcular_aproveitamento(equipe):
    """
    Calcula A = PTS / (PJ x 3) x 100.

    Parâmetros:
        equipe (dict): equipe avaliada.
    Retorna:
        float: percentual de aproveitamento (0 se não houver partidas).
    """
    if equipe["pj"] == 0:
        return 0.0
    return equipe["pts"] / (equipe["pj"] * PONTOS_VITORIA) * 100


def calcular_media_sofridos(equipe):
    """
    Calcula a média de gols sofridos por jogo.

    Parâmetros:
        equipe (dict): equipe com pelo menos uma partida.
    Retorna:
        float: gols sofridos divididos por partidas jogadas.
    """
    return equipe["gc"] / equipe["pj"]


def formatar_saldo(saldo):
    """
    Formata o saldo de gols com sinal de + quando positivo.

    Parâmetros:
        saldo (int): saldo de gols.
    Retorna:
        str: saldo formatado.
    """
    if saldo > 0:
        return f"+{saldo}"
    return str(saldo)


def largura_nomes(lista_equipes):
    """
    Calcula a largura da coluna de nomes para alinhar as tabelas.

    Parâmetros:
        lista_equipes (list): equipes que serão exibidas.
    Retorna:
        int: largura da coluna.
    """
    largura = len("Equipe")
    for equipe in lista_equipes:
        if len(equipe["nome"]) > largura:
            largura = len(equipe["nome"])
    return largura


# ---------------------------------------------------------------------------
# Buscas
# ---------------------------------------------------------------------------
def buscar_equipe(lista_equipes, codigo):
    """
    Busca convencional (com repetição) de uma equipe pelo código.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        codigo (int): código procurado.
    Retorna:
        dict | None: equipe encontrada ou None.
    """
    for equipe in lista_equipes:
        if equipe["codigo"] == codigo:
            return equipe
    return None


def buscar_equipe_recursivo(lista_equipes, codigo, indice=0):
    """
    Busca recursiva de uma equipe pelo código (Requisito 14).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        codigo (int): código procurado.
        indice (int): posição analisada nesta chamada.
    Retorna:
        dict | None: equipe encontrada ou None.
    """
    # Caso-base 1: chegou ao fim da lista sem encontrar
    if indice >= len(lista_equipes):
        return None
    # Caso-base 2: encontrou a equipe
    if lista_equipes[indice]["codigo"] == codigo:
        return lista_equipes[indice]
    # Chamada recursiva: analisa a próxima posição
    return buscar_equipe_recursivo(lista_equipes, codigo, indice + 1)


def nome_existe(lista_equipes, nome, codigo_ignorado=None):
    """
    Verifica se já existe equipe com o nome, sem diferenciar maiúsculas.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        nome (str): nome a verificar.
        codigo_ignorado (int | None): equipe que está sendo alterada.
    Retorna:
        bool: True se outra equipe já usa o nome.
    """
    for equipe in lista_equipes:
        mesmo_nome = equipe["nome"].casefold() == nome.casefold()
        if mesmo_nome and equipe["codigo"] != codigo_ignorado:
            return True
    return False


def selecionar_equipe(lista_equipes):
    """
    Pede um código ao usuário e localiza a equipe correspondente.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    Retorna:
        dict | None: equipe encontrada ou None (com mensagem de erro).
    """
    if not lista_equipes:
        print("Nenhuma equipe cadastrada.")
        return None

    codigo = ler_inteiro("Código da equipe: ", 1)
    equipe = buscar_equipe(lista_equipes, codigo)
    if equipe is None:
        print("Equipe não encontrada.")
    return equipe


# ---------------------------------------------------------------------------
# Equipes: cadastro, listagem, consulta, alteração e exclusão
# ---------------------------------------------------------------------------
def ler_nome_equipe(lista_equipes, codigo_ignorado=None):
    """
    Lê um nome de equipe obrigatório e não repetido.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        codigo_ignorado (int | None): equipe que está sendo alterada.
    Retorna:
        str: nome validado.
    """
    while True:
        nome = ler_texto("Nome da equipe: ")
        if not nome_existe(lista_equipes, nome, codigo_ignorado):
            return nome
        print("Erro: já existe uma equipe com esse nome.")


def criar_equipe(codigo, nome, cidade, treinador):
    """
    Monta a estrutura de uma equipe com os indicadores zerados.

    Parâmetros:
        codigo (int): identificador único.
        nome (str): nome da equipe.
        cidade (str): cidade de origem.
        treinador (str): nome do treinador.
    Retorna:
        dict: nova equipe.
    """
    return {
        "codigo": codigo,
        "nome": nome,
        "cidade": cidade,
        "treinador": treinador,
        "pj": 0, "v": 0, "e": 0, "d": 0,
        "gp": 0, "gc": 0, "sg": 0, "pts": 0,
    }


def cadastrar_equipe(lista_equipes):
    """
    Cadastra uma nova equipe (Requisito 02).

    Parâmetros:
        lista_equipes (list): lista que receberá a equipe.
    """
    exibir_titulo("CADASTRO DE EQUIPE")

    while True:
        codigo = ler_inteiro("Código da equipe: ", 1)
        if buscar_equipe(lista_equipes, codigo) is None:
            break
        print("Erro: já existe uma equipe com esse código.")

    nome = ler_nome_equipe(lista_equipes)
    cidade = ler_texto("Cidade de origem: ")
    treinador = ler_texto("Nome do treinador: ")

    lista_equipes.append(criar_equipe(codigo, nome, cidade, treinador))
    print("Equipe cadastrada com sucesso.")


def listar_equipes(lista_equipes):
    """
    Lista as equipes na ordem de cadastro (Requisito 03).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    """
    exibir_titulo("EQUIPES CADASTRADAS")
    if not lista_equipes:
        print("Nenhuma equipe cadastrada.")
        return

    for equipe in lista_equipes:
        print(f"Código: {equipe['codigo']} | Equipe: {equipe['nome']} | "
              f"Cidade: {equipe['cidade']} | "
              f"Treinador: {equipe['treinador']}")


def exibir_desempenho(equipe):
    """
    Exibe os dados cadastrais e os indicadores de uma equipe.

    Parâmetros:
        equipe (dict): equipe a exibir.
    """
    exibir_titulo("DESEMPENHO DA EQUIPE")
    print(f"Código: {equipe['codigo']}")
    print(f"Equipe: {equipe['nome']}")
    print(f"Cidade: {equipe['cidade']}")
    print(f"Treinador: {equipe['treinador']}")
    print()
    print(f"Partidas jogadas: {equipe['pj']}")
    print(f"Vitórias: {equipe['v']}")
    print(f"Empates: {equipe['e']}")
    print(f"Derrotas: {equipe['d']}")
    print()
    print(f"Gols marcados: {equipe['gp']}")
    print(f"Gols sofridos: {equipe['gc']}")
    print(f"Saldo de gols: {formatar_saldo(equipe['sg'])}")
    print()
    print(f"Pontos conquistados: {equipe['pts']}")
    print(f"Aproveitamento: {calcular_aproveitamento(equipe):.1f}%")
    print("=" * 50)


def consultar_equipe(lista_equipes):
    """
    Consulta o desempenho individual de uma equipe (Requisito 06).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    """
    exibir_titulo("CONSULTA DE EQUIPE")
    equipe = selecionar_equipe(lista_equipes)
    if equipe is not None:
        exibir_desempenho(equipe)


def alterar_equipe(lista_equipes):
    """
    Altera nome, cidade ou treinador. O código e as estatísticas não podem
    ser editados (Requisito 10).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    """
    exibir_titulo("ALTERAÇÃO DE EQUIPE")
    equipe = selecionar_equipe(lista_equipes)
    if equipe is None:
        return

    while True:
        print(f"\nAlterando a equipe de código {equipe['codigo']}")
        print(f"1 - Nome ({equipe['nome']})")
        print(f"2 - Cidade ({equipe['cidade']})")
        print(f"3 - Treinador ({equipe['treinador']})")
        print("0 - Voltar")
        opcao = input("Informe o que deseja modificar: ").strip()

        match opcao:
            case "1":
                equipe["nome"] = ler_nome_equipe(lista_equipes,
                                                 equipe["codigo"])
                print("Nome atualizado.")
            case "2":
                equipe["cidade"] = ler_texto("Nova cidade: ")
                print("Cidade atualizada.")
            case "3":
                equipe["treinador"] = ler_texto("Novo treinador: ")
                print("Treinador atualizado.")
            case "0":
                break
            case _:
                print("Erro: opção inválida.")


def equipe_possui_partidas(lista_partidas, codigo):
    """
    Verifica se a equipe participou de alguma partida.

    Parâmetros:
        lista_partidas (list): partidas registradas.
        codigo (int): código da equipe.
    Retorna:
        bool: True se participou como mandante ou visitante.
    """
    for partida in lista_partidas:
        if codigo == partida["mandante"] or codigo == partida["visitante"]:
            return True
    return False


def excluir_equipe(lista_equipes, lista_partidas):
    """
    Exclui uma equipe sem partidas, mediante confirmação (Requisito 10).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        lista_partidas (list): partidas registradas.
    """
    exibir_titulo("EXCLUSÃO DE EQUIPE")
    equipe = selecionar_equipe(lista_equipes)
    if equipe is None:
        return

    if equipe_possui_partidas(lista_partidas, equipe["codigo"]):
        print("Operação não permitida: a equipe possui partidas registradas.")
        return

    if confirmar(f"Confirma a exclusão da equipe {equipe['nome']}?"):
        lista_equipes.remove(equipe)
        print("Equipe excluída com sucesso.")
    else:
        print("Exclusão cancelada.")


# ---------------------------------------------------------------------------
# Partidas
# ---------------------------------------------------------------------------
def buscar_partida(lista_partidas, codigo_mandante, codigo_visitante):
    """
    Procura um confronto com o mesmo mando de campo.

    Parâmetros:
        lista_partidas (list): partidas registradas.
        codigo_mandante (int): código do mandante.
        codigo_visitante (int): código do visitante.
    Retorna:
        dict | None: partida encontrada ou None.
    """
    for partida in lista_partidas:
        if (partida["mandante"] == codigo_mandante
                and partida["visitante"] == codigo_visitante):
            return partida
    return None


def atualizar_estatisticas(equipe, gols_pro, gols_contra):
    """
    Atualiza os indicadores de uma equipe após uma partida (Requisito 05).

    Parâmetros:
        equipe (dict): equipe a atualizar (alterada diretamente).
        gols_pro (int): gols marcados pela equipe.
        gols_contra (int): gols sofridos pela equipe.
    """
    equipe["pj"] += 1
    equipe["gp"] += gols_pro
    equipe["gc"] += gols_contra
    equipe["sg"] = equipe["gp"] - equipe["gc"]

    if gols_pro > gols_contra:
        equipe["v"] += 1
        equipe["pts"] += PONTOS_VITORIA
    elif gols_pro == gols_contra:
        equipe["e"] += 1
        equipe["pts"] += PONTOS_EMPATE
    else:
        equipe["d"] += 1


def registrar_partida(lista_equipes, lista_partidas):
    """
    Registra o resultado de uma partida (Requisito 04).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        lista_partidas (list): lista que receberá a partida.
    """
    exibir_titulo("REGISTRO DE PARTIDA")
    if len(lista_equipes) < 2:
        print("Cadastre pelo menos duas equipes antes de registrar partidas.")
        return

    codigo_mandante = ler_inteiro("Código da equipe mandante: ", 1)
    codigo_visitante = ler_inteiro("Código da equipe visitante: ", 1)
    mandante = buscar_equipe(lista_equipes, codigo_mandante)
    visitante = buscar_equipe(lista_equipes, codigo_visitante)

    if mandante is None or visitante is None:
        print("Erro: as duas equipes precisam estar cadastradas.")
        return
    if codigo_mandante == codigo_visitante:
        print("Erro: uma equipe não pode enfrentar a si mesma.")
        return
    if buscar_partida(lista_partidas, codigo_mandante,
                      codigo_visitante) is not None:
        print("Erro: este confronto, com este mando, já foi registrado.")
        return

    gols_mandante = ler_inteiro(f"Gols do {mandante['nome']}: ")
    gols_visitante = ler_inteiro(f"Gols do {visitante['nome']}: ")

    print(f"\n{mandante['nome']} {gols_mandante} x "
          f"{gols_visitante} {visitante['nome']}")
    if not confirmar("Confirma o resultado?"):
        print("Registro cancelado.")
        return

    # A partida guarda os códigos: se um nome mudar, o histórico acompanha
    lista_partidas.append({
        "mandante": codigo_mandante,
        "visitante": codigo_visitante,
        "gols_mandante": gols_mandante,
        "gols_visitante": gols_visitante,
    })
    atualizar_estatisticas(mandante, gols_mandante, gols_visitante)
    atualizar_estatisticas(visitante, gols_visitante, gols_mandante)

    if gols_mandante > gols_visitante:
        print(f"Vitória do {mandante['nome']}.")
    elif gols_mandante < gols_visitante:
        print(f"Vitória do {visitante['nome']}.")
    else:
        print("A partida terminou empatada.")


def descrever_partida(lista_equipes, partida):
    """
    Monta o texto de uma partida com os nomes das equipes.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        partida (dict): partida registrada.
    Retorna:
        str: texto no formato "Mandante 3 x 1 Visitante".
    """
    mandante = buscar_equipe(lista_equipes, partida["mandante"])
    visitante = buscar_equipe(lista_equipes, partida["visitante"])
    return (f"{mandante['nome']} {partida['gols_mandante']} x "
            f"{partida['gols_visitante']} {visitante['nome']}")


def listar_resultados(lista_equipes, lista_partidas):
    """
    Lista os resultados registrados (Requisito 07).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        lista_partidas (list): partidas registradas.
    """
    exibir_titulo("RESULTADOS REGISTRADOS")
    if not lista_partidas:
        print("Nenhuma partida registrada.")
        return

    for partida in lista_partidas:
        print(descrever_partida(lista_equipes, partida))


# ---------------------------------------------------------------------------
# Classificação e ranking
# ---------------------------------------------------------------------------
def criterio_classificacao(equipe):
    """
    Chave de ordenação da tabela. O sinal negativo faz os maiores números
    virem primeiro, mantendo o nome em ordem alfabética crescente.

    Parâmetros:
        equipe (dict): equipe avaliada.
    Retorna:
        tuple: pontos, vitórias, saldo, gols marcados e nome.
    """
    return (-equipe["pts"], -equipe["v"], -equipe["sg"], -equipe["gp"],
            chave_alfabetica(equipe))


def gerar_classificacao(lista_equipes):
    """
    Gera a classificação sem modificar a lista original (Requisito 08).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    Retorna:
        list: nova lista ordenada.
    """
    return sorted(lista_equipes, key=criterio_classificacao)


def exibir_classificacao(lista_equipes):
    """
    Exibe a tabela de classificação.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    """
    exibir_titulo("TABELA DE CLASSIFICAÇÃO")
    if not lista_equipes:
        print("Nenhuma equipe cadastrada.")
        return

    largura = largura_nomes(lista_equipes)
    print(f"{'Pos.':<5}{'Equipe':<{largura}} {'PJ':>3} {'V':>3} {'E':>3} "
          f"{'D':>3} {'GP':>3} {'GC':>3} {'SG':>4} {'PTS':>4}")

    for posicao, equipe in enumerate(gerar_classificacao(lista_equipes), 1):
        print(f"{f'{posicao}º':<5}{equipe['nome']:<{largura}} "
              f"{equipe['pj']:>3} {equipe['v']:>3} {equipe['e']:>3} "
              f"{equipe['d']:>3} {equipe['gp']:>3} {equipe['gc']:>3} "
              f"{formatar_saldo(equipe['sg']):>4} {equipe['pts']:>4}")


def filtrar_com_partidas(lista_equipes):
    """
    Seleciona apenas as equipes que já jogaram.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    Retorna:
        list: nova lista com equipes de PJ maior que zero.
    """
    resultado = []
    for equipe in lista_equipes:
        if equipe["pj"] > 0:
            resultado.append(equipe)
    return resultado


def criterio_aproveitamento(equipe):
    """
    Chave de ordenação do ranking de aproveitamento.

    Parâmetros:
        equipe (dict): equipe avaliada.
    Retorna:
        tuple: aproveitamento, vitórias, saldo e nome.
    """
    return (-calcular_aproveitamento(equipe), -equipe["v"], -equipe["sg"],
            chave_alfabetica(equipe))


def exibir_ranking_aproveitamento(lista_equipes):
    """
    Exibe o ranking de aproveitamento (Requisito 13).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    """
    exibir_titulo("RANKING DE APROVEITAMENTO")
    participantes = filtrar_com_partidas(lista_equipes)
    if not participantes:
        print("Ainda não há equipes com partidas disputadas.")
        return

    ranking = sorted(participantes, key=criterio_aproveitamento)
    largura = largura_nomes(ranking)
    print(f"{'Pos.':<5}{'Código':<8}{'Equipe':<{largura}} {'PJ':>3} "
          f"{'PTS':>4} {'Aprov.':>8}")

    for posicao, equipe in enumerate(ranking, 1):
        print(f"{f'{posicao}º':<5}{equipe['codigo']:<8}"
              f"{equipe['nome']:<{largura}} {equipe['pj']:>3} "
              f"{equipe['pts']:>4} "
              f"{calcular_aproveitamento(equipe):>7.1f}%")


# ---------------------------------------------------------------------------
# Matrizes de confrontos
# ---------------------------------------------------------------------------
def obter_codigos_ordenados(lista_equipes):
    """
    Define a ordem das linhas e colunas das matrizes.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    Retorna:
        list: códigos em ordem crescente.
    """
    codigos = []
    for equipe in lista_equipes:
        codigos.append(equipe["codigo"])
    codigos.sort()
    return codigos


def criar_matriz(ordem):
    """
    Cria uma matriz quadrada preenchida com -1.

    Parâmetros:
        ordem (int): quantidade de linhas e colunas.
    Retorna:
        list: lista de listas.
    """
    matriz = []
    for _ in range(ordem):
        linha = []
        for _ in range(ordem):
            linha.append(SEM_RESULTADO)
        matriz.append(linha)
    return matriz


def construir_matrizes(codigos, lista_partidas):
    """
    Constrói as matrizes de gols marcados e sofridos pelo mandante
    (Requisito 11). Linha = mandante; coluna = visitante.

    Parâmetros:
        codigos (list): códigos na ordem das linhas e colunas.
        lista_partidas (list): partidas registradas.
    Retorna:
        tuple: (matriz de gols marcados, matriz de gols sofridos).
    """
    marcados = criar_matriz(len(codigos))
    sofridos = criar_matriz(len(codigos))

    for partida in lista_partidas:
        linha = codigos.index(partida["mandante"])
        coluna = codigos.index(partida["visitante"])
        marcados[linha][coluna] = partida["gols_mandante"]
        sofridos[linha][coluna] = partida["gols_visitante"]

    return marcados, sofridos


def exibir_matriz(titulo, codigos, matriz):
    """
    Exibe uma matriz com os códigos como cabeçalho.

    Parâmetros:
        titulo (str): descrição da matriz.
        codigos (list): códigos das linhas e colunas.
        matriz (list): lista de listas com os valores.
    """
    # A largura acompanha o maior código, para não desalinhar as colunas
    largura = max(len(str(max(codigos))), 3) + 2

    print(f"\n{titulo}")
    print(" " * largura + " |", end="")
    for codigo in codigos:
        print(f"{codigo:>{largura}}", end="")
    print()
    print("-" * (largura * (len(codigos) + 1) + 2))

    for indice_linha in range(len(matriz)):
        print(f"{codigos[indice_linha]:>{largura}} |", end="")
        for valor in matriz[indice_linha]:
            print(f"{valor:>{largura}}", end="")
        print()


def visualizar_matrizes(lista_equipes, lista_partidas):
    """
    Monta e apresenta as duas matrizes de confrontos.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        lista_partidas (list): partidas registradas.
    """
    exibir_titulo("MATRIZ DE CONFRONTOS")
    if not lista_equipes:
        print("Nenhuma equipe cadastrada.")
        return

    codigos = obter_codigos_ordenados(lista_equipes)
    marcados, sofridos = construir_matrizes(codigos, lista_partidas)

    print("Linha = mandante | Coluna = visitante | -1 = sem resultado")
    for codigo in codigos:
        print(f"  {codigo} = {buscar_equipe(lista_equipes, codigo)['nome']}")

    exibir_matriz("GOLS MARCADOS PELO MANDANTE", codigos, marcados)
    exibir_matriz("GOLS SOFRIDOS PELO MANDANTE", codigos, sofridos)


# ---------------------------------------------------------------------------
# Cálculos do campeonato
# ---------------------------------------------------------------------------
def gerar_lista_gols(lista_partidas):
    """
    Gera a lista com o total de gols de cada partida.

    Parâmetros:
        lista_partidas (list): partidas registradas.
    Retorna:
        list: números inteiros.
    """
    gols = []
    for partida in lista_partidas:
        gols.append(partida["gols_mandante"] + partida["gols_visitante"])
    return gols


def somar_gols(lista_gols):
    """
    Soma os gols com repetição convencional.

    Parâmetros:
        lista_gols (list): gols de cada partida.
    Retorna:
        int: total de gols.
    """
    total = 0
    for gols in lista_gols:
        total += gols
    return total


def somar_gols_recursivo(lista_gols, indice=0):
    """
    Soma os gols com recursividade (Requisito 15).

    Parâmetros:
        lista_gols (list): gols de cada partida.
        indice (int): elemento processado nesta chamada.
    Retorna:
        int: soma do elemento atual até o final da lista.
    """
    # Caso-base: não há mais elementos
    if indice >= len(lista_gols):
        return 0
    # Elemento atual + soma recursiva do restante
    return lista_gols[indice] + somar_gols_recursivo(lista_gols, indice + 1)


def calcular_resumo(lista_partidas):
    """
    Calcula os números gerais usados nos três relatórios.

    Parâmetros:
        lista_partidas (list): partidas registradas.
    Retorna:
        dict: partidas, gols, vitórias por mando, empates, média e
        percentual de empates.
    """
    mandantes = 0
    visitantes = 0
    empates = 0

    for partida in lista_partidas:
        if partida["gols_mandante"] > partida["gols_visitante"]:
            mandantes += 1
        elif partida["gols_mandante"] < partida["gols_visitante"]:
            visitantes += 1
        else:
            empates += 1

    total_partidas = len(lista_partidas)
    total_gols = somar_gols(gerar_lista_gols(lista_partidas))
    media = 0.0
    percentual_empates = 0.0

    if total_partidas > 0:  # evita divisão por zero
        media = total_gols / total_partidas
        percentual_empates = empates / total_partidas * 100

    return {
        "partidas": total_partidas,
        "gols": total_gols,
        "vitorias_mandantes": mandantes,
        "vitorias_visitantes": visitantes,
        "empates": empates,
        "media": media,
        "percentual_empates": percentual_empates,
    }


def criterio_ataque(equipe):
    """
    Chave do melhor ataque: mais gols marcados; empate pelo nome.

    Parâmetros:
        equipe (dict): equipe avaliada.
    Retorna:
        tuple: gols marcados (negativo) e nome.
    """
    return (-equipe["gp"], chave_alfabetica(equipe))


def criterio_defesa(equipe):
    """
    Chave da melhor defesa: menor média de gols sofridos; depois o nome.

    Parâmetros:
        equipe (dict): equipe avaliada.
    Retorna:
        tuple: média de gols sofridos e nome.
    """
    return (calcular_media_sofridos(equipe), chave_alfabetica(equipe))


def criterio_saldo(equipe):
    """
    Chave do maior saldo de gols; empate pelo nome.

    Parâmetros:
        equipe (dict): equipe avaliada.
    Retorna:
        tuple: saldo (negativo) e nome.
    """
    return (-equipe["sg"], chave_alfabetica(equipe))


def criterio_maior_aproveitamento(equipe):
    """
    Chave do maior aproveitamento; empate somente pelo nome.

    Parâmetros:
        equipe (dict): equipe avaliada.
    Retorna:
        tuple: aproveitamento (negativo) e nome.
    """
    return (-calcular_aproveitamento(equipe), chave_alfabetica(equipe))


def encontrar_destaques(lista_equipes):
    """
    Identifica as equipes destaque do campeonato (Requisito 12).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    Retorna:
        dict: textos de melhor ataque, defesa, saldo e aproveitamento.
    """
    sem_dados = "Dados insuficientes"
    destaques = {"ataque": sem_dados, "defesa": sem_dados,
                 "saldo": sem_dados, "aproveitamento": sem_dados}

    participantes = filtrar_com_partidas(lista_equipes)
    if not participantes:
        return destaques

    # min() com a chave devolve o primeiro colocado de cada critério
    ataque = min(participantes, key=criterio_ataque)
    defesa = min(participantes, key=criterio_defesa)
    saldo = min(participantes, key=criterio_saldo)
    melhor = min(participantes, key=criterio_maior_aproveitamento)

    destaques["ataque"] = f"{ataque['nome']} ({ataque['gp']} gols)"
    destaques["defesa"] = (f"{defesa['nome']} "
                           f"({calcular_media_sofridos(defesa):.2f} "
                           "gols sofridos por jogo)")
    destaques["aproveitamento"] = (f"{melhor['nome']} "
                                   f"({calcular_aproveitamento(melhor):.1f}%)")

    if saldo["sg"] > 0:
        destaques["saldo"] = f"{saldo['nome']} ({formatar_saldo(saldo['sg'])})"
    else:
        destaques["saldo"] = "Nenhuma equipe com saldo positivo"

    return destaques


def total_gols_partida(partida):
    """
    Soma os gols das duas equipes.

    Parâmetros:
        partida (dict): partida registrada.
    Retorna:
        int: total de gols da partida.
    """
    return partida["gols_mandante"] + partida["gols_visitante"]


def diferenca_gols_partida(partida):
    """
    Calcula a diferença absoluta de gols.

    Parâmetros:
        partida (dict): partida registrada.
    Retorna:
        int: diferença entre os placares.
    """
    return abs(partida["gols_mandante"] - partida["gols_visitante"])


def encontrar_partida_destaque(lista_equipes, lista_partidas, medida):
    """
    Encontra a partida com o maior valor de uma medida. Em caso de empate,
    vence a ordem alfabética do mandante e depois a do visitante.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        lista_partidas (list): partidas registradas.
        medida (function): total_gols_partida ou diferenca_gols_partida.
    Retorna:
        dict | None: partida destaque ou None se não houver partidas.
    """
    destaque = None
    melhor_chave = None

    for partida in lista_partidas:
        mandante = buscar_equipe(lista_equipes, partida["mandante"])
        visitante = buscar_equipe(lista_equipes, partida["visitante"])
        chave = (-medida(partida), chave_alfabetica(mandante),
                 chave_alfabetica(visitante))

        if melhor_chave is None or chave < melhor_chave:
            melhor_chave = chave
            destaque = partida

    return destaque


def descrever_maior_goleada(lista_equipes, lista_partidas):
    """
    Monta o texto da partida com maior diferença de gols.

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        lista_partidas (list): partidas registradas.
    Retorna:
        str: descrição ou mensagem de ausência de dados.
    """
    partida = encontrar_partida_destaque(lista_equipes, lista_partidas,
                                         diferenca_gols_partida)
    if partida is None:
        return "Dados insuficientes"
    if diferenca_gols_partida(partida) == 0:
        return "Não há (todas as partidas terminaram empatadas)"
    return (f"{descrever_partida(lista_equipes, partida)} "
            f"(diferença de {diferenca_gols_partida(partida)})")


# ---------------------------------------------------------------------------
# Relatórios
# ---------------------------------------------------------------------------
def resumo_campeonato(lista_equipes, lista_partidas):
    """
    Exibe o resumo geral do campeonato (Requisito 09).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        lista_partidas (list): partidas registradas.
    """
    exibir_titulo("RESUMO DO CAMPEONATO")
    resumo = calcular_resumo(lista_partidas)

    print(f"Equipes cadastradas: {len(lista_equipes)}")
    print(f"Partidas realizadas: {resumo['partidas']}")
    print(f"Total de gols: {resumo['gols']}")

    if resumo["partidas"] == 0:
        print("Ainda não existem dados suficientes para calcular médias "
              "e resultados.")
        return

    com_vencedor = resumo["partidas"] - resumo["empates"]
    print(f"Média de gols por partida: {resumo['media']:.2f}")
    print(f"Partidas empatadas: {resumo['empates']}")
    print(f"Partidas com vencedor: {com_vencedor}")


def analise_estatistica(lista_equipes, lista_partidas):
    """
    Exibe a análise estatística de desempenho (Requisito 12).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        lista_partidas (list): partidas registradas.
    """
    exibir_titulo("ANÁLISE ESTATÍSTICA")
    if not lista_partidas:
        print("Ainda não existem partidas registradas para análise.")
        return

    resumo = calcular_resumo(lista_partidas)
    destaques = encontrar_destaques(lista_equipes)

    print(f"Total de gols: {resumo['gols']}")
    print(f"Média de gols por partida: {resumo['media']:.2f}")
    print(f"Percentual de empates: {resumo['percentual_empates']:.1f}%")
    print("Maior goleada: "
          f"{descrever_maior_goleada(lista_equipes, lista_partidas)}")
    print(f"Melhor ataque: {destaques['ataque']}")
    print(f"Melhor defesa: {destaques['defesa']}")
    print(f"Maior saldo de gols: {destaques['saldo']}")
    print(f"Maior aproveitamento: {destaques['aproveitamento']}")


def relatorio_consolidado(lista_equipes, lista_partidas):
    """
    Exibe o relatório gerencial consolidado (Requisito 16).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
        lista_partidas (list): partidas registradas.
    """
    exibir_titulo("RELATÓRIO GERENCIAL CONSOLIDADO")
    resumo = calcular_resumo(lista_partidas)

    print(f"Equipes cadastradas: {len(lista_equipes)}")
    print(f"Partidas realizadas: {resumo['partidas']}")
    print(f"Total de gols: {resumo['gols']}")

    if resumo["partidas"] == 0:
        print("Sem partidas registradas: não há dados suficientes para os "
              "demais indicadores.")
        return

    destaques = encontrar_destaques(lista_equipes)
    lider = gerar_classificacao(lista_equipes)[0]
    mais_gols = encontrar_partida_destaque(lista_equipes, lista_partidas,
                                           total_gols_partida)

    print(f"Média de gols por partida: {resumo['media']:.2f}")
    print(f"Vitórias dos mandantes: {resumo['vitorias_mandantes']}")
    print(f"Vitórias dos visitantes: {resumo['vitorias_visitantes']}")
    print(f"Empates: {resumo['empates']}")
    print(f"Líder da classificação: {lider['nome']} ({lider['pts']} pontos)")
    print(f"Melhor ataque: {destaques['ataque']}")
    print(f"Melhor defesa: {destaques['defesa']}")
    print(f"Maior aproveitamento: {destaques['aproveitamento']}")
    print("Partida com mais gols: "
          f"{descrever_partida(lista_equipes, mais_gols)} "
          f"({total_gols_partida(mais_gols)} gols)")
    print("Partida com maior diferença: "
          f"{descrever_maior_goleada(lista_equipes, lista_partidas)}")


# ---------------------------------------------------------------------------
# Demonstrações de recursividade
# ---------------------------------------------------------------------------
def executar_busca_recursiva(lista_equipes):
    """
    Executa a busca recursiva e compara com a convencional (Requisito 14).

    Parâmetros:
        lista_equipes (list): equipes cadastradas.
    """
    exibir_titulo("BUSCA RECURSIVA DE EQUIPE")
    codigo = ler_inteiro("Código procurado: ", 1)

    recursiva = buscar_equipe_recursivo(lista_equipes, codigo, 0)
    convencional = buscar_equipe(lista_equipes, codigo)

    for rotulo, equipe in (("Recursiva", recursiva),
                           ("Convencional", convencional)):
        if equipe is None:
            print(f"Busca {rotulo.lower()}: None (equipe não encontrada)")
        else:
            print(f"Busca {rotulo.lower()}: {equipe['codigo']} - "
                  f"{equipe['nome']}")

    # "is" verifica se as duas buscas devolveram o mesmo objeto
    if recursiva is convencional:
        print("Comparação: os resultados são iguais.")
    else:
        print("Comparação: os resultados são diferentes.")


def calcular_gols_recursao(lista_partidas):
    """
    Compara a soma recursiva com a soma por repetição (Requisito 15).

    Parâmetros:
        lista_partidas (list): partidas registradas.
    """
    exibir_titulo("TOTAL DE GOLS DO CAMPEONATO")
    if not lista_partidas:
        print("Nenhuma partida registrada. Total de gols: 0")
        return

    lista_gols = gerar_lista_gols(lista_partidas)
    total_recursivo = somar_gols_recursivo(lista_gols)
    total_repeticao = somar_gols(lista_gols)

    print(f"Gols por partida: {lista_gols}")
    print(f"Total por recursividade: {total_recursivo}")
    print(f"Total por repetição: {total_repeticao}")

    if total_recursivo == total_repeticao:
        print("Comparação: os resultados são iguais.")
    else:
        print("Comparação: os resultados são diferentes.")


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------
def exibir_menu():
    """Apresenta o menu principal (Requisitos 01 e 17)."""
    exibir_titulo("CHAMPPY | MENU PRINCIPAL")
    print(" 1 - Cadastrar equipe")
    print(" 2 - Listar equipes")
    print(" 3 - Registrar partida")
    print(" 4 - Consultar equipe")
    print(" 5 - Consultar resultados")
    print(" 6 - Exibir classificação")
    print(" 7 - Consultar resumo do campeonato")
    print(" 8 - Alterar cadastro de equipe")
    print(" 9 - Excluir equipe")
    print("10 - Visualizar matriz de confrontos")
    print("11 - Consultar análise estatística")
    print("12 - Consultar ranking de aproveitamento")
    print("13 - Realizar busca recursiva")
    print("14 - Calcular total de gols por recursão")
    print("15 - Gerar relatório consolidado")
    print(" 0 - Encerrar aplicação")


def main():
    """Mantém o menu em execução até o usuário escolher encerrar."""
    while True:
        exibir_menu()
        opcao = input("Informe a opção desejada: ").strip()

        match opcao:
            case "1":
                cadastrar_equipe(equipes)
            case "2":
                listar_equipes(equipes)
            case "3":
                registrar_partida(equipes, partidas)
            case "4":
                consultar_equipe(equipes)
            case "5":
                listar_resultados(equipes, partidas)
            case "6":
                exibir_classificacao(equipes)
            case "7":
                resumo_campeonato(equipes, partidas)
            case "8":
                alterar_equipe(equipes)
            case "9":
                excluir_equipe(equipes, partidas)
            case "10":
                visualizar_matrizes(equipes, partidas)
            case "11":
                analise_estatistica(equipes, partidas)
            case "12":
                exibir_ranking_aproveitamento(equipes)
            case "13":
                executar_busca_recursiva(equipes)
            case "14":
                calcular_gols_recursao(partidas)
            case "15":
                relatorio_consolidado(equipes, partidas)
            case "0":
                print("Aplicação encerrada. Até logo.")
                break
            case _:
                print("Erro: opção inválida.")

        input("\nPressione Enter para continuar...")


# Executa o menu somente quando o arquivo é rodado diretamente
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nAplicação interrompida pelo usuário.")
