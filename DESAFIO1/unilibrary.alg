algoritmo "UniLibrary"
// =============================================================================
// Disciplina : Algoritmo e Programação
// Desafio 1  : Lógica de Programação - Tema 4
// Sistema    : UniLibrary - Sistema de Gerenciamento de Biblioteca Universitária
// Autor      : Vitor de Oliveira
// Ferramenta : VisuAlg 3.0.7
// -----------------------------------------------------------------------------
// OBSERVAÇÕES SOBRE O VISUALG (decisões de projeto):
// 1) O VisuAlg NÃO aceita vetores, matrizes nem registros como parâmetros de
//    procedimentos/funções (dá erro "tipo de dados não reconhecido"). Por isso
//    o acervo, o vetor auxiliar ordenado, a matriz e o vetor de nomes são
//    GLOBAIS. As sub-rotinas recebem por parâmetro aquilo que o VisuAlg permite:
//    quantidades, posições, códigos, categorias, textos e limites de validação.
// 2) No VisuAlg o comando "retorne" NÃO interrompe a função: a execução continua
//    até o "fimfuncao". Por isso cada função guarda o resultado em uma variável
//    local e executa um único "retorne" no final.
// 3) A comparação de textos no VisuAlg diferencia maiúsculas de minúsculas, por
//    isso o desempate por título usa maiusc() nos dois lados.
// 4) Palavras como "copia", "inicio", "pos" são reservadas/funções do VisuAlg e
//    não podem ser usadas como nomes de variáveis.
// =============================================================================

const
   // ---- Capacidade e limites do sistema ----
   MAX_LIVROS = 40
   MAX_CATEGORIAS = 5
   MAX_EXEMPLARES = 99        // limite superior de exemplares por título
   ANO_MINIMO = 1450          // invenção da prensa de Gutenberg
   ANO_MAXIMO = 2026          // ano atual: não existe livro publicado no futuro

   // ---- Categorias (linhas da matriz de movimentações) ----
   TECNOLOGIA = 1
   EXATAS = 2
   HUMANAS = 3
   NEGOCIOS = 4
   LITERATURA = 5

   // ---- Status do livro ----
   DISPONIVEL = 1
   INDISPONIVEL = 0

   // ---- Tipos de movimentação (colunas da matriz) ----
   EMPRESTIMO = 1
   DEVOLUCAO = 2

   // ---- Valores especiais ----
   NAO_ENCONTRADO = -1        // retorno das buscas quando o código não existe
   CANCELAR = 0               // código digitado para desistir de uma operação
   OPCAO_SAIR = 10            // opção do menu que encerra o sistema

   // ---- Larguras das colunas nas tabelas ----
   LARG_TITULO = 23
   LARG_AUTOR = 15
   LARG_CATEGORIA = 26

tipo
   // Registro que agrupa todas as informações de um livro
   Livro = registro
      codigo: inteiro
      titulo: caractere
      autor: caractere
      ano: inteiro
      categoria: inteiro
      qtdTotal: inteiro
      qtdDisponivel: inteiro
      qtdEmprestimos: inteiro
      status: inteiro
   fimregistro

var
   // ---------------------------- VARIÁVEIS GLOBAIS ----------------------------
   // São globais apenas as estruturas compartilhadas por várias sub-rotinas e
   // que o VisuAlg não permite passar por parâmetro.
   acervo: vetor[1..MAX_LIVROS] de Livro         // vetor de registros principal
   vetOrdenado: vetor[1..MAX_LIVROS] de Livro    // cópia de trabalho (ranking e busca binária)
   movimentacoes: vetor[1..MAX_CATEGORIAS, 1..2] de inteiro   // categoria x tipo de operação
   nomesCategorias: vetor[1..MAX_CATEGORIAS] de caractere     // vetor simples com os nomes
   qtdLivros: inteiro                            // posições utilizadas do acervo
   opcao: inteiro                                // opção escolhida no menu

// =============================================================================
//                     SUB-ROTINAS DE APOIO (UTILITÁRIAS)
// =============================================================================

// Inicializa as estruturas globais. "quantidade" é passada por REFERÊNCIA (var)
// porque o procedimento precisa zerar a variável original do programa principal.
procedimento inicializarEstruturas(var quantidade: inteiro)
var
   lin, col: inteiro
inicio
   quantidade <- 0
   // Zera a matriz de movimentações com repetições aninhadas
   para lin de 1 ate MAX_CATEGORIAS faca
      para col de EMPRESTIMO ate DEVOLUCAO faca
         movimentacoes[lin, col] <- 0
      fimpara
   fimpara
   nomesCategorias[TECNOLOGIA] <- "Tecnologia"
   nomesCategorias[EXATAS] <- "Ciências Exatas"
   nomesCategorias[HUMANAS] <- "Ciências Humanas"
   nomesCategorias[NEGOCIOS] <- "Administração e Negócios"
   nomesCategorias[LITERATURA] <- "Literatura"
