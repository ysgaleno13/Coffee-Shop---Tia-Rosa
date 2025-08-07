# COFFEE.SHOPS.TIA.ROSA.py

# Importações que a gente sempre usa, do Python mesmo
import json
from datetime import datetime
import os # Pra ver se os arquivos de dados existem
from collections import Counter # Pra contar as coisas no histórico do cliente
import random # Para escolher frases aleatórias


try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # Se a pessoa não tiver o colorama o sistema pode rodar sem cor.
    print("Aviso: A biblioteca 'colorama' não foi encontrada. As cores no terminal não serão exibidas.")
    class NoColor: # Uma classe fictícia pra não dar erro se não tiver colorama
        def __getattr__(self, name):
            return ''
    Fore = NoColor()
    Style = NoColor()


# --- Classes: O Coração da Cafeteria ---
# Aqui consigo organizar as informações principais, como se fossem fichas.

class ItemCardapio:
    """
    Representa um alimento ou bebida do nosso cardápio da Tia Rosa.
    Registra o nome, preço, categoria, ingredientes, promoção e o que é mais vendido.
   
    """
    def __init__(self, nome_do_item, preco_do_item, tipo_de_item, ingredientes_do_item=None, promocao=None):
        self.nome = nome_do_item
        self.preco = preco_do_item
        self.categoria = tipo_de_item # Ex: 'bebida', 'salgado', 'doce'
        self.ingredientes = ingredientes_do_item if ingredientes_do_item is not None else [] # Uma lista, tipo ['café', 'leite']
        self.promocao = promocao # Pode ser uma string tipo "Leve 2 pague 1" ou None
        self.vezes_vendido = 0 # Começa zerado

class Cliente:
    """
    Representa um cliente fiel da Tia Rosa, com seus dados e os pontos!
    O histórico de pedidos ajuda a gente a lembrar do que ele gosta.
    """
    def __init__(self, nome_completo, email_contato):
        self.nome = nome_completo
        self.email = email_contato
        self.pontos_fidelidade = 0
        self.historico_de_pedidos = [] # Lista dos nomes dos itens que ele já pediu

class Comanda:
    """
    Representa um pedido que acabou de sair do forno ou da máquina de café.
    Liga o cliente aos produtos, registra a hora e o valor total.
    """
    def __init__(self, cliente_que_pediu, itens_da_comanda):
        self.cliente = cliente_que_pediu
        self.itens = itens_da_comanda # Lista de objetos ItemCardapio
        self.hora_do_pedido = datetime.now() # A hora exata que a comanda foi fechada
        self.valor_total = sum(item.preco for item in itens_da_comanda) # Soma o preço de tudo

# --- Histórico de Dados ---
# Essas listas guardam tudo enquanto o sistema tá ligado.
# Depois é só salvar em arquivos pra não perder nada.
cardapio_da_tia_rosa = []
nossos_clientes = []
comandas_do_dia = []

# --- Os Combos Cariocas ---
# Uns combos já prontos, com nomes que são a cara do Rio de Janeiro.
# Importante: os itens desses combos precisam existir no cardápio individualmente!
OS_COMBOS_DA_CIDADE = {
    "Lanche da Lapa": {
        "itens": ["Cappuccino", "Bolo de Cenoura", "Pão de Queijo", "Pão de Queijo"], # Dois pães de queijo
        "promocao": "Aquele lanche que segura o dia!",
        "preco_base": 0 # Será calculado dinamicamente
    },
    
	"Desjejum da Urca": {
        "itens": ["Pingado", "Pão na Chapa ou Pão com Ovo Frito na Manteiga", "Suco Natural da Casa"],
        "promocao": "Simples, direto e com gosto de manhã carioca!",
        "preco_base": 0
    },
    	
	"Café da Manhã Copacabana": {
        "itens": ["Café Preto", "Torradas Artesanais com Requeijão", "Fruta da Estação Cortada na Hora"],
        "promocao": "Pra quem começa o dia com calma e sabor!",
        "preco_base": 0
    },
   
	"Doce da Glória": {
        "itens": ["Salgado ou Fatia de Torta de Limão", "Café Expresso"],
        "promocao": "Pra quem merece um mimo da tarde!",
        "preco_base": 0
    },
   	
	"Expresso da Lapa": {
        "itens": ["Café Expresso", "Pão Francês com Queijo Minas", "Pastel Recheado"],
        "promocao": "Um combo rápido pra quem tem pressa (mas não abre mão do sabor)!",
        "preco_base": 0
    },
    
	"Reforço do Catete": {
        "itens": ["Vitamina de Banana com Aveia", "Misto", "Biscoito de Polvilho ou Bolo da Casa"],
        "promocao": "Pra quem pulou o café da manhã!",
        "preco_base": 0
    }
}

