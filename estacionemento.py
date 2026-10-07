"""
PAGUEPARE PARKING
Sistema de estacionamento com interface gráfica (Tkinter).

- 20 vagas (1-10 à esquerda, 11-20 à direita)
- Entrada e saída de veículos com cálculo do valor
- Validação de placa (modelo antigo ABC-1234 e Mercosul ABC1D23)
- Todo texto digitado vira MAIÚSCULO automaticamente
- Dados salvos em vagas.json

Regra de cobrança:
- Quem entra já paga o primeiro bloco (R$ 2,50), mesmo ficando poucos minutos.
- Cada bloco de 15 minutos custa R$ 2,50 (R$ 10,00 por hora).
- A tolerância de 5 minutos vale para o que passar de um bloco completo:
  1h00 = R$ 10,00 | 1h05 = R$ 10,00 (tolerância) | 1h11 = R$ 12,50
"""

# =============================================================================
# 1. IMPORTAÇÕES
# =============================================================================
import json
import re
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

# =============================================================================
# 2. CONFIGURAÇÕES (valores e cores - altere aqui para ajustar o sistema)
# =============================================================================
NOME_ESTACIONAMENTO = "PARKING PAGUEPARE"
TOTAL_VAGAS = 20
VALOR_BLOCO = 2.50        # R$ por bloco de 15 minutos (equivale a R$ 10,00/hora)
MINUTOS_BLOCO = 15        # duração de cada bloco
TOLERANCIA_MIN = 5       # minutos de tolerância sobre um bloco completo
ARQUIVO_DADOS = Path(__file__).with_name("vagas.json")  # onde os dados ficam salvos

# Cores do sistema
AZUL = "#0B2A6F"
AMARELO = "#FFC400"
VERDE = "#2E9E4F"
VERMELHO = "#C62828"
ASFALTO = "#3A3A3A"
FUNDO = "#E8EEF9"