fimprocedimento

// Espera o usuário pressionar ENTER (dá tempo de ler a saída antes do menu)
procedimento pausar
var
   teclaEnter: caractere
inicio
   escreval("")
   escreva("Pressione ENTER para voltar ao menu...")
   leia(teclaEnter)
fimprocedimento

// Ajusta um texto a uma largura fixa (corta se for maior, completa com espaços
// se for menor). Usada para alinhar as colunas das tabelas.
funcao ajustarTexto(texto: caractere; largura: inteiro): caractere
var
   saida: caractere
inicio
   saida <- texto
   se compr(saida) > largura entao
      saida <- copia(saida, 1, largura)
   fimse
   enquanto compr(saida) < largura faca
      saida <- saida + " "
   fimenquanto
   retorne saida
fimfuncao

// Devolve o nome de uma categoria a partir do seu número
funcao nomeCategoria(categoria: inteiro): caractere
var
   nome: caractere
inicio
   se (categoria < 1) ou (categoria > MAX_CATEGORIAS) entao
      nome <- "Inexistente"
   senao
      nome <- nomesCategorias[categoria]
   fimse
   retorne nome
fimfuncao

// Converte o status numérico em texto
funcao textoStatus(codStatus: inteiro): caractere
var
   texto: caractere
inicio
   se codStatus = DISPONIVEL entao
      texto <- "DISPONÍVEL"
   senao
      texto <- "INDISPONÍVEL"
   fimse
   retorne texto
fimfuncao

// Verifica se o acervo está vazio. Se estiver, já avisa o usuário.
// Recebe a quantidade por VALOR: apenas consulta, não altera.
funcao acervoVazio(quantidade: inteiro): logico
var
   vazio: logico
inicio
   vazio <- quantidade = 0
   se vazio entao
      escreval("")
      escreval(">> O acervo está vazio. Cadastre pelo menos um livro (opção 1).")
   fimse
   retorne vazio
fimfuncao

// Lê um número inteiro e só aceita valores dentro de [minimo, maximo].
// Enquanto o valor for inválido, mostra a mensagem de erro e pede de novo
// (o usuário corrige sem sair do cadastro).
// "valor" é passado por REFERÊNCIA (var) porque é o resultado da leitura.
procedimento lerInteiroValidado(pergunta, msgErro: caractere; minimo, maximo: inteiro; var valor: inteiro)
var
   valido: logico
inicio
   repita
      escreva(pergunta)
      leia(valor)
      valido <- (valor >= minimo) e (valor <= maximo)
      se nao valido entao
         escreval("   ERRO: ", msgErro, " (permitido de ", minimo, " a ", maximo, "). Tente novamente.")
      fimse
   ate valido
fimprocedimento

// Lê um texto obrigatório (não aceita vazio). "texto" é passado por referência.
procedimento lerTextoObrigatorio(pergunta: caractere; var texto: caractere)
inicio
   repita
      escreva(pergunta)
      leia(texto)
      se texto = "" entao
         escreval("   ERRO: este campo não pode ficar em branco. Tente novamente.")
      fimse
   ate texto <> ""
fimprocedimento

// =============================================================================
//                         BUSCA E OPERAÇÕES SOBRE O LIVRO
// =============================================================================

// FUNÇÃO DE CONSULTA: busca sequencial pelo código no acervo.
// Parâmetros (por valor): o código procurado e a quantidade de posições válidas.
// Retorna a posição do livro no vetor ou NAO_ENCONTRADO.
funcao buscarPosicaoPorCodigo(codigoBuscado, quantidade: inteiro): inteiro
var
   i, posicao: inteiro
   encontrado: logico
inicio
   posicao <- NAO_ENCONTRADO
   encontrado <- falso
   i <- 1
   enquanto (i <= quantidade) e (nao encontrado) faca
      se acervo[i].codigo = codigoBuscado entao
         posicao <- i
         encontrado <- verdadeiro
      fimse
      i <- i + 1
   fimenquanto
   retorne posicao
fimfuncao

// Quantidade de exemplares que estão emprestados neste momento:
// qtdEmprestada = qtdTotal - qtdDisponivel
funcao calcularQtdEmprestada(posicao: inteiro): inteiro
inicio
   retorne acervo[posicao].qtdTotal - acervo[posicao].qtdDisponivel
fimfuncao

// Atualiza o status do livro de acordo com a quantidade disponível
procedimento atualizarStatus(posicao: inteiro)
inicio
   se acervo[posicao].qtdDisponivel > 0 entao
      acervo[posicao].status <- DISPONIVEL
   senao
      acervo[posicao].status <- INDISPONIVEL
   fimse
fimprocedimento