# --- Frases de atendimento ---
FRASES_BOAS_VINDAS = [
    "Seja bem-vindo de volta, {nome}! Pronto pra mais um dia delicioso?",
    "Que prazer te ver de novo, {nome}! Já deixamos seu {item_favorito} pronto.",
    "Já estávamos com saudade de ver seu nome por aqui, {nome}.",
    "E aí, {nome}! Hoje vai de {item_favorito} ou quer experimentar algo novo?",
    "Sinta-se em casa, {nome}! Seu {item_favorito} está no ponto."
]

FRASES_SUGESTAO_REPETIR = [
    "Bom dia, {nome}! Vai repetir o seu {item_favorito} de sempre?",
    "Café da manhã completo, como você gosta, {nome}? Já temos seu {item_favorito}.",
    "E aí! Tudo bem {nome}? Deseja repetir o seu '{item_favorito}' de sempre? (Sim/Não)"
]

FRASES_SUGESTAO_NOVO = [
    "Oi, {nome}! Que tal um {sugestao_nova} pra adoçar sua tarde?",
    "{nome}, sua fidelidade rende. Que tal trocar seus pontos por um mimo hoje?",
    "Você está a três pontos de um café grátis. Quer aproveitar hoje?"
]

FRASES_PONTOS_FIDELIDADE = [
    "Você tem {pontos} pontos, falta só {faltam} para seu café gratuito",
    "Falta pouco pra sua próxima recompensa. Continue acumulando seus pontos.",
    "Você acumulou {pontos} pontos! Parabéns, tem um mimo grátis te esperando."
]


# --- Onde a gente guarda os arquivos (nomes dos arquivos JSON) ---
ARQUIVO_CARDAPIO = 'cardapio.json'
ARQUIVO_CLIENTES = 'clientes.json'
ARQUIVO_COMANDAS = 'comandas.json'

# --- Funções de Guardar e Trazer os Dados (Persistência) ---

def guardar_tudo():
    """
    Salva o cardápio, os clientes e as comandas em arquivos JSON.
    Assim, é possível fechar o sistema e os dados não somem!
    """
    try:
        # Salva o cardápio: transforma cada item em um dicionário
        with open(ARQUIVO_CARDAPIO, 'w', encoding='utf-8') as f:
            json.dump([item.__dict__ for item in cardapio_da_tia_rosa], f, indent=4, ensure_ascii=False)
        
        # Salva os clientes: cada cliente vira um dicionário
        with open(ARQUIVO_CLIENTES, 'w', encoding='utf-8') as f:
            json.dump([cliente.__dict__ for cliente in nossos_clientes], f, indent=4, ensure_ascii=False)
        
        
        # Salva as comandas, só o que é importante pra recriar depois.
        pedidos_para_salvar = []
        for comanda in comandas_do_dia:
            pedidos_para_salvar.append({
                'nome_do_cliente': comanda.cliente.nome,
                'nomes_dos_itens': [item.nome for item in comanda.itens],
                'hora': comanda.hora_do_pedido.isoformat(), # Transforma a data/hora em texto
                'valor_total': comanda.valor_total
            })
        with open(ARQUIVO_COMANDAS, 'w', encoding='utf-8') as f:
            json.dump(pedidos_para_salvar, f, indent=4, ensure_ascii=False)
            
        print(Fore.GREEN + "Dados salvos!")
    except Exception as e:
        print(Fore.RED + f"Eita! Deu problema pra salvar os dados: {e}. Verifique se a pasta tá liberada, por favor.")

