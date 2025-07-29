from ofxparse import OfxParser
import pandas as pd

REGRAS = {
    "PIX": ("Transferência", "Financeiro", "Administrativo"),
    "BOLETO": ("Pagamento", "Financeiro", "Administrativo"),
    "TED": ("Transferência", "Financeiro", "Administrativo"),
    "DOC": ("Transferência", "Financeiro", "Administrativo"),
    "NU PAGAMENTOS": ("Recebimento", "Financeiro", "Administrativo"),
    "PAG*": ("Cartão de Crédito", "Financeiro", "Administrativo"),
    "UBER": ("Transporte", "Logística", "Operacional"),
    "GOL": ("Viagem", "Logística", "Operacional"),
    "LATAM": ("Viagem", "Logística", "Operacional"),
    "99": ("Transporte", "Logística", "Operacional")
}

def classificar_transacao(descricao: str, memo: str):
    texto = f"{descricao} {memo}".upper()
    for palavra, (categoria, centro, setor) in REGRAS.items():
        if palavra in texto:
            return categoria, centro, setor
    return "Outros", "❗Definir", "❗Definir"

def extrair_transacoes(ofx_file) -> pd.DataFrame:
    ofx = OfxParser.parse(ofx_file)
    transacoes = []

    for txn in ofx.account.statement.transactions:
        desc = txn.payee or ""
        memo = txn.memo or ""
        categoria, centro, setor = classificar_transacao(desc, memo)

        transacoes.append({
            "Data": txn.date.strftime("%Y-%m-%d"),  # padroniza para string ISO
            "Valor": float(txn.amount),
            "Tipo": "Receita" if txn.amount > 0 else "Despesa",
            "Descrição": desc,
            "Memo": memo,
            "Categoria": categoria,
            "Centro de Custo": centro,
            "Setor": setor,
            "ID Transação": str(txn.id),  # Garante string para chave
            "Conciliado com": ""
        })

    df = pd.DataFrame(transacoes)

    # Garante tipos coerentes para uso posterior
    df["Valor"] = df["Valor"].astype(float)
    df["Data"] = pd.to_datetime(df["Data"])

    return df