// Registra uma operação na matriz: linha = categoria, coluna = tipo de operação
procedimento registrarMovimentacao(categoria, tipoOperacao: inteiro)
inicio
   movimentacoes[categoria, tipoOperacao] <- movimentacoes[categoria, tipoOperacao] + 1
fimprocedimento

// Pede um código até que ele exista no acervo ou até o usuário digitar 0.
// "posicao" volta por REFERÊNCIA com a posição encontrada (ou NAO_ENCONTRADO
// se o usuário cancelou).
procedimento solicitarLivroExistente(quantidade: inteiro; var posicao: inteiro)
var
   codigo: inteiro
inicio
   repita
      escreva("Informe o código do livro (0 para cancelar): ")
      leia(codigo)
      posicao <- NAO_ENCONTRADO
      se codigo <> CANCELAR entao
         posicao <- buscarPosicaoPorCodigo(codigo, quantidade)
         se posicao = NAO_ENCONTRADO entao
            escreval("   ERRO: código ", codigo, " inexistente no acervo. Tente novamente.")
         fimse
      senao
         escreval("   Operação cancelada.")
      fimse
   ate (posicao <> NAO_ENCONTRADO) ou (codigo = CANCELAR)
fimprocedimento

// Exibe a ficha completa de um livro.
// Como o VisuAlg não aceita registro como parâmetro, o procedimento recebe a
// POSIÇÃO e um indicador lógico dizendo de qual vetor ler (acervo principal
// ou vetor ordenado). O registro é copiado para uma variável LOCAL "livroAux".
procedimento exibirFichaLivro(posicao: inteiro; doVetorOrdenado: logico)
var
   livroAux: Livro
inicio
   se doVetorOrdenado entao
      livroAux <- vetOrdenado[posicao]
   senao
      livroAux <- acervo[posicao]
   fimse
   escreval("----------------------------------------------------")
   escreval(" Código ................: ", livroAux.codigo)
   escreval(" Título ................: ", livroAux.titulo)
   escreval(" Autor .................: ", livroAux.autor)
   escreval(" Ano de publicação .....: ", livroAux.ano)
   escreval(" Categoria .............: ", livroAux.categoria, " - ", nomeCategoria(livroAux.categoria))
   escreval(" Exemplares (total) ....: ", livroAux.qtdTotal)
   escreval(" Exemplares disponíveis : ", livroAux.qtdDisponivel)
   escreval(" Exemplares emprestados : ", livroAux.qtdTotal - livroAux.qtdDisponivel)
   escreval(" Empréstimos realizados : ", livroAux.qtdEmprestimos)
   escreval(" Status ................: ", textoStatus(livroAux.status))
   escreval("----------------------------------------------------")
fimprocedimento

// Cabeçalho e linha da tabela de listagem do acervo
procedimento exibirCabecalhoListagem
inicio
   escreval("CÓDIGO | ", ajustarTexto("TÍTULO", LARG_TITULO), " | ", ajustarTexto("AUTOR", LARG_AUTOR), " | ANO  | CAT | TOTAL | DISP | STATUS")
   escreval("-----------------------------------------------------------------------------------------")
fimprocedimento

procedimento exibirLinhaLivro(posicao: inteiro)
inicio
   escreval(acervo[posicao].codigo:6, " | ", ajustarTexto(acervo[posicao].titulo, LARG_TITULO), " | ", ajustarTexto(acervo[posicao].autor, LARG_AUTOR), " | ", acervo[posicao].ano:4, " | ", acervo[posicao].categoria:3, " | ", acervo[posicao].qtdTotal:5, " | ", acervo[posicao].qtdDisponivel:4, " | ", textoStatus(acervo[posicao].status))
fimprocedimento

// =============================================================================
//                       OPÇÕES DO MENU (UMA SUB-ROTINA CADA)
// =============================================================================

// Lê um código novo: precisa ser positivo e ainda não pode existir no acervo.
// "codigo" volta por REFERÊNCIA; "quantidade" entra por VALOR (limite da busca).
procedimento lerCodigoUnico(quantidade: inteiro; var codigo: inteiro)
var
   valido: logico
inicio
   repita
      escreva("Código do livro (número inteiro positivo): ")
      leia(codigo)
      valido <- verdadeiro
      se codigo <= 0 entao
         escreval("   ERRO: o código deve ser maior que zero. Tente novamente.")
         valido <- falso
      senao
         se buscarPosicaoPorCodigo(codigo, quantidade) <> NAO_ENCONTRADO entao
            escreval("   ERRO: já existe um livro com o código ", codigo, ". Informe outro código.")
            valido <- falso
         fimse
      fimse
   ate valido
fimprocedimento

// OPÇÃO 1 - Cadastro de livro.
// "quantidade" é passada por REFERÊNCIA (var), pois o cadastro aumenta a
// quantidade de livros do programa principal.
procedimento cadastrarLivro(var quantidade: inteiro)
var
   novaPosicao, codigo, ano, categoria, qtdExemplares, c: inteiro
   titulo, autor: caractere