def carregar_tudo():
    """
    Traz os dados de volta dos arquivos JSON para as nossas listas em memória.
    Isso acontece assim que o sistema liga, pra continuar de onde parou.
    """
    global cardapio_da_tia_rosa, nossos_clientes, comandas_do_dia
    
    # Tenta carregar o cardápio
    if os.path.exists(ARQUIVO_CARDAPIO):
        try:
            with open(ARQUIVO_CARDAPIO, 'r', encoding='utf-8') as f:
                dados_do_cardapio = json.load(f)
                # Recria os objetos ItemCardapio a partir dos dicionários
                for d in dados_do_cardapio:
                    item = ItemCardapio(d['nome'], d['preco'], d['categoria'], d.get('ingredientes', []), d.get('promocao'))
                    item.vezes_vendido = d.get('vezes_vendido', 0) # Pega o contador, se existir
                    cardapio_da_tia_rosa.append(item)
        except json.JSONDecodeError:
            print(Fore.YELLOW + "Aviso: Arquivo do cardápio vazio ou estragado. Começando com cardápio novinho.")
        except Exception as e:
            print(Fore.RED + f"Erro ao carregar o cardápio: {e}")

    # Tenta carregar os clientes
    if os.path.exists(ARQUIVO_CLIENTES):
        try:
            with open(ARQUIVO_CLIENTES, 'r', encoding='utf-8') as f:
                dados_dos_clientes = json.load(f)
                # Recria os objetos Cliente
                for d in dados_dos_clientes:
                    cliente = Cliente(d['nome'], d['email'])
                    cliente.pontos_fidelidade = d.get('pontos_fidelidade', 0)
                    cliente.historico_de_pedidos = d.get('historico_de_pedidos', [])
                    nossos_clientes.append(cliente)
        except json.JSONDecodeError:
            print(Fore.YELLOW + "Aviso: Arquivo de clientes vazio ou estragado. Começando com clientes novos.")
        except Exception as e:
            print(Fore.RED + f"Erro ao carregar os clientes: {e}")

    # Tenta carregar as comandas (aqui é mais complexo, é preciso achar o cliente e os produtos)
    if os.path.exists(ARQUIVO_COMANDAS):
        try:
            with open(ARQUIVO_COMANDAS, 'r', encoding='utf-8') as f:
                dados_das_comandas = json.load(f)
                for dc in dados_das_comandas:
                    # Acha o cliente pelo nome
                    cliente_recuperado = next((c for c in nossos_clientes if c.nome == dc['nome_do_cliente']), None)
                    itens_recuperados = []
                    # Pra cada nome de item na comanda, tenta achar o objeto no cardápio
                    for nome_item_comanda in dc['nomes_dos_itens']:
                        item_achado = next((p for p in cardapio_da_tia_rosa if p.nome == nome_item_comanda), None)
                        if item_achado:
                            itens_recuperados.append(item_achado)
                        else:
                            print(Fore.YELLOW + f"Aviso: Item '{nome_item_comanda}' de uma comanda antiga não está mais no cardápio.")
                    
                    # Se achou o cliente e pelo menos um item, recria a comanda
                    if cliente_recuperado and itens_recuperados:
                        comanda_obj = Comanda(cliente_recuperado, itens_recuperados)
                        # Coloca a hora original e o valor total de volta
                        comanda_obj.hora_do_pedido = datetime.fromisoformat(dc['hora']) 
                        comanda_obj.valor_total = dc.get('valor_total', sum(p.preco for p in itens_recuperados))
                        comandas_do_dia.append(comanda_obj)
                    else:
                        print(Fore.YELLOW + f"Aviso: Comanda do cliente '{dc['nome_do_cliente']}' não foi totalmente recuperada (cliente ou itens sumiram).")
        except json.JSONDecodeError:
            print(Fore.YELLOW + "Aviso: Arquivo de comandas vazio ou estragado. Começando com comandas zeradas.")
        except Exception as e:
            print(Fore.RED + f"Erro ao carregar as comandas: {e}")

