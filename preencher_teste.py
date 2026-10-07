"""
Preenche as 20 vagas de uma vez, só para testar o sistema.

Como usar:
    1. Feche o PaguePare Parking (se estiver aberto)
    2. Rode:  python preencher_teste.py
    3. Abra o sistema:  python main.py

ATENÇÃO: sobrescreve o vagas.json atual.
Para limpar tudo depois, apague o arquivo vagas.json.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

ARQUIVO = Path(__file__).with_name("vagas.json")

# (nome, placa, modelo, minutos que o carro já está estacionado)
# Mistura placas antigas e Mercosul, e tempos variados para testar
# a tolerância e o extrato (5, 10, 25, 26, 60, 65, 71 min etc.)
VEICULOS = [
    ("CARLOS SILVA",     "ABC1234", "GOL",         5),
    ("MARIA SOUZA",      "BRA2E19", "ONIX",        10),
    ("JOÃO PEREIRA",     "DEF5678", "CIVIC",       15),
    ("ANA COSTA",        "RIO4A56", "HB20",        25),
    ("PEDRO ALVES",      "GHI9012", "COROLLA",     26),
    ("LUCAS LIMA",       "SPX7B89", "POLO",        40),
    ("FERNANDA ROCHA",   "JKL3456", "KA",          45),
    ("RAFAEL GOMES",     "MNO7890", "FIESTA",      55),
    ("JULIANA MARTINS",  "QWE1R23", "CRETA",       60),
    ("BRUNO NUNES",      "PQR1234", "UNO",         65),
    ("PATRÍCIA DIAS",    "STU5678", "TIGGO 5X",    70),
    ("ROBERTO CRUZ",     "VWX9A12", "COMPASS",     71),
    ("CAMILA BARROS",    "YZA3456", "MOBI",        80),
    ("DIEGO FARIAS",     "BCD7E89", "KICKS",       95),
    ("LARISSA MELO",     "EFG0123", "ARGO",        110),
    ("THIAGO RAMOS",     "HIJ4K56", "T-CROSS",     125),
    ("VANESSA TEIXEIRA", "KLM7890", "SANDERO",     150),
    ("GUSTAVO MOURA",    "NOP2Q34", "HILUX",       180),
    ("ELAINE CARDOSO",   "RST5678", "FIT",         200),
    ("MARCOS VIEIRA",    "UVW8X90", "RENEGADE",    240),
]

agora = datetime.now()
vagas = {}
for numero, (nome, placa, modelo, minutos) in enumerate(VEICULOS, start=1):
    # Garante que todas as placas do teste são válidas
    assert re.match(r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$", placa), f"Placa inválida: {placa}"
    entrada = agora - timedelta(minutes=minutos)
    vagas[str(numero)] = {
        "nome": nome,
        "placa": placa,
        "modelo": modelo,
        "entrada": entrada.isoformat(timespec="seconds"),
    }

ARQUIVO.write_text(json.dumps(vagas, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(vagas)} vagas preenchidas em {ARQUIVO.name}. Agora rode: python main.py")