inicio
   escreval("")
   escreval("=========== CADASTRO DE LIVRO ===========")
   se quantidade >= MAX_LIVROS entao
      escreval(">> Capacidade máxima atingida (", MAX_LIVROS, " livros). Não é possível cadastrar.")
   senao
      lerCodigoUnico(quantidade, codigo)
      lerTextoObrigatorio("Título: ", titulo)
      lerTextoObrigatorio("Autor: ", autor)
      lerInteiroValidado("Ano de publicação: ", "ano inválido", ANO_MINIMO, ANO_MAXIMO, ano)
      escreval("Categorias:")
      para c de 1 ate MAX_CATEGORIAS faca
         escreval("   ", c, " - ", nomesCategorias[c])
      fimpara
      lerInteiroValidado("Categoria: ", "categoria inexistente", 1, MAX_CATEGORIAS, categoria)
      lerInteiroValidado("Quantidade de exemplares: ", "quantidade inválida", 1, MAX_EXEMPLARES, qtdExemplares)

      // Todos os dados são válidos: grava o registro na próxima posição livre
      novaPosicao <- quantidade + 1
      acervo[novaPosicao].codigo <- codigo
      acervo[novaPosicao].titulo <- titulo
      acervo[novaPosicao].autor <- autor
      acervo[novaPosicao].ano <- ano
      acervo[novaPosicao].categoria <- categoria
      acervo[novaPosicao].qtdTotal <- qtdExemplares
      acervo[novaPosicao].qtdDisponivel <- qtdExemplares
      acervo[novaPosicao].qtdEmprestimos <- 0
      acervo[novaPosicao].status <- DISPONIVEL
      quantidade <- novaPosicao
      escreval(">> Livro cadastrado com sucesso! (", quantidade, " de ", MAX_LIVROS, " posições usadas)")
   fimse
fimprocedimento

// OPÇÃO 2 - Lista todo o acervo
procedimento listarAcervo(quantidade: inteiro)
var
   i: inteiro
inicio
   escreval("")
   escreval("=========== ACERVO COMPLETO ===========")
   se nao acervoVazio(quantidade) entao
      exibirCabecalhoListagem
      para i de 1 ate quantidade faca
         exibirLinhaLivro(i)
      fimpara
      escreval("Total de livros cadastrados: ", quantidade)
   fimse
fimprocedimento

// OPÇÃO 3 - Consulta um livro pelo código
procedimento consultarLivro(quantidade: inteiro)
var
   posicao: inteiro
inicio
   escreval("")
   escreval("=========== CONSULTA DE LIVRO ===========")
   se nao acervoVazio(quantidade) entao
      solicitarLivroExistente(quantidade, posicao)
      se posicao <> NAO_ENCONTRADO entao
         escreval("Livro encontrado na posição ", posicao, " do acervo:")
         exibirFichaLivro(posicao, falso)
      fimse
   fimse
fimprocedimento

// OPÇÃO 4 - Empréstimo de um exemplar
procedimento realizarEmprestimo(quantidade: inteiro)
var
   posicao: inteiro
   livroExiste, podeEmprestar: logico
inicio
   escreval("")
   escreval("=========== EMPRÉSTIMO ===========")
   se nao acervoVazio(quantidade) entao
      solicitarLivroExistente(quantidade, posicao)
      livroExiste <- posicao <> NAO_ENCONTRADO
      se livroExiste entao
         podeEmprestar <- (acervo[posicao].qtdDisponivel > 0) e (acervo[posicao].status = DISPONIVEL)
         se podeEmprestar entao
            acervo[posicao].qtdDisponivel <- acervo[posicao].qtdDisponivel - 1
            acervo[posicao].qtdEmprestimos <- acervo[posicao].qtdEmprestimos + 1
            atualizarStatus(posicao)
            registrarMovimentacao(acervo[posicao].categoria, EMPRESTIMO)
            escreval(">> Empréstimo realizado: ", acervo[posicao].titulo)
            escreval("   Disponíveis agora: ", acervo[posicao].qtdDisponivel, " de ", acervo[posicao].qtdTotal)
            se acervo[posicao].status = INDISPONIVEL entao
               escreval("   Atenção: último exemplar emprestado. Status: ", textoStatus(acervo[posicao].status))
            fimse
         senao
            escreval(">> ERRO: não há exemplares disponíveis de '", acervo[posicao].titulo, "'.")
            escreval("   Status: ", textoStatus(acervo[posicao].status), " - todos os ", acervo[posicao].qtdTotal, " exemplares estão emprestados.")
         fimse
      fimse
   fimse
fimprocedimento

// OPÇÃO 5 - Devolução de um exemplar
procedimento realizarDevolucao(quantidade: inteiro)
var
   posicao, qtdEmprestada: inteiro