def _popular_cardapio_inicial():
    """
    Popula o cardápio com os itens iniciais se ele estiver vazio.
    Isso garante que sempre teremos algo para vender!
    """
    if not cardapio_da_tia_rosa:
        print(Fore.YELLOW + "Cardápio vazio! Adicionando itens padrão da Tia Rosa...")
        cardapio_da_tia_rosa.append(ItemCardapio("Café Preto", 4.50, "Bebida", ["Café", "Água"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Pingado", 5.00, "Bebida", ["Café", "Leite"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Cappuccino", 8.00, "Bebida", ["Café", "Leite", "Chocolate em pó"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Suco de Laranja", 7.00, "Bebida", ["Laranja"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Suco de Acerola", 7.00, "Bebida", ["Acerola", "Água", "Açúcar"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Pão de Queijo", 3.50, "Salgado", ["Polvilho", "Queijo", "Ovo", "Leite"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Misto", 9.00, "Salgado", ["Pão de forma", "Queijo", "Presunto"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Pão com Ovo", 7.00, "Salgado", ["Pão francês", "Ovo"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Bolo de Cenoura", 10.00, "Doce", ["Cenoura", "Farinha", "Ovo", "Chocolate"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Bolo de Abacaxi", 9.50, "Doce", ["Abacaxi", "Farinha", "Ovo"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Bolo de Chocolate", 10.00, "Doce", ["Chocolate", "Farinha", "Ovo"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Café Expresso", 6.00, "Bebida", ["Café"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Sonho", 7.00, "Doce", ["Coco", "Doce de Leite", "Gema de ovo"]))
        
        # Itens genéricos para combos que podem ter variações
        cardapio_da_tia_rosa.append(ItemCardapio("Pão na Chapa ou Pão com Ovo Frito na Manteiga", 8.00, "Salgado", ["Pão", "Manteiga", "Ovo"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Suco Natural da Casa", 7.50, "Bebida", ["Frutas da estação"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Torradas com Requeijão", 6.00, "Salgado", ["Pão", "Requeijão"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Salada de Frutas", 5.00, "Doce", ["Frutas frescas"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Fatia de Torta de Limão", 8.50, "Doce", ["Bolo no Pote", "Torta de Limão"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Pão Francês com Queijo Minas", 6.50, "Salgado", ["Pão francês", "Queijo Minas"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Pastel", 4.00, "Salgado", ["Massa", "Recheio"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Vitamina Fitness", 9.00, "Bebida", ["Banana", "Aveia", "Leite"]))
        cardapio_da_tia_rosa.append(ItemCardapio("Biscoito ou Bolo da Casa", 5.50, "Doce", ["Biscoito", "Bolo"]))

        # Adicionando algumas promoções aleatórias para teste
        for item in cardapio_da_tia_rosa:
            if random.random() < 0.3: # 30% de chance de ter promoção
                item.promocao = random.choice(["Leve 2 Pague 1", "50% OFF", "Brinde Surpresa"])

        guardar_tudo() # Salva esses itens iniciais
        print(Fore.GREEN + "Cardápio padrão da Tia Rosa carregado!")

    # Calcula o preço base dos combos
    for nome_combo, dados_combo in OS_COMBOS_DA_CIDADE.items():
        preco_calculado = 0.0
        for item_nome in dados_combo["itens"]:
            item_obj = _achar_item_por_nome(item_nome)
            if item_obj:
                preco_calculado += item_obj.preco
            else:
                # Se um item do combo não existe, o sistema avisa e não calcula o preço
                print(Fore.YELLOW + f"Aviso: Item '{item_nome}' do combo '{nome_combo}' não encontrado no cardápio. Preço do combo pode estar incorreto.")
                preco_calculado = 0.0 # Zera pra não dar preço errado
                break
        OS_COMBOS_DA_CIDADE[nome_combo]["preco_base"] = preco_calculado


# --- Funções do Cardápio ---

def incluir_item_no_cardapio():
    """
    Deixa adicionar um novo item ao cardápio da cafeteria.
    Pede o nome, ingredientes, preço e categoria.
    """
    print(Fore.BLUE + "\n--- BOTA MAIS UM SABOR NO CARDÁPIO! ---")
    nome = input("Qual o nome do novo item? ").strip().title()
    if not nome:
        print(Fore.RED + "Ops! O nome não pode ficar vazio. Tenta de novo.")
        return
    
    # Vê se já não tem um item com esse nome, pra não bagunçar
    if any(item.nome == nome for item in cardapio_da_tia_rosa):
        print(Fore.RED + f"Ih, já tem '{nome}' no cardápio! Vê se não é pra editar o existente.")
        return

    while True: # Pra ter certeza que o preço é um número e não é negativo
        try:
            preco_str = input("Qual o preço? (Ex: 12.50): R$ ").replace(',', '.') # Aceita vírgula ou ponto
            preco = float(preco_str)
            if preco < 0:
                print(Fore.RED + "Preço negativo. Tente de novo.")
                continue
            break # Se deu certo, sai do loop
        except ValueError:
            print(Fore.RED + "Preço inválido. Digita um número, tipo 7.50.")

    categoria = input("Qual a categoria? (Ex: 'bebida', 'salgado', 'doce'): ").strip().lower()
    if not categoria:
        print(Fore.YELLOW + "Aviso: Não informou a categoria. Fica mais organizado com ela!")

    ingredientes_str = input("Quais os ingredientes? (Separa por vírgula, tipo: 'açúcar, leite' - Opcional): ")
    ingredientes = [ing.strip().capitalize() for ing in ingredientes_str.split(',') if ing.strip()]
    
    promocao = input("Tem alguma promoção pra esse item? (Deixe em branco se não tiver): ").strip()
    if not promocao:
        promocao = None

    novo_item = ItemCardapio(nome, preco, categoria, ingredientes, promocao)
    cardapio_da_tia_rosa.append(novo_item)
    guardar_tudo() # Salva pra não perder o item novo
    print(Fore.GREEN + f"'{nome}' adicionado ao cardápio com sucesso! Que delícia!")

def mostrar_cardapio():
    """
    Mostra todos os itens que temos no cardápio e organizado por categoria.
    Ajustado para alinhar as colunas e colorir promoções.
    """
    print(Fore.CYAN + "\n--- CARDÁPIO DA COFFEE SHOPS TIA ROSA (Sabor do Rio!) ---")
    if not cardapio_da_tia_rosa:
        print(Fore.YELLOW + "Nosso cardápio tá vazio! Que tal adicionar algo?")
        return

    categorias = sorted(list(set(item.categoria for item in cardapio_da_tia_rosa)))

    # Definindo larguras fixas para as colunas para alinhamento
    LARGURA_ID = 4
    LARGURA_NOME = 40
    LARGURA_PRECO = 10
    LARGURA_PROMOCAO = 25
    LARGURA_INGREDIENTES = 40 # Pode ser ajustado conforme a necessidade

    for categoria in categorias:
        print(Fore.BLUE + f"\n--- {categoria.upper()} ---")
        print(Fore.BLUE + f"{'ID':<{LARGURA_ID}} | {'Nome do Item':<{LARGURA_NOME}} | {'Preço':<{LARGURA_PRECO}} | {'Promoção':<{LARGURA_PROMOCAO}} | {'Ingredientes':<{LARGURA_INGREDIENTES}}")
        print(Fore.BLUE + "-" * (LARGURA_ID + LARGURA_NOME + LARGURA_PRECO + LARGURA_PROMOCAO + LARGURA_INGREDIENTES + 5 * 3)) # 5 barras e 3 espaços entre colunas

        itens_da_categoria = [item for item in cardapio_da_tia_rosa if item.categoria == categoria]
        for i, item in enumerate(itens_da_categoria):
            ingr = ', '.join(item.ingredientes) if item.ingredientes else "Não informado"
            
            promo_texto = item.promocao if item.promocao else "N/A"
            
            # Aplica cor verde para promoções, branco normal para N/A
            if item.promocao:
                promo_exibicao = Fore.GREEN + promo_texto + Style.RESET_ALL
            else:
                promo_exibicao = promo_texto
            
            # Truncar strings se forem muito longas para caber na coluna
            nome_exibicao = (item.nome[:LARGURA_NOME-3] + '...') if len(item.nome) > LARGURA_NOME else item.nome

            # Uma forma simples é preencher com espaços e depois adicionar a cor.
            promo_formatada = f"{promo_exibicao:<{LARGURA_PROMOCAO + len(Fore.GREEN) + len(Style.RESET_ALL) if item.promocao else LARGURA_PROMOCAO}}"
            
            ingr_exibicao = (ingr[:LARGURA_INGREDIENTES-3] + '...') if len(ingr) > LARGURA_INGREDIENTES else ingr

            print(f"{i+1:<{LARGURA_ID}} | {nome_exibicao:<{LARGURA_NOME}} | R$ {item.preco:<{LARGURA_PRECO-3}.2f} | {promo_formatada} | {ingr_exibicao:<{LARGURA_INGREDIENTES}}")
    print(Fore.CYAN + "-" * (LARGURA_ID + LARGURA_NOME + LARGURA_PRECO + LARGURA_PROMOCAO + LARGURA_INGREDIENTES + 5 * 3))

# --- Funções dos Clientes ---

def cadastrar_cliente():
    """
    Permite cadastrar um novo cliente no nosso programa de fidelidade.
    Pede nome e e-mail. Os pontos começam do zero.
    """
    print(Fore.BLUE + "\n--- VEM FAZER PARTE DA FAMÍLIA TIA ROSA! ---")
    nome = input("Qual o nome completo do cliente? ").strip().title()
    if not nome:
        print(Fore.RED + "Nome vazio. Tente de novo.")
        return None # Retorna None para indicar que o cadastro falhou
    
    # Vê se o cliente já não tá cadastrado
    cliente_existente = next((c for c in nossos_clientes if c.nome == nome), None)
    if cliente_existente:
        print(Fore.RED + f"Ih, o cliente '{nome}' já tá na nossa lista! Que tal fazer um pedido?")
        return cliente_existente # Retorna o cliente existente
        
    email = input("Qual o e-mail do cliente? ").strip().lower()
    # Uma checagem simples pro e-mail
    if "@" not in email or "." not in email:
        print(Fore.YELLOW + "Aviso: Esse e-mail parece meio estranho. Confere se tá certinho (ex: email@exemplo.com).")

    novo_cliente = Cliente(nome, email)
    nossos_clientes.append(novo_cliente)
    guardar_tudo() # Salva o novo cliente
    print(Fore.GREEN + f"Cliente '{nome}' cadastrado com sucesso! Já pode começar a juntar pontos!")
    return novo_cliente # Retorna o novo cliente cadastrado

def mostrar_clientes():
    """
    Mostra a lista de todos os nossos clientes cadastrados, com e-mail e pontos.
    """
    print(Fore.CYAN + "\n--- NOSSOS CLIENTES QUERIDOS! ---")
    if not nossos_clientes:
        print(Fore.YELLOW + "Nenhum cliente cadastrado ainda.")
        return

    # Cabeçalho pra organizar
    print(Fore.BLUE + f"{'ID':<4} | {'Nome do Cliente':<25} | {'E-mail':<30} | {'Pontos':<7}")
    print(Fore.BLUE + "-" * 70) # Linha separadora

    for i, cliente in enumerate(nossos_clientes):
        print(f"{i+1:<4} | {cliente.nome:<25} | {cliente.email:<30} | {cliente.pontos_fidelidade:<7}")
    print(Fore.CYAN + "-------------------------------------------------------------------")

# --- Funções de Pedidos (Comandas) ---

def _achar_item_por_nome(nome_do_item):
    """
    Função interna pra achar um item no cardápio pelo nome, sem se importar com maiúsculas/minúsculas.
    Retorna o objeto ItemCardapio se achar, senão, retorna nada (None).
    """
    return next((item for item in cardapio_da_tia_rosa if item.nome.lower() == nome_do_item.strip().lower()), None)

def _finalizar_comanda_e_pontos(cliente, itens_selecionados):
    """
    Função interna pra fechar a comanda: registra, calcula os pontos,
    atualiza o histórico do cliente e vê se ele já ganhou algo.
    """
    if not itens_selecionados:
        print(Fore.RED + "Epa! Nenhum item válido foi selecionado para a comanda.")
        return False

    nova_comanda = Comanda(cliente, itens_selecionados)
    comandas_do_dia.append(nova_comanda)
    
    # Pontos de fidelidade: 3 pontos a cada R$10 gastos.
    pontos_ganhos = int(nova_comanda.valor_total // 10) * 3
    cliente.pontos_fidelidade += pontos_ganhos
    
    # Atualiza o histórico do cliente e o contador de vendas dos itens
    for item in itens_selecionados:
        cliente.historico_de_pedidos.append(item.nome)
        item.vezes_vendido += 1

    guardar_tudo() # Salva tudo depois da comanda fechada

    print(Fore.GREEN + f"\nComanda saindo para o(a) {cliente.nome}!")
    print(Fore.GREEN + f"Itens: {', '.join([item.nome for item in itens_selecionados])} | Total: R$ {nova_comanda.valor_total:.2f}")
    print(Fore.GREEN + "Pedido feito!") # Texto de confirmação
    
    # Mensagem personalizada dos pontos
    if pontos_ganhos > 0:
        print(Fore.GREEN + f"Que beleza! Você ganhou {pontos_ganhos} ponto(s) de fidelidade! Agora você tem {cliente.pontos_fidelidade} pontos no total.")
    
    _verificar_recompensa_fidelidade(cliente) # Vê se o cliente já pode pegar um mimo grátis
    return True

def _verificar_recompensa_fidelidade(cliente):
    """
    Vê se o cliente tem pontos suficientes (20 pontos) pra ganhar um café grátis
    e pergunta se ele quer resgatar.
    """
    if cliente.pontos_fidelidade >= 20:
        print(Fore.MAGENTA + f"\nEita, {cliente.nome}! Você já tem {cliente.pontos_fidelidade} pontos e pode resgatar um café preto grátis!")
        resposta = input("Deseja resgatar seu café grátis agora? (Sim/Não): ").strip().lower()
        if resposta == 'sim':
            # Tenta achar o "Café Preto" no cardápio pra dar de graça
            cafe_gratis = _achar_item_por_nome("Café Preto") 
            if cafe_gratis:
                # Cria uma comanda de recompensa com valor zero
                comanda_recompensa = Comanda(cliente, [cafe_gratis])
                comanda_recompensa.valor_total = 0.0 
                comandas_do_dia.append(comanda_recompensa)
                cliente.pontos_fidelidade -= 20 # Tira os pontos usados
                guardar_tudo()
                print(Fore.GREEN + "Parabénsss! Seu Café Preto grátis foi resgatado! Seus pontos foram atualizados.")
            else:
                print(Fore.RED + "Ops! 'Café Preto' não encontrado no cardápio pra resgate. Vê se ele tá cadastrado.")
        else:
            print(Fore.YELLOW + "Tranquilo! Você pode resgatar seu café grátis em outro momento. Seus pontos continuam guardados!")
    elif cliente.pontos_fidelidade > 0:
        faltam_pontos = 20 - cliente.pontos_fidelidade
        frase_pontos = random.choice(FRASES_PONTOS_FIDELIDADE).format(pontos=cliente.pontos_fidelidade, faltam=faltam_pontos)
        print(Fore.MAGENTA + f"\n{frase_pontos}")


def fazer_pedido(cliente_atual=None): # Adicionado cliente_atual para o fluxo guiado
    """
    Guia o usuário pra fazer uma nova comanda.
    Tem a opção de "pedido expresso" pra quem é de casa e a escolha de itens ou combos.
    """
    print(Fore.BLUE + "\n--- VAMOS MONTAR SEU PEDIDO! ---")
    
    cliente = cliente_atual # Usa o cliente passado, se houver
    if not cliente: # Se não foi passado, pede o nome
        nome_cliente = input("Qual o nome do cliente? ").strip().title()
        cliente = next((c for c in nossos_clientes if c.nome == nome_cliente), None)
    
    if not cliente:
        print(Fore.RED + "Cliente não encontrado! Por favor, realize o cadastro na opção 3 do menu.")
        return

    # --- Boas-vindas e Sugestão Personalizada ---
    item_favorito = "seu pedido de sempre"
    if cliente.historico_de_pedidos:
        contagem_historico = Counter(cliente.historico_de_pedidos)
        if contagem_historico:
            item_favorito = contagem_historico.most_common(1)[0][0]
            
            # Frase de boas-vindas personalizada
            frase_boas_vindas = random.choice(FRASES_BOAS_VINDAS).format(nome=cliente.nome.split()[0], item_favorito=item_favorito)
            print(Fore.MAGENTA + f"\n{frase_boas_vindas}")

            # Sugestão de repetir o pedido favorito
            frase_sugestao = random.choice(FRASES_SUGESTAO_REPETIR).format(nome=cliente.nome.split()[0], item_favorito=item_favorito)
            print(Fore.MAGENTA + f"\n{frase_sugestao}")
            resposta = input().strip().lower()
            
            if resposta == 'sim':
                # Tenta montar o pedido expresso
                itens_do_expresso = []
                if item_favorito in OS_COMBOS_DA_CIDADE:
                    for nome_item_combo in OS_COMBOS_DA_CIDADE[item_favorito]["itens"]:
                        item_do_combo = _achar_item_por_nome(nome_item_combo)
                        if item_do_combo:
                            itens_do_expresso.append(item_do_combo)
                        else:
                            print(Fore.YELLOW + f"Aviso: Item '{nome_item_combo}' do combo '{item_favorito}' não encontrado. Não foi possível montar o pedido expresso.")
                            itens_do_expresso = [] # Limpa pra não processar errado
                            break
                else:
                    item_individual = _achar_item_por_nome(item_favorito)
                    if item_individual:
                        itens_do_expresso.append(item_individual)
                    else:
                        print(Fore.YELLOW + f"Aviso: Item '{item_favorito}' não encontrado. Não foi possível montar o pedido expresso.")
                
                if itens_do_expresso:
                    _finalizar_comanda_e_pontos(cliente, itens_do_expresso)
                    return # Acabou a função, a comanda já foi feita.
                else:
                    print(Fore.YELLOW + "Não foi possível montar o pedido expresso. Vamos para o cardápio completo.")
            else:
                print(Fore.YELLOW + "Beleza, sem problemas! Vamos para o cardápio completo.")
    else:
        print(Fore.MAGENTA + f"\nOlá, {cliente.nome.split()[0]}! Que bom te ver por aqui pela primeira vez!")


    mostrar_cardapio() # Mostra o cardápio completo pra escolher.

    if not cardapio_da_tia_rosa:
        print(Fore.YELLOW + "Aviso: Não temos itens no cardápio pra fazer uma comanda. Adiciona uns primeiro!")
        return

    # Mostra os combos cariocas disponíveis
    print(Fore.YELLOW + "\n--- Combos Especiais do Dia (Sabor do Rio de Janeiro!) ---")
    if not OS_COMBOS_DA_CIDADE:
        print(Fore.YELLOW + "Nenhum combo especial definido ainda.")
    else:
        for nome_combo, dados_combo in OS_COMBOS_DA_CIDADE.items():
            print(f"- {nome_combo}: {dados_combo['promocao']}")
            print(f"  Itens: {', '.join(dados_combo['itens'])}")
            print(f"  Preço: R$ {dados_combo['preco_base']:.2f}")
    print(Fore.CYAN + "----------------------------------------------------")

    # Pede os itens da comanda (pode ser item individual ou combo)
    escolha_itens_str = input("Quais itens ou combos você quer? (Separa por vírgula): ").split(',')
    
    itens_pra_comanda = []
    
    for item_escolhido in escolha_itens_str:
        item_limpo = item_escolhido.strip().title()

        # Vê se é um dos nossos combos cariocas
        if item_limpo in OS_COMBOS_DA_CIDADE:
            print(Fore.CYAN + f"Adicionando combo: {item_limpo}")
            for nome_item_combo in OS_COMBOS_DA_CIDADE[item_limpo]["itens"]:
                item_do_combo = _achar_item_por_nome(nome_item_combo)
                if item_do_combo:
                    itens_pra_comanda.append(item_do_combo)
                else:
                    print(Fore.YELLOW + f"Aviso: O item '{nome_item_combo}' do combo '{item_limpo}' não foi encontrado no cardápio e foi ignorado.")
        else: # Se não for combo, tenta achar como item individual
            item_encontrado = _achar_item_por_nome(item_limpo)
            if item_encontrado:
                itens_pra_comanda.append(item_encontrado)
            else:
                print(Fore.YELLOW + f"Aviso: O item '{item_limpo}' não foi encontrado no cardápio nem como combo e foi ignorado.")
    
    _finalizar_comanda_e_pontos(cliente, itens_pra_comanda)


def ver_relatorio_do_dia():
    """
    Mostra um relatório detalhado de todas as comandas do dia.
    Inclui quem pediu, o que pediu, a hora e o valor.
    No final, um resumo das vendas e os itens mais pedidos.
    """
    print(Fore.CYAN + "\n--- RELATÓRIO DE VENDAS DO DIA (Tia Rosa Agradece!) ---")
    if not comandas_do_dia:
        print(Fore.YELLOW + "Nenhuma comanda registrada ainda.")
        return
    
    total_arrecadado_geral = 0.0
    
    for i, comanda in enumerate(comandas_do_dia):
        nomes_dos_itens = [item.nome for item in comanda.itens]
        total_da_comanda = comanda.valor_total
        total_arrecadado_geral += total_da_comanda

        print(f"Comanda {i+1} - Horário: {comanda.hora_do_pedido.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"  Cliente: {comanda.cliente.nome} (Pontos: {comanda.cliente.pontos_fidelidade})")
        print(f"  Itens: {', '.join(nomes_dos_itens)}")
        print(f"  Valor Total: R$ {total_da_comanda:.2f}")
        print(Fore.CYAN + "------------------------------------------------------------------")
    
    print(Fore.BLUE + f"\n--- RESUMO DO MOVIMENTO DO DIA ---")
    print(Fore.BLUE + f"Total de Comandas: {len(comandas_do_dia)}")
    print(Fore.BLUE + f"Valor Total Arrecadado: R$ {total_arrecadado_geral:.2f}")
    
    # Os itens que mais saíram!
    print(Fore.MAGENTA + "\n--- OS QUERIDINHOS DO CARDÁPIO (Mais Vendidos) ---")
    if not cardapio_da_tia_rosa:
        print(Fore.YELLOW + "Nenhum item no cardápio pra analisar as vendas.")
        return
    
    # Ordena os itens pelo número de vezes que foram vendidos
    itens_ordenados = sorted(cardapio_da_tia_rosa, key=lambda item: item.vezes_vendido, reverse=True)
    
    if any(item.vezes_vendido > 0 for item in itens_ordenados):
        for item in itens_ordenados:
            if item.vezes_vendido > 0: # Mostra só o que vendeu
                print(f"- {item.nome}: {item.vezes_vendido} vez(es) vendida(s)")
    else:
        print(Fore.YELLOW + "Nenhum item foi vendido ainda pra fazer esse ranking. Que tal começar?")
    print(Fore.CYAN + "--------------------------------------------")


# --- O Menu Principal ---

def iniciar_cafeteria():
    """
    Essa é a função que liga o sistema da cafeteria.
    Ela carrega os dados, mostra o menu e deixa a gente escolher o que fazer.
    """
    carregar_tudo() # Tenta trazer os dados antigos assim que o sistema liga.
    _popular_cardapio_inicial() # Garante que o cardápio tenha itens padrão

    while True:
        print(Fore.BLUE + "\n" + "="*60)
        print(Fore.LIGHTGREEN_EX + "========== BEM-VINDO(A) AO COFFEE SHOPS TIA ROSA! ==========")
        print(Fore.BLUE + "="*60)
        print(Fore.YELLOW + "--- O QUE VAMOS PEDIR HOJE? ---")
        print("1. Adicionar um item novo ao Cardápio")
        print("2. Ver Nosso Cardápio Completo")
        print("3. Cadastrar um Cliente Novo")
        print("4. Ver a Lista de Clientes")
        print("5. Fazer o Pedido")
        print("6. Relatório de Vendas do Dia")
        print("0. Fechar a Cafeteria por Hoje")
        print("=============================================================")

        escolha = input("Escolha uma opção (digite o número e Enter): ").strip()
        
        if escolha == '1':
            incluir_item_no_cardapio()
        elif escolha == '2':
            mostrar_cardapio()
        elif escolha == '3':
            cliente_recem_cadastrado = cadastrar_cliente()
            if cliente_recem_cadastrado:
                print(Fore.CYAN + "\n--- Agora vamos ver o cardápio para o seu pedido! ---")
                mostrar_cardapio()
                print(Fore.CYAN + "\n--- E agora, vamos fazer o seu pedido! ---")
                fazer_pedido(cliente_recem_cadastrado)
        elif escolha == '4':
            mostrar_clientes()
        elif escolha == '5':
            fazer_pedido()
        elif escolha == '6':
            ver_relatorio_do_dia()
        elif escolha == '0':
            print(Fore.BLUE + "Até mais! O Coffee Shops Tia Rosa agradece sua visita!")
            guardar_tudo() # Salva tudo antes de desligar, pra não perder nada.
            break
        else:
            print(Fore.RED + "Opção inválida, meu caro! Digita um número de 0 a 6, por favor.")

# --- Ponto de Entrada do Programa ---
# Esse pedaço só roda quando você executa o arquivo diretamente.
if __name__ == "__main__":
    # E agora, vamos abrir a cafeteria!
    iniciar_cafeteria()