# Placa antiga (ABC-1234 / ABC1234) ou Mercosul (ABC1D23)
REGEX_PLACA = re.compile(r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$")


# =============================================================================
# 3. FUNÇÕES AUXILIARES (regras de negócio, sem interface)
# =============================================================================
def normalizar_placa(texto: str) -> str:
    """Remove espaços e hífen e deixa em maiúsculo: 'abc-1234' -> 'ABC1234'."""
    return re.sub(r"[\s-]", "", texto).upper()


def placa_valida(texto: str) -> bool:
    """Confere se a placa está no formato antigo ou Mercosul."""
    return bool(REGEX_PLACA.match(normalizar_placa(texto)))


def formatar_placa(placa: str) -> str:
    """Exibição: ABC1234 -> ABC-1234 (modelo antigo). Mercosul fica como está."""
    if placa[4].isdigit():
        return f"{placa[:3]}-{placa[3:]}"
    return placa


def calcular_valor(minutos: float) -> float:
    """
    Calcula o valor a pagar.
    - Mínimo de 1 bloco (R$ 2,50), cobrado já na entrada.
    - Cada bloco de 15 min completo é cobrado.
    - Se sobrar tempo além dos blocos completos, só cobra mais um bloco
      quando o excedente passar da tolerância (5 min).
    """
    blocos_completos = int(minutos // MINUTOS_BLOCO)
    excedente = minutos - blocos_completos * MINUTOS_BLOCO

    blocos = blocos_completos
    if excedente > TOLERANCIA_MIN:
        blocos += 1

    blocos = max(blocos, 1)  # quem entra paga no mínimo o primeiro bloco
    return blocos * VALOR_BLOCO


def moeda(valor: float) -> str:
    """Formata em reais: 2.5 -> 'R$ 2,50'."""
    return f"R$ {valor:.2f}".replace(".", ",")


def formatar_duracao(minutos: float) -> str:
    """Formata minutos como '1h 05min'."""
    total = int(minutos)
    return f"{total // 60}h {total % 60:02d}min"


# =============================================================================
# 4. PERSISTÊNCIA (salvar e carregar os dados em arquivo JSON)
# =============================================================================
def carregar_vagas() -> dict:
    """Lê o arquivo vagas.json. Se não existir ou estiver corrompido, começa vazio."""
    if ARQUIVO_DADOS.exists():
        try:
            return json.loads(ARQUIVO_DADOS.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def salvar_vagas(vagas: dict) -> None:
    """Grava as vagas ocupadas no arquivo vagas.json."""
    ARQUIVO_DADOS.write_text(
        json.dumps(vagas, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# =============================================================================
# 5. CAMPO DE TEXTO SEMPRE MAIÚSCULO
# =============================================================================
def criar_entry_maiusculo(pai, **opcoes) -> tk.Entry:
    """
    Cria um campo de texto que transforma tudo o que o usuário digita em
    MAIÚSCULO, na hora, preservando a posição do cursor.
    """
    var = tk.StringVar()
    entry = tk.Entry(pai, textvariable=var, **opcoes)

    def converter(*_):
        texto = var.get()
        if texto != texto.upper():
            posicao = entry.index("insert")
            var.set(texto.upper())
            entry.icursor(posicao)

    var.trace_add("write", converter)
    return entry


# =============================================================================
# 6. JANELA DE ENTRADA DE VEÍCULO
# =============================================================================
class DialogoEntrada(tk.Toplevel):
    def __init__(self, app, vaga_inicial=None):
        super().__init__(app.root)
        self.app = app
        self.title("Dar entrada")
        self.configure(bg=FUNDO, padx=20, pady=15)
        self.resizable(False, False)
        self.transient(app.root)
        self.grab_set()  # trava a janela principal enquanto esta estiver aberta

        tk.Label(self, text="ENTRADA DE VEÍCULO", bg=FUNDO, fg=AZUL,
                 font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # --- Campos do formulário (todos em maiúsculo) ---
        self.campos = {}
        for i, rotulo in enumerate(["NOME", "PLACA DO VEÍCULO", "VAGA (1-20)", "MODELO DO VEÍCULO"], start=1):
            tk.Label(self, text=rotulo, bg=FUNDO, fg=AZUL,
                     font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", pady=4)
            entry = criar_entry_maiusculo(self, font=("Segoe UI", 11), width=24)
            entry.grid(row=i, column=1, pady=4, padx=(10, 0))
            self.campos[rotulo] = entry

        # Se o usuário clicou numa vaga livre, já vem preenchida
        if vaga_inicial:
            self.campos["VAGA (1-20)"].insert(0, str(vaga_inicial))

        # Aviso do valor de entrada
        tk.Label(self, text=f"Valor de entrada: {moeda(VALOR_BLOCO)}", bg=FUNDO, fg=VERDE,
                 font=("Segoe UI", 10, "bold")).grid(row=5, column=0, columnspan=2, pady=(8, 0))

        # --- Botões ---
        botoes = tk.Frame(self, bg=FUNDO)
        botoes.grid(row=6, column=0, columnspan=2, pady=(12, 0))
        tk.Button(botoes, text="CONFIRMAR", bg=VERDE, fg="white", width=12,
                  font=("Segoe UI", 10, "bold"), command=self.confirmar).pack(side="left", padx=5)
        tk.Button(botoes, text="CANCELAR", bg=VERMELHO, fg="white", width=12,
                  font=("Segoe UI", 10, "bold"), command=self.destroy).pack(side="left", padx=5)

        self.campos["NOME"].focus_set()
        self.bind("<Return>", lambda _: self.confirmar())

    def erro_no_campo(self, rotulo, titulo, mensagem):
        """Mostra o aviso e leva o cursor direto para o campo com problema."""
        messagebox.showwarning(titulo, mensagem, parent=self)
        campo = self.campos[rotulo]
        campo.focus_set()
        campo.select_range(0, tk.END)

    def confirmar(self):
        """Valida campo por campo (na ordem da tela) e registra a entrada."""
        nome = self.campos["NOME"].get().strip()
        placa = normalizar_placa(self.campos["PLACA DO VEÍCULO"].get())
        vaga_txt = self.campos["VAGA (1-20)"].get().strip()
        modelo = self.campos["MODELO DO VEÍCULO"].get().strip()

        # --- Validação do nome ---
        if len(nome) < 2:
            return self.erro_no_campo("NOME", "Nome inválido", "Informe o nome do cliente.")

        # --- Validação da placa ---
        if not placa:
            return self.erro_no_campo("PLACA DO VEÍCULO", "Placa vazia", "Informe a placa do veículo.")
        if not placa_valida(placa):
            return self.erro_no_campo(
                "PLACA DO VEÍCULO", "Placa inválida",
                "Digite uma placa válida.\nExemplos: ABC-1234 ou ABC1D23.")
        for v, dados in self.app.vagas.items():
            if dados["placa"] == placa:
                return self.erro_no_campo(
                    "PLACA DO VEÍCULO", "Veículo já estacionado",
                    f"A placa {formatar_placa(placa)} já está na vaga {v}.")

        # --- Validação da vaga ---
        if not vaga_txt:
            return self.erro_no_campo("VAGA (1-20)", "Vaga vazia", "Informe o número da vaga.")
        if not vaga_txt.isdigit() or not 1 <= int(vaga_txt) <= TOTAL_VAGAS:
            return self.erro_no_campo(
                "VAGA (1-20)", "Vaga inválida", f"Escolha uma vaga entre 1 e {TOTAL_VAGAS}.")
        vaga = str(int(vaga_txt))  # "05" vira "5"
        if vaga in self.app.vagas:
            return self.erro_no_campo(
                "VAGA (1-20)", "Vaga ocupada", f"A vaga {vaga} está ocupada! Escolha outra.")

        # --- Validação do modelo ---
        if not modelo:
            return self.erro_no_campo("MODELO DO VEÍCULO", "Modelo vazio", "Informe o modelo do veículo.")

        # --- Tudo certo: registra a entrada ---
        self.app.vagas[vaga] = {
            "nome": nome,
            "placa": placa,
            "modelo": modelo,
            "entrada": datetime.now().isoformat(timespec="seconds"),
        }
        salvar_vagas(self.app.vagas)
        self.app.atualizar_vagas()
        messagebox.showinfo(
            "ENTRADA REGISTRADA",
            f"{nome}\n{formatar_placa(placa)} - {modelo}\nVAGA {vaga}\n\n"
            f"Valor de entrada: {moeda(VALOR_BLOCO)}", parent=self)
        self.destroy()


# =============================================================================
# 7. APLICAÇÃO PRINCIPAL
# =============================================================================
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.vagas = carregar_vagas()   # {"3": {nome, placa, modelo, entrada}, ...}
        self.labels_vagas = {}          # guarda o quadrado visual de cada vaga

        root.title(NOME_ESTACIONAMENTO)
        root.configure(bg=FUNDO)
        root.resizable(False, False)

        # Monta a tela de cima para baixo
        self.criar_cabecalho()
        corpo = tk.Frame(root, bg=FUNDO)
        corpo.pack(padx=15, pady=15)
        self.criar_menu(corpo)
        self.criar_estacionamento(corpo)
        self.criar_rodape()
        self.atualizar_vagas()

    # -------------------------------------------------------------------------
    # 7.1 MONTAGEM DA INTERFACE
    # -------------------------------------------------------------------------
    def criar_cabecalho(self):
        """Faixa azul com o nome do estacionamento e linha amarela embaixo."""
        topo = tk.Frame(self.root, bg=AZUL)
        topo.pack(fill="x")
        tk.Label(topo, text="🅿  " + NOME_ESTACIONAMENTO, bg=AZUL, fg=AMARELO,
                 font=("Segoe UI", 24, "bold"), pady=10).pack()
        tk.Frame(self.root, bg=AMARELO, height=5).pack(fill="x")

    def criar_menu(self, pai):
        """Menu lateral azul com os botões de ação e a legenda de cores."""
        menu = tk.Frame(pai, bg=AZUL, padx=12, pady=12)
        menu.grid(row=0, column=0, sticky="ns", padx=(0, 15))

        tk.Label(menu, text="MENU", bg=AZUL, fg=AMARELO,
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

        # (chave, texto do botão, função chamada ao clicar)
        opcoes = [
            ("entrada", "➕  DAR ENTRADA", lambda: DialogoEntrada(self)),
            ("saida", "🚗  DAR SAÍDA", self.dar_saida),
            ("extrato", "🧾  EXTRATO / A RECEBER", self.mostrar_extrato),
            ("listar", "📋  VEÍCULOS ESTACIONADOS", self.listar_veiculos),
            ("precos", "💰  TABELA DE PREÇOS", self.mostrar_precos),
            ("sair", "❌  SAIR", self.root.destroy),
        ]
        self.botoes_menu = {}  # guarda cada botão para podermos esconder/mostrar
        for chave, texto, comando in opcoes:
            botao = tk.Button(menu, text=texto, command=comando, width=26, anchor="w",
                              bg=AMARELO, fg=AZUL, activebackground="#FFD54F",
                              font=("Segoe UI", 11, "bold"), relief="flat", pady=6,
                              cursor="hand2")
            botao.pack(pady=4)
            self.botoes_menu[chave] = botao

        # Aviso que aparece no lugar do botão "Dar entrada" quando está lotado
        self.aviso_lotado = tk.Label(menu, text="⛔  ESTACIONAMENTO LOTADO", width=26,
                                     bg=VERMELHO, fg="white", pady=10,
                                     font=("Segoe UI", 11, "bold"))
        self.entrada_visivel = True  # controla se o botão "Dar entrada" está na tela

        # Legenda de cores das vagas
        legenda = tk.Frame(menu, bg=AZUL)
        legenda.pack(pady=(20, 0), anchor="w")
        for cor, txt in [(VERDE, "VAGA LIVRE"), (VERMELHO, "VAGA OCUPADA")]:
            linha = tk.Frame(legenda, bg=AZUL)
            linha.pack(anchor="w", pady=2)
            tk.Label(linha, bg=cor, width=2).pack(side="left")
            tk.Label(linha, text=" " + txt, bg=AZUL, fg="white",
                     font=("Segoe UI", 10)).pack(side="left")

    def criar_estacionamento(self, pai):
        """Desenha o estacionamento: vagas 1-10 à esquerda, pista no meio, 11-20 à direita."""
        area = tk.Frame(pai, bg=ASFALTO, padx=10, pady=10, bd=4, relief="ridge")
        area.grid(row=0, column=1)

        metade = TOTAL_VAGAS // 2
        for i in range(metade):
            esquerda, direita = i + 1, i + 1 + metade
            self.criar_vaga(area, esquerda, linha=i, coluna=0)
            # Faixa central tracejada (pista)
            tk.Label(area, text="┆", bg=ASFALTO, fg=AMARELO,
                     font=("Segoe UI", 16, "bold"), width=6).grid(row=i, column=1)
            self.criar_vaga(area, direita, linha=i, coluna=2)

    def criar_vaga(self, pai, numero, linha, coluna):
        """Cria o quadrado de uma vaga e liga o clique dele à função clicou_vaga."""
        lbl = tk.Label(pai, width=24, height=2, font=("Segoe UI", 10, "bold"),
                       fg="white", relief="solid", bd=2, cursor="hand2")
        lbl.grid(row=linha, column=coluna, pady=2)
        lbl.bind("<Button-1>", lambda _e, n=numero: self.clicou_vaga(n))
        self.labels_vagas[numero] = lbl

    def criar_rodape(self):
        """Barra inferior com o resumo de vagas ocupadas/livres."""
        self.status = tk.Label(self.root, bg=AZUL, fg=AMARELO,
                               font=("Segoe UI", 10, "bold"), pady=6)
        self.status.pack(fill="x", side="bottom")

    # -------------------------------------------------------------------------
    # 7.2 ATUALIZAÇÃO VISUAL DAS VAGAS
    # -------------------------------------------------------------------------
    def atualizar_vagas(self):
        """Pinta cada vaga: verde se livre, vermelha (com placa e modelo) se ocupada."""
        for n, lbl in self.labels_vagas.items():
            dados = self.vagas.get(str(n))
            if dados:
                lbl.config(bg=VERMELHO,
                           text=f"{n:02d} - OCUPADA\n{formatar_placa(dados['placa'])} | {dados['modelo'][:12]}")
            else:
                lbl.config(bg=VERDE, text=f"{n:02d}\nLIVRE")

        ocupadas = len(self.vagas)
        self.status.config(
            text=f"OCUPADAS: {ocupadas}   |   LIVRES: {TOTAL_VAGAS - ocupadas}   |   TOTAL: {TOTAL_VAGAS}")
        self.atualizar_botao_entrada()

    def atualizar_botao_entrada(self):
        """Esconde o botão 'Dar entrada' se todas as vagas estiverem ocupadas
        e mostra de novo assim que alguma vaga for liberada."""
        lotado = len(self.vagas) >= TOTAL_VAGAS
        botao = self.botoes_menu["entrada"]
        proximo = self.botoes_menu["saida"]  # o botão de entrada fica sempre antes deste

        if lotado and self.entrada_visivel:
            botao.pack_forget()
            self.aviso_lotado.pack(pady=4, before=proximo)
            self.entrada_visivel = False
        elif not lotado and not self.entrada_visivel:
            self.aviso_lotado.pack_forget()
            botao.pack(pady=4, before=proximo)
            self.entrada_visivel = True

    # -------------------------------------------------------------------------
    # 7.3 AÇÃO: CLIQUE EM UMA VAGA
    # -------------------------------------------------------------------------
    def clicou_vaga(self, numero):
        """Vaga livre abre a entrada; vaga ocupada mostra os detalhes."""
        dados = self.vagas.get(str(numero))
        if dados is None:
            DialogoEntrada(self, vaga_inicial=numero)
        else:
            entrada = datetime.fromisoformat(dados["entrada"])
            minutos = (datetime.now() - entrada).total_seconds() / 60
            messagebox.showinfo(
                f"VAGA {numero} - OCUPADA",
                f"Cliente: {dados['nome']}\n"
                f"Placa: {formatar_placa(dados['placa'])}\n"
                f"Modelo: {dados['modelo']}\n"
                f"Entrada: {entrada:%d/%m/%Y %H:%M}\n"
                f"Permanência: {formatar_duracao(minutos)}\n"
                f"Valor até agora: {moeda(calcular_valor(minutos))}")

    # -------------------------------------------------------------------------
    # 7.4 AÇÃO: DAR SAÍDA
    # -------------------------------------------------------------------------
    def dar_saida(self):
        """Pergunta o número da vaga e segue para o fechamento da conta."""
        if not self.vagas:
            return messagebox.showinfo("SAÍDA", "Não há veículos estacionados.")

        janela = tk.Toplevel(self.root)
        janela.title("Dar saída")
        janela.configure(bg=FUNDO, padx=20, pady=15)
        janela.transient(self.root)
        janela.grab_set()

        tk.Label(janela, text="NÚMERO DA VAGA:", bg=FUNDO, fg=AZUL,
                 font=("Segoe UI", 11, "bold")).pack()
        entrada = criar_entry_maiusculo(janela, font=("Segoe UI", 12), width=8, justify="center")
        entrada.pack(pady=8)
        entrada.focus_set()

        def confirmar():
            """Valida a vaga digitada; em caso de erro devolve o foco ao campo."""
            txt = entrada.get().strip()
            if not txt.isdigit() or not 1 <= int(txt) <= TOTAL_VAGAS:
                messagebox.showwarning(
                    "Vaga inválida", f"Digite um número de 1 a {TOTAL_VAGAS}.", parent=janela)
                entrada.focus_set()
                entrada.select_range(0, tk.END)
                return
            vaga = str(int(txt))
            if vaga not in self.vagas:
                messagebox.showinfo("Vaga livre", f"A vaga {vaga} já está livre.", parent=janela)
                entrada.focus_set()
                entrada.select_range(0, tk.END)
                return
            janela.destroy()
            self.finalizar_saida(vaga)

        tk.Button(janela, text="CONTINUAR", bg=AZUL, fg=AMARELO, width=14,
                  font=("Segoe UI", 10, "bold"), command=confirmar).pack(pady=4)
        janela.bind("<Return>", lambda _: confirmar())

    def finalizar_saida(self, vaga):
        """Mostra o resumo com o valor total e, se confirmado, libera a vaga."""
        dados = self.vagas[vaga]
        entrada = datetime.fromisoformat(dados["entrada"])
        saida = datetime.now()
        minutos = (saida - entrada).total_seconds() / 60
        valor = calcular_valor(minutos)

        resumo = (
            f"Cliente: {dados['nome']}\n"
            f"Placa: {formatar_placa(dados['placa'])}\n"
            f"Modelo: {dados['modelo']}\n"
            f"Vaga: {vaga}\n"
            f"Entrada: {entrada:%d/%m/%Y %H:%M}\n"
            f"Saída: {saida:%d/%m/%Y %H:%M}\n"
            f"Permanência: {formatar_duracao(minutos)}\n\n"
            f"TOTAL A PAGAR: {moeda(valor)}"
        )

        if messagebox.askyesno("CONFIRMAR PAGAMENTO E SAÍDA", resumo + "\n\nConfirmar saída?"):
            del self.vagas[vaga]        # libera a vaga
            salvar_vagas(self.vagas)
            self.atualizar_vagas()
            messagebox.showinfo("SAÍDA CONCLUÍDA", "Pagamento registrado. Boa viagem!")

    # -------------------------------------------------------------------------
    # 7.4.1 AÇÃO: EXTRATO (VALORES A RECEBER DE CADA VEÍCULO)
    # -------------------------------------------------------------------------
    def mostrar_extrato(self):
        """Tabela com o valor que cada veículo deve até agora e o total a receber."""
        janela = tk.Toplevel(self.root)
        janela.title("Extrato - valores a receber")
        janela.configure(bg=FUNDO)

        tk.Label(janela, text="EXTRATO - VALORES A RECEBER", bg=AZUL, fg=AMARELO,
                 font=("Segoe UI", 14, "bold"), pady=8).pack(fill="x")

        tabela = ttk.Treeview(
            janela, show="headings", height=12,
            columns=("vaga", "nome", "placa", "modelo", "entrada", "tempo", "valor"))
        for col, titulo, largura in [("vaga", "VAGA", 55), ("nome", "NOME", 150),
                                     ("placa", "PLACA", 90), ("modelo", "MODELO", 120),
                                     ("entrada", "ENTRADA", 110), ("tempo", "PERMANÊNCIA", 100),
                                     ("valor", "A RECEBER", 100)]:
            tabela.heading(col, text=titulo)
            tabela.column(col, width=largura, anchor="center")
        tabela.pack(padx=10, pady=10)

        total_label = tk.Label(janela, bg=FUNDO, fg=AZUL, font=("Segoe UI", 13, "bold"))
        total_label.pack(pady=(0, 5))

        def preencher():
            """Recalcula tudo com a hora atual (também usado pelo botão Atualizar)."""
            tabela.delete(*tabela.get_children())
            total = 0.0
            agora = datetime.now()
            for vaga in sorted(self.vagas, key=int):
                d = self.vagas[vaga]
                entrada = datetime.fromisoformat(d["entrada"])
                minutos = (agora - entrada).total_seconds() / 60
                valor = calcular_valor(minutos)
                total += valor
                tabela.insert("", "end", values=(
                    vaga, d["nome"], formatar_placa(d["placa"]), d["modelo"],
                    entrada.strftime("%d/%m %H:%M"), formatar_duracao(minutos), moeda(valor)))
            total_label.config(
                text=f"VEÍCULOS: {len(self.vagas)}   |   TOTAL A RECEBER: {moeda(total)}")

        tk.Button(janela, text="🔄  ATUALIZAR", bg=AMARELO, fg=AZUL, width=16,
                  font=("Segoe UI", 10, "bold"), command=preencher).pack(pady=(0, 10))
        preencher()

    # -------------------------------------------------------------------------
    # 7.5 AÇÃO: LISTAR VEÍCULOS ESTACIONADOS
    # -------------------------------------------------------------------------
    def listar_veiculos(self):
        """Abre uma tabela com todos os veículos que estão no estacionamento."""
        janela = tk.Toplevel(self.root)
        janela.title("Veículos estacionados")
        janela.configure(bg=FUNDO)

        tabela = ttk.Treeview(janela, columns=("vaga", "nome", "placa", "modelo", "entrada"),
                              show="headings", height=12)
        for col, titulo, largura in [("vaga", "VAGA", 60), ("nome", "NOME", 160),
                                     ("placa", "PLACA", 100), ("modelo", "MODELO", 140),
                                     ("entrada", "ENTRADA", 140)]:
            tabela.heading(col, text=titulo)
            tabela.column(col, width=largura, anchor="center")
        tabela.pack(padx=10, pady=10)

        for vaga in sorted(self.vagas, key=int):
            d = self.vagas[vaga]
            entrada = datetime.fromisoformat(d["entrada"]).strftime("%d/%m %H:%M")
            tabela.insert("", "end", values=(vaga, d["nome"], formatar_placa(d["placa"]),
                                             d["modelo"], entrada))

    # -------------------------------------------------------------------------
    # 7.6 AÇÃO: TABELA DE PREÇOS
    # -------------------------------------------------------------------------
    def mostrar_precos(self):
        """Exibe as regras de cobrança."""
        messagebox.showinfo(
            "TABELA DE PREÇOS",
            f"Entrada (primeiros {MINUTOS_BLOCO} min): {moeda(VALOR_BLOCO)}\n"
            f"A cada {MINUTOS_BLOCO} minutos: {moeda(VALOR_BLOCO)}\n"
            f"Hora cheia: {moeda(VALOR_BLOCO * 60 / MINUTOS_BLOCO)}\n\n"
            f"Tolerância: {TOLERANCIA_MIN} minutos sobre cada bloco completo.\n"
            f"Ex.: 1h05 paga {moeda(4 * VALOR_BLOCO)}; 1h11 paga {moeda(5 * VALOR_BLOCO)}.")


# =============================================================================
# 8. PONTO DE ENTRADA DO PROGRAMA
# =============================================================================
if __name__ == "__main__":
    janela_principal = tk.Tk()
    App(janela_principal)
    janela_principal.mainloop()