inicio
   escreval("")
   escreval("=========== DEVOLUÇÃO ===========")
   se nao acervoVazio(quantidade) entao
      solicitarLivroExistente(quantidade, posicao)
      se posicao <> NAO_ENCONTRADO entao
         qtdEmprestada <- calcularQtdEmprestada(posicao)
         // Só pode devolver se existe exemplar emprestado E se a devolução não
         // fizer a quantidade disponível ultrapassar a quantidade total
         se (qtdEmprestada > 0) e (acervo[posicao].qtdDisponivel + 1 <= acervo[posicao].qtdTotal) entao
            acervo[posicao].qtdDisponivel <- acervo[posicao].qtdDisponivel + 1
            atualizarStatus(posicao)
            registrarMovimentacao(acervo[posicao].categoria, DEVOLUCAO)
            escreval(">> Devolução registrada: ", acervo[posicao].titulo)
            escreval("   Disponíveis agora: ", acervo[posicao].qtdDisponivel, " de ", acervo[posicao].qtdTotal, " - Status: ", textoStatus(acervo[posicao].status))
         senao
            escreval(">> ERRO: nenhum exemplar de '", acervo[posicao].titulo, "' está emprestado.")
            escreval("   Todos os ", acervo[posicao].qtdTotal, " exemplares já estão na biblioteca (disponível = total).")
         fimse
      fimse
   fimse
fimprocedimento

// OPÇÃO 6 - Lista somente os livros com exemplares disponíveis
procedimento exibirDisponiveis(quantidade: inteiro)
var
   i, contador: inteiro
inicio
   escreval("")
   escreval("=========== LIVROS DISPONÍVEIS ===========")
   se nao acervoVazio(quantidade) entao
      contador <- 0
      exibirCabecalhoListagem
      para i de 1 ate quantidade faca
         se acervo[i].status = DISPONIVEL entao
            exibirLinhaLivro(i)
            contador <- contador + 1
         fimse
      fimpara
      se contador = 0 entao
         escreval("Nenhum livro disponível no momento: todos os exemplares estão emprestados.")
      senao
         escreval("Livros disponíveis: ", contador, " de ", quantidade)
      fimse
   fimse
fimprocedimento

// =============================================================================
//                    ORDENAÇÃO (RANKING) E BUSCA RECURSIVA
// =============================================================================

// Copia o acervo para o vetor auxiliar. As ordenações trabalham na CÓPIA para
// não bagunçar a ordem de cadastro do acervo principal.
procedimento copiarAcervo(quantidade: inteiro)
var
   i: inteiro
inicio
   para i de 1 ate quantidade faca
      vetOrdenado[i] <- acervo[i]      // copia o registro inteiro
   fimpara
fimprocedimento

// Troca dois registros COMPLETOS de lugar no vetor ordenado (todos os campos
// continuam juntos). Usa um registro LOCAL como auxiliar.
procedimento trocarRegistros(i, j: inteiro)
var
   aux: Livro
inicio
   aux <- vetOrdenado[i]
   vetOrdenado[i] <- vetOrdenado[j]
   vetOrdenado[j] <- aux
fimprocedimento

// Critério do ranking: devolve VERDADEIRO se o livro da posição "a" deve ficar
// ANTES do livro da posição "b".
//   1º) mais empréstimos primeiro;
//   2º) empate -> menos exemplares disponíveis primeiro;
//   3º) empate -> título em ordem alfabética.
funcao vemAntesNoRanking(a, b: inteiro): logico
var
   antes: logico
inicio
   se vetOrdenado[a].qtdEmprestimos <> vetOrdenado[b].qtdEmprestimos entao
      antes <- vetOrdenado[a].qtdEmprestimos > vetOrdenado[b].qtdEmprestimos
   senao
      se vetOrdenado[a].qtdDisponivel <> vetOrdenado[b].qtdDisponivel entao
         antes <- vetOrdenado[a].qtdDisponivel < vetOrdenado[b].qtdDisponivel
      senao
         antes <- maiusc(vetOrdenado[a].titulo) < maiusc(vetOrdenado[b].titulo)
      fimse
   fimse
   retorne antes
fimfuncao

// BUBBLE SORT com critérios múltiplos. A cada passada, o livro "mais fraco"
// afunda para o fim. Se uma passada inteira não fizer trocas, o vetor já está
// ordenado e o laço termina antes (otimização com a variável houveTroca).
procedimento ordenarRanking(quantidade: inteiro)
var
   passada, j: inteiro
   houveTroca: logico
inicio
   passada <- 1
   repita
      houveTroca <- falso
      para j de 1 ate quantidade - passada faca
         se vemAntesNoRanking(j + 1, j) entao
            trocarRegistros(j, j + 1)
            houveTroca <- verdadeiro
         fimse
      fimpara
      passada <- passada + 1
   ate (nao houveTroca) ou (passada >= quantidade)
fimprocedimento

// OPÇÃO 7 - Ranking do acervo
procedimento exibirRanking(quantidade: inteiro)
var
   i: inteiro
inicio
   escreval("")
   escreval("=========== RANKING DO ACERVO ===========")
   se nao acervoVazio(quantidade) entao
      copiarAcervo(quantidade)
      ordenarRanking(quantidade)
      escreval("Critérios: 1) mais empréstimos  2) menos disponíveis  3) título (A-Z)")
      escreval("")
      escreval("POSIÇÃO | ", ajustarTexto("LIVRO", LARG_TITULO), " | ", ajustarTexto("AUTOR", LARG_AUTOR), " | EMPRÉSTIMOS | DISPONÍVEIS")
      escreval("-------------------------------------------------------------------------------")
      para i de 1 ate quantidade faca
         escreval(i:6, "º | ", ajustarTexto(vetOrdenado[i].titulo, LARG_TITULO), " | ", ajustarTexto(vetOrdenado[i].autor, LARG_AUTOR), " | ", vetOrdenado[i].qtdEmprestimos:11, " | ", vetOrdenado[i].qtdDisponivel:11)
      fimpara
      escreval("(A ordem de cadastro do acervo principal não foi alterada.)")
   fimse
fimprocedimento

// SELECTION SORT por código (crescente) no vetor auxiliar. É pré-requisito da
// busca binária, que só funciona em vetor ordenado.
procedimento ordenarPorCodigo(quantidade: inteiro)
var
   i, j, posMenor: inteiro
inicio
   para i de 1 ate quantidade - 1 faca
      posMenor <- i
      para j de i + 1 ate quantidade faca
         se vetOrdenado[j].codigo < vetOrdenado[posMenor].codigo entao
            posMenor <- j
         fimse
      fimpara
      se posMenor <> i entao
         trocarRegistros(i, posMenor)
      fimse
   fimpara
fimprocedimento

// BUSCA BINÁRIA RECURSIVA no vetor ordenado por código.
// Parâmetros (por valor): código procurado e o intervalo [posInicio..posFim].
// Casos-base:
//   1) posInicio > posFim  -> intervalo vazio: o código não existe.
//   2) código do meio = código procurado -> encontrado, retorna a posição.
// Caso recursivo: chama a si mesma com a METADE onde o código pode estar
// (o intervalo diminui a cada chamada, então a recursão sempre termina).
funcao buscaBinariaRecursiva(codigoBuscado, posInicio, posFim: inteiro): inteiro
var
   meio, posEncontrada: inteiro
inicio
   se posInicio > posFim entao
      escreval("   inicio (", posInicio, ") > fim (", posFim, "): não há mais posições para pesquisar.")
      posEncontrada <- NAO_ENCONTRADO
   senao
      meio <- (posInicio + posFim) div 2
      escreval("   Intervalo [", posInicio, " .. ", posFim, "]  meio = ", meio, "  código no meio = ", vetOrdenado[meio].codigo)
      se vetOrdenado[meio].codigo = codigoBuscado entao
         posEncontrada <- meio
      senao
         se codigoBuscado < vetOrdenado[meio].codigo entao
            escreval("      ", codigoBuscado, " < ", vetOrdenado[meio].codigo, " -> procurar na metade INFERIOR")
            posEncontrada <- buscaBinariaRecursiva(codigoBuscado, posInicio, meio - 1)
         senao
            escreval("      ", codigoBuscado, " > ", vetOrdenado[meio].codigo, " -> procurar na metade SUPERIOR")
            posEncontrada <- buscaBinariaRecursiva(codigoBuscado, meio + 1, posFim)
         fimse
      fimse
   fimse
   retorne posEncontrada
fimfuncao

// OPÇÃO 9 - Busca recursiva por código
procedimento realizarBuscaRecursiva(quantidade: inteiro)
var
   i, codigo, posicao: inteiro
inicio
   escreval("")
   escreval("=========== BUSCA RECURSIVA (BINÁRIA) ===========")
   se nao acervoVazio(quantidade) entao
      copiarAcervo(quantidade)
      ordenarPorCodigo(quantidade)
      escreva("Códigos ordenados: ")
      para i de 1 ate quantidade faca
         escreva(vetOrdenado[i].codigo, " ")
      fimpara
      escreval("")
      escreva("Informe o código a ser pesquisado: ")
      leia(codigo)
      escreval("Passos da busca:")
      posicao <- buscaBinariaRecursiva(codigo, 1, quantidade)
      se posicao = NAO_ENCONTRADO entao
         escreval(">> Código ", codigo, " NÃO encontrado no catálogo.")
      senao
         escreval(">> Código ", codigo, " encontrado na posição ", posicao, " do vetor ordenado por código:")
         exibirFichaLivro(posicao, verdadeiro)
      fimse
   fimse
fimprocedimento

// =============================================================================
//                       ESTATÍSTICAS E PROCESSAMENTO DA MATRIZ
// =============================================================================

// Percorre TODA a matriz de movimentações com repetições aninhadas,
// mostra a tabela categoria x operação e calcula os totais.
procedimento processarMatriz
var
   lin, col, totalLinha, totalGeral: inteiro
   totalColuna: vetor[1..2] de inteiro
inicio
   totalGeral <- 0
   totalColuna[EMPRESTIMO] <- 0
   totalColuna[DEVOLUCAO] <- 0
   escreval("")
   escreval("----------- MATRIZ DE MOVIMENTAÇÕES -----------")
   escreval(ajustarTexto("CATEGORIA", LARG_CATEGORIA), " EMPRÉSTIMOS  DEVOLUÇÕES   TOTAL")
   para lin de 1 ate MAX_CATEGORIAS faca
      totalLinha <- 0
      escreva(ajustarTexto(nomesCategorias[lin], LARG_CATEGORIA))
      para col de EMPRESTIMO ate DEVOLUCAO faca
         escreva(movimentacoes[lin, col]:12)
         totalLinha <- totalLinha + movimentacoes[lin, col]
         totalColuna[col] <- totalColuna[col] + movimentacoes[lin, col]
      fimpara
      escreval(totalLinha:8)
      totalGeral <- totalGeral + totalLinha
   fimpara
   escreval(ajustarTexto("TOTAL", LARG_CATEGORIA), totalColuna[EMPRESTIMO]:12, totalColuna[DEVOLUCAO]:12, totalGeral:8)
   escreval("Total de movimentações armazenadas na matriz: ", totalGeral)
fimprocedimento

// OPÇÃO 8 - Estatísticas gerais (usa contadores e acumuladores)
procedimento exibirEstatisticas(quantidade: inteiro)
var
   i, c: inteiro
   totalExemplares, totalDisponiveis, totalEmprestados: inteiro
   totalEmprestimos, totalDevolucoes: inteiro
   posMaisEmprestado, posMaisDisponivel, categoriaTop: inteiro
   empatados: caractere
   percDisponiveis, percEmprestados, mediaExemplares: real
   livrosPorCategoria: vetor[1..MAX_CATEGORIAS] de inteiro
inicio
   escreval("")
   escreval("=========== ESTATÍSTICAS GERAIS ===========")
   se nao acervoVazio(quantidade) entao
      // ---- zera contadores e acumuladores ----
      totalExemplares <- 0
      totalDisponiveis <- 0
      totalEmprestimos <- 0
      totalDevolucoes <- 0
      posMaisEmprestado <- 1
      posMaisDisponivel <- 1
      para c de 1 ate MAX_CATEGORIAS faca
         livrosPorCategoria[c] <- 0
      fimpara

      // ---- percorre o acervo acumulando ----
      para i de 1 ate quantidade faca
         totalExemplares <- totalExemplares + acervo[i].qtdTotal
         totalDisponiveis <- totalDisponiveis + acervo[i].qtdDisponivel
         totalEmprestimos <- totalEmprestimos + acervo[i].qtdEmprestimos
         livrosPorCategoria[acervo[i].categoria] <- livrosPorCategoria[acervo[i].categoria] + 1
         se acervo[i].qtdEmprestimos > acervo[posMaisEmprestado].qtdEmprestimos entao
            posMaisEmprestado <- i
         fimse
         se acervo[i].qtdDisponivel > acervo[posMaisDisponivel].qtdDisponivel entao
            posMaisDisponivel <- i
         fimse
      fimpara
      totalEmprestados <- totalExemplares - totalDisponiveis

      // ---- devoluções e categoria com mais empréstimos (vêm da matriz) ----
      categoriaTop <- 1
      para c de 1 ate MAX_CATEGORIAS faca
         totalDevolucoes <- totalDevolucoes + movimentacoes[c, DEVOLUCAO]
         se movimentacoes[c, EMPRESTIMO] > movimentacoes[categoriaTop, EMPRESTIMO] entao
            categoriaTop <- c
         fimse
      fimpara

      // ---- cálculos com real (totalExemplares > 0, pois cada livro tem 1 ou mais) ----
      percDisponiveis <- (totalDisponiveis / totalExemplares) * 100
      percEmprestados <- (totalEmprestados / totalExemplares) * 100
      mediaExemplares <- totalExemplares / quantidade

      // ---- saída ----
      escreval("Livros cadastrados ...................: ", quantidade)
      escreval("Total de exemplares ..................: ", totalExemplares)
      escreval("Exemplares disponíveis ...............: ", totalDisponiveis)
      escreval("Exemplares emprestados no momento ....: ", totalEmprestados)
      escreval("Total de empréstimos realizados ......: ", totalEmprestimos)
      escreval("Total de devoluções ..................: ", totalDevolucoes)
      escreval("Percentual de exemplares disponíveis .: ", percDisponiveis:6:2, " %")
      escreval("Percentual de exemplares emprestados .: ", percEmprestados:6:2, " %")
      escreval("Média de exemplares por livro ........: ", mediaExemplares:6:2)
      se acervo[posMaisEmprestado].qtdEmprestimos > 0 entao
         // Monta a lista de TODOS os livros empatados no maior número de empréstimos
         empatados <- ""
         para i de 1 ate quantidade faca
            se acervo[i].qtdEmprestimos = acervo[posMaisEmprestado].qtdEmprestimos entao
               se empatados <> "" entao
                  empatados <- empatados + " / "
               fimse
               empatados <- empatados + acervo[i].titulo
            fimse
         fimpara
         escreval("Livro com mais empréstimos ...........: ", empatados, " (", acervo[posMaisEmprestado].qtdEmprestimos, " empréstimos)")
      senao
         escreval("Livro com mais empréstimos ...........: nenhum empréstimo realizado ainda")
      fimse
      empatados <- ""
      para i de 1 ate quantidade faca
         se acervo[i].qtdDisponivel = acervo[posMaisDisponivel].qtdDisponivel entao
            se empatados <> "" entao
               empatados <- empatados + " / "
            fimse
            empatados <- empatados + acervo[i].titulo
         fimse
      fimpara
      escreval("Livro com mais exemplares disponíveis : ", empatados, " (", acervo[posMaisDisponivel].qtdDisponivel, " disponíveis)")
      escreval("")
      escreval(ajustarTexto("CATEGORIA", LARG_CATEGORIA), " LIVROS  EMPRÉSTIMOS  DEVOLUÇÕES")
      para c de 1 ate MAX_CATEGORIAS faca
         escreval(ajustarTexto(nomesCategorias[c], LARG_CATEGORIA), livrosPorCategoria[c]:7, movimentacoes[c, EMPRESTIMO]:13, movimentacoes[c, DEVOLUCAO]:12)
      fimpara
      se movimentacoes[categoriaTop, EMPRESTIMO] > 0 entao
         empatados <- ""
         para c de 1 ate MAX_CATEGORIAS faca
            se movimentacoes[c, EMPRESTIMO] = movimentacoes[categoriaTop, EMPRESTIMO] entao
               se empatados <> "" entao
                  empatados <- empatados + " / "
               fimse
               empatados <- empatados + nomesCategorias[c]
            fimse
         fimpara
         escreval("Categoria com mais empréstimos .......: ", empatados, " (", movimentacoes[categoriaTop, EMPRESTIMO], " empréstimos)")
      senao
         escreval("Categoria com mais empréstimos .......: nenhum empréstimo realizado ainda")
      fimse
      // Obs.: havendo empate, todos os empatados são listados, separados por " / ".

      processarMatriz
   fimse
fimprocedimento

// =============================================================================
//                                   MENU
// =============================================================================
procedimento exibirMenu
inicio
   escreval("")
   escreval("==========================================================")
   escreval("   UNILIBRARY - SISTEMA DE GERENCIAMENTO DE BIBLIOTECA")
   escreval("==========================================================")
   escreval("  1. Cadastrar livro")
   escreval("  2. Listar acervo")
   escreval("  3. Consultar livro")
   escreval("  4. Realizar empréstimo")
   escreval("  5. Realizar devolução")
   escreval("  6. Exibir livros disponíveis")
   escreval("  7. Exibir ranking do acervo")
   escreval("  8. Exibir estatísticas")
   escreval("  9. Realizar busca recursiva")
   escreval(" 10. Encerrar sistema")
   escreval("----------------------------------------------------------")
   escreva("Escolha uma opção: ")
fimprocedimento

// =============================================================================
//                            PROGRAMA PRINCIPAL
// =============================================================================
inicio
   inicializarEstruturas(qtdLivros)
   repita
      exibirMenu
      leia(opcao)
      escolha opcao
      caso 1
         cadastrarLivro(qtdLivros)
      caso 2
         listarAcervo(qtdLivros)
      caso 3
         consultarLivro(qtdLivros)
      caso 4
         realizarEmprestimo(qtdLivros)
      caso 5
         realizarDevolucao(qtdLivros)
      caso 6
         exibirDisponiveis(qtdLivros)
      caso 7
         exibirRanking(qtdLivros)
      caso 8
         exibirEstatisticas(qtdLivros)
      caso 9
         realizarBuscaRecursiva(qtdLivros)
      caso 10
         escreval("")
         escreval("Encerrando o UniLibrary... Até logo!")
      outrocaso
         escreval("")
         escreval(">> Opção inválida! Digite um número de 1 a ", OPCAO_SAIR, ".")
      fimescolha
      se opcao <> OPCAO_SAIR entao
         pausar
      fimse
   ate opcao = OPCAO_SAIR
fimalgoritmo
