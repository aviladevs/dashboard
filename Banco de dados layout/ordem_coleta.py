import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import sqlite3
import datetime

# BANCO

def init_db():
    conn = sqlite3.connect("coletas.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, cnpj TEXT, endereco TEXT, contato TEXT
        );
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS coletas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_coleta TEXT,
            emitente_nome TEXT, emitente_cnpj TEXT, emitente_endereco TEXT, emitente_contato TEXT,
            destinatario_nome TEXT, destinatario_cnpj TEXT, destinatario_endereco TEXT, destinatario_contato TEXT,
            data_solicitacao TEXT, data_coleta TEXT, horario TEXT,
            tipo_mercadoria TEXT, peso TEXT, volume TEXT, observacoes TEXT, responsavel TEXT, logo BLOB
        );
    """
    )
    conn.commit()
    return conn


def buscar_clientes(conn):
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    return df


def cadastrar_cliente(conn, nome, cnpj, endereco, contato):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nome, cnpj, endereco, contato) VALUES (?, ?, ?, ?)",
        (nome, cnpj, endereco, contato),
    )
    conn.commit()


def cadastrar_coleta(conn, coleta):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO coletas (
            numero_coleta, emitente_nome, emitente_cnpj, emitente_endereco, emitente_contato,
            destinatario_nome, destinatario_cnpj, destinatario_endereco, destinatario_contato,
            data_solicitacao, data_coleta, horario,
            tipo_mercadoria, peso, volume, observacoes, responsavel, logo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            coleta["numero_coleta"],
            coleta["emitente_nome"],
            coleta["emitente_cnpj"],
            coleta["emitente_endereco"],
            coleta["emitente_contato"],
            coleta["destinatario_nome"],
            coleta["destinatario_cnpj"],
            coleta["destinatario_endereco"],
            coleta["destinatario_contato"],
            coleta["data_solicitacao"],
            coleta["data_coleta"],
            coleta["horario"],
            coleta["tipo_mercadoria"],
            coleta["peso"],
            coleta["volume"],
            coleta["observacoes"],
            coleta["responsavel"],
            coleta["logo"],
        ),
    )
    conn.commit()


def atualizar_coleta(conn, coleta_id, coleta):
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE coletas SET
            emitente_nome=?, emitente_cnpj=?, emitente_endereco=?, emitente_contato=?,
            destinatario_nome=?, destinatario_cnpj=?, destinatario_endereco=?, destinatario_contato=?,
            data_solicitacao=?, data_coleta=?, horario=?,
            tipo_mercadoria=?, peso=?, volume=?, observacoes=?, responsavel=?
        WHERE id=?
    """,
        (
            coleta["emitente_nome"],
            coleta["emitente_cnpj"],
            coleta["emitente_endereco"],
            coleta["emitente_contato"],
            coleta["destinatario_nome"],
            coleta["destinatario_cnpj"],
            coleta["destinatario_endereco"],
            coleta["destinatario_contato"],
            coleta["data_solicitacao"],
            coleta["data_coleta"],
            coleta["horario"],
            coleta["tipo_mercadoria"],
            coleta["peso"],
            coleta["volume"],
            coleta["observacoes"],
            coleta["responsavel"],
            coleta_id,
        ),
    )
    conn.commit()


def buscar_coletas(conn):
    df = pd.read_sql_query("SELECT * FROM coletas ORDER BY id DESC", conn)
    return df


def gerar_numero_coleta():
    agora = datetime.datetime.now()
    return f"C{agora.strftime('%Y%m%d%H%M%S')}"


class OrdemColetaPDF(FPDF):
    def __init__(self, logo_bytes=None):
        super().__init__()
        self.logo_bytes = logo_bytes

    def header(self):
        if self.logo_bytes:
            temp_logo = "temp_logo.png"
            with open(temp_logo, "wb") as f:
                f.write(self.logo_bytes)
            self.image(temp_logo, 12, 10, 28)
        self.set_font("Arial", "B", 18)
        self.cell(0, 15, "Ordem de Coleta", align="C", ln=True)
        self.ln(2)
        self.set_font("Arial", "", 11)
        self.cell(0, 8, "Documento gerado por Avila Transportes", align="C", ln=True)
        self.ln(4)
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def section(self, title):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(230, 230, 255)
        self.cell(0, 8, f" {title} ", ln=True, fill=True)
        self.ln(1)

    def value_line(self, label, value):
        self.set_font("Arial", "B", 10)
        self.cell(50, 7, label, border=0)
        self.set_font("Arial", "", 10)
        self.cell(0, 7, str(value), border=0, ln=True)

    def add_ordem(self, coleta):
        self.section(f"Dados da Coleta Nº {coleta['numero_coleta']}")
        self.value_line("Data Solicitação:", coleta['data_solicitacao'])
        self.value_line("Data Coleta:", coleta['data_coleta'])
        self.value_line("Horário:", coleta['horario'])
        self.value_line("Tipo de Mercadoria:", coleta['tipo_mercadoria'])
        self.value_line("Peso Estimado:", coleta['peso'])
        self.value_line("Volume Estimado:", coleta['volume'])

        self.ln(2)
        self.section("Emitente (Remetente)")
        self.value_line("Razão Social:", coleta['emitente_nome'])
        self.value_line("CNPJ:", coleta['emitente_cnpj'])
        self.value_line("Endereço:", coleta['emitente_endereco'])
        self.value_line("Contato:", coleta['emitente_contato'])

        self.ln(2)
        self.section("Destinatário (Recebedor)")
        self.value_line("Razão Social:", coleta['destinatario_nome'])
        self.value_line("CNPJ:", coleta['destinatario_cnpj'])
        self.value_line("Endereço:", coleta['destinatario_endereco'])
        self.value_line("Contato:", coleta['destinatario_contato'])

        self.ln(2)
        self.section("Observações")
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 6, coleta['observacoes'])

        self.ln(6)
        self.value_line("Responsável pela Emissão:", coleta['responsavel'])
        self.value_line("Assinatura:", "_____________________________")
        self.ln(2)
        self.set_font("Arial", "I", 7)
        self.cell(
            0,
            8,
            "Documento gerado automaticamente - Avila Transportes",
            align="C",
            ln=True,
        )


st.set_page_config(
    page_title="Ordem de Coleta - Avila Transportes", layout="centered"
)
st.title("🚚 Avila Transportes - Sistema de Ordem de Coleta")

conn = init_db()

aba = st.sidebar.selectbox(
    "Menu", ["Nova Ordem de Coleta", "Consultar Ordem de Coleta", "Clientes"]
)

if aba == "Clientes":
    st.header("Cadastro & Busca de Clientes")
    with st.form("novo_cliente"):
        nome = st.text_input("Razão Social")
        cnpj = st.text_input("CNPJ")
        endereco = st.text_input("Endereço")
        contato = st.text_input("Contato")
        submitted = st.form_submit_button("Cadastrar Cliente")
        if submitted and nome:
            cadastrar_cliente(conn, nome, cnpj, endereco, contato)
            st.success("Cliente cadastrado!")

    st.subheader("Inventário de Clientes")
    df_clientes = buscar_clientes(conn)
    if df_clientes.empty:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        selected_idx = st.selectbox(
            "Selecione um cliente para editar ou apagar:",
            df_clientes.index,
            format_func=lambda idx: df_clientes.loc[idx, "nome"],
        )
        cliente = df_clientes.loc[selected_idx]
        with st.expander(f"Editar cliente: {cliente['nome']}"):
            novo_nome = st.text_input(
                "Razão Social", value=cliente["nome"], key=f"nome_{cliente['id']}"
            )
            novo_cnpj = st.text_input(
                "CNPJ", value=cliente["cnpj"], key=f"cnpj_{cliente['id']}"
            )
            novo_endereco = st.text_input(
                "Endereço", value=cliente["endereco"], key=f"end_{cliente['id']}"
            )
            novo_contato = st.text_input(
                "Contato", value=cliente["contato"], key=f"contato_{cliente['id']}"
            )
            col_e, col_a = st.columns([1, 1])
            with col_e:
                if st.button("Salvar Alterações", key=f"salvar_{cliente['id']}"):
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE clientes SET nome=?, cnpj=?, endereco=?, contato=? WHERE id=?
                    """,
                        (novo_nome, novo_cnpj, novo_endereco, novo_contato, cliente["id"]),
                    )
                    conn.commit()
                    st.success("Alterações salvas.")
            with col_a:
                if st.button("Apagar Cliente", key=f"apagar_{cliente['id']}"):
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM clientes WHERE id=?", (cliente["id"],)
                    )
                    conn.commit()
                    st.warning("Cliente apagado.")

        st.dataframe(buscar_clientes(conn), use_container_width=True)


if aba == "Consultar Ordem de Coleta":
    st.header("Consultar e Alterar Ordem de Coleta")
    df = buscar_coletas(conn)
    if df.empty:
        st.warning("Nenhuma ordem cadastrada ainda.")
    else:
        selected = st.selectbox("Selecione uma Ordem pelo número", df["numero_coleta"])
        coleta_row = df[df["numero_coleta"] == selected].iloc[0]
        if "editar" not in st.session_state:
            st.session_state.editar = False

        if not st.session_state.editar:
            st.write("**Emitente:**", coleta_row["emitente_nome"])
            st.write("**Destinatário:**", coleta_row["destinatario_nome"])
            st.write("**Data da Solicitação:**", coleta_row["data_solicitacao"])
            st.write("**Data da Coleta:**", coleta_row["data_coleta"])
            st.write("**Horário:**", coleta_row["horario"])
            st.write("**Tipo de Mercadoria:**", coleta_row["tipo_mercadoria"])
            st.write("**Peso Estimado:**", coleta_row["peso"])
            st.write("**Volume Estimado:**", coleta_row["volume"])
            st.write("**Observações:**", coleta_row["observacoes"])
            st.write("**Responsável:**", coleta_row["responsavel"])
            if st.button("Editar"):
                st.session_state.editar = True

            logo_bytes = coleta_row["logo"]
            coleta_dict = coleta_row.to_dict()
            pdf = OrdemColetaPDF(logo_bytes=logo_bytes)
            pdf.add_page()
            pdf.add_ordem(coleta_dict)
            pdf_buffer = io.BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)
            st.download_button(
                label="📥 Baixar PDF",
                data=pdf_buffer,
                file_name=f"ordem_coleta_{coleta_row['numero_coleta']}.pdf",
                mime="application/pdf",
            )
        else:
            with st.form("editar_coleta"):
                emitente_nome = st.text_input("Emitente", value=coleta_row["emitente_nome"])
                destinatario_nome = st.text_input(
                    "Destinatário", value=coleta_row["destinatario_nome"]
                )
                data_solicitacao = st.text_input(
                    "Data Solicitação", value=coleta_row["data_solicitacao"]
                )
                data_coleta = st.text_input(
                    "Data Coleta", value=coleta_row["data_coleta"]
                )
                horario = st.text_input("Horário para Coleta", value=coleta_row["horario"])
                tipo_mercadoria = st.text_input(
                    "Tipo de Mercadoria", value=coleta_row["tipo_mercadoria"]
                )
                peso = st.text_input("Peso Estimado", value=coleta_row["peso"])
                volume = st.text_input("Volume Estimado", value=coleta_row["volume"])
                observacoes = st.text_area(
                    "Observações", value=coleta_row["observacoes"]
                )
                responsavel = st.text_input(
                    "Responsável", value=coleta_row["responsavel"]
                )
                salvar = st.form_submit_button("Salvar Alterações")
                if salvar:
                    coleta = dict(
                        emitente_nome=emitente_nome,
                        emitente_cnpj=coleta_row["emitente_cnpj"],
                        emitente_endereco=coleta_row["emitente_endereco"],
                        emitente_contato=coleta_row["emitente_contato"],
                        destinatario_nome=destinatario_nome,
                        destinatario_cnpj=coleta_row["destinatario_cnpj"],
                        destinatario_endereco=coleta_row["destinatario_endereco"],
                        destinatario_contato=coleta_row["destinatario_contato"],
                        data_solicitacao=data_solicitacao,
                        data_coleta=data_coleta,
                        horario=horario,
                        tipo_mercadoria=tipo_mercadoria,
                        peso=peso,
                        volume=volume,
                        observacoes=observacoes,
                        responsavel=responsavel,
                    )
                    atualizar_coleta(conn, coleta_row["id"], coleta)
                    st.success("Alteração salva!")
                    st.session_state.editar = False
                    st.experimental_rerun()
            if st.button("Cancelar"):
                st.session_state.editar = False

            if st.button("Duplicar esta Ordem de Coleta"):
                novo_numero = gerar_numero_coleta()
                nova_coleta = coleta_row.to_dict()
                nova_coleta["numero_coleta"] = novo_numero
                nova_coleta["data_solicitacao"] = datetime.datetime.now().strftime(
                    "%d/%m/%Y"
                )
                nova_coleta["data_coleta"] = datetime.datetime.now().strftime("%d/%m/%Y")
                nova_coleta["id"] = None
                with st.form("duplicar_ordem"):
                    st.write("Edite os campos antes de salvar a nova ordem.")
                    emitente_nome = st.text_input(
                        "Emitente", value=nova_coleta["emitente_nome"]
                    )
                    destinatario_nome = st.text_input(
                        "Destinatário", value=nova_coleta["destinatario_nome"]
                    )
                    data_solicitacao = st.text_input(
                        "Data Solicitação", value=nova_coleta["data_solicitacao"]
                    )
                    data_coleta = st.text_input(
                        "Data Coleta", value=nova_coleta["data_coleta"]
                    )
                    horario = st.text_input(
                        "Horário para Coleta", value=nova_coleta["horario"]
                    )
                    tipo_mercadoria = st.text_input(
                        "Tipo de Mercadoria", value=nova_coleta["tipo_mercadoria"]
                    )
                    peso = st.text_input(
                        "Peso Estimado", value=nova_coleta["peso"]
                    )
                    volume = st.text_input(
                        "Volume Estimado", value=nova_coleta["volume"]
                    )
                    observacoes = st.text_area(
                        "Observações", value=nova_coleta["observacoes"]
                    )
                    responsavel = st.text_input(
                        "Responsável", value=nova_coleta["responsavel"]
                    )
                    salvar_dup = st.form_submit_button(
                        "Salvar nova Ordem Duplicada"
                    )
                    if salvar_dup:
                        coleta = dict(
                            numero_coleta=novo_numero,
                            emitente_nome=emitente_nome,
                            emitente_cnpj=coleta_row["emitente_cnpj"],
                            emitente_endereco=coleta_row["emitente_endereco"],
                            emitente_contato=coleta_row["emitente_contato"],
                            destinatario_nome=destinatario_nome,
                            destinatario_cnpj=coleta_row["destinatario_cnpj"],
                            destinatario_endereco=coleta_row["destinatario_endereco"],
                            destinatario_contato=coleta_row["destinatario_contato"],
                            data_solicitacao=data_solicitacao,
                            data_coleta=data_coleta,
                            horario=horario,
                            tipo_mercadoria=tipo_mercadoria,
                            peso=peso,
                            volume=volume,
                            observacoes=observacoes,
                            responsavel=responsavel,
                            logo=coleta_row["logo"],
                        )
                        cadastrar_coleta(conn, coleta)
                        st.success(
                            f"Ordem {novo_numero} duplicada e salva!"
                        )


if aba == "Nova Ordem de Coleta":
    st.header("Ordem de Coleta")

    df_clientes = buscar_clientes(conn)
    opcoes = df_clientes["nome"].tolist() if not df_clientes.empty else []

    col1, col2 = st.columns(2)
    with col1:
        emitente_nome = st.selectbox(
            "Emitente", options=opcoes + ["Outro (preencher manualmente)"]
        )
    with col2:
        destinatario_nome = st.selectbox(
            "Destinatário", options=opcoes + ["Outro (preencher manualmente)"]
        )

    def campos_cliente(prefixo):
        col1, col2 = st.columns(2)
        with col1:
            cnpj = st.text_input(f"CNPJ{prefixo}")
        with col2:
            contato = st.text_input(f"Contato {prefixo}")
        endereco = st.text_input(f"Endereço {prefixo}")
        return cnpj, endereco, contato

    col3, col4, col5 = st.columns(3)
    with col3:
        data_solicitacao = st.date_input("Data da Solicitação", datetime.date.today())
    with col4:
        data_coleta = st.date_input("Data da Coleta", datetime.date.today())
    with col5:
        horario = st.text_input("Horário para Coleta", "08:00 - 12:00")

    if emitente_nome == "Outro (preencher manualmente)":
        st.markdown("### Dados do Emitente")
        emitente_cnpj, emitente_endereco, emitente_contato = campos_cliente(
            "Emitente"
        )
    else:
        dados = df_clientes[df_clientes["nome"] == emitente_nome].iloc[0]
        emitente_cnpj = dados["cnpj"]
        emitente_endereco = dados["endereco"]
        emitente_contato = dados["contato"]

    if destinatario_nome == "Outro (preencher manualmente)":
        st.markdown("### Dados do Destinatário")
        destinatario_cnpj, destinatario_endereco, destinatario_contato = campos_cliente(
            "Destinatário"
        )
    else:
        dados = df_clientes[df_clientes["nome"] == destinatario_nome].iloc[0]
        destinatario_cnpj = dados["cnpj"]
        destinatario_endereco = dados["endereco"]
        destinatario_contato = dados["contato"]

    tipo_mercadoria = st.text_input("Tipo de Mercadoria")
    peso = st.text_input("Peso Estimado")
    volume = st.text_input("Volume Estimado")
    observacoes = st.text_area("Observações")
    responsavel = st.text_input("Responsável", "Nícolas Rosa Ávila Barros")
    logo = st.file_uploader("Logo para PDF (PNG/JPG)", type=["png", "jpg", "jpeg"])

    gerar = st.button("Gerar Ordem de Coleta")

    if gerar:
        numero_coleta = gerar_numero_coleta()
        coleta = dict(
            numero_coleta=numero_coleta,
            emitente_nome=emitente_nome,
            emitente_cnpj=emitente_cnpj,
            emitente_endereco=emitente_endereco,
            emitente_contato=emitente_contato,
            destinatario_nome=destinatario_nome,
            destinatario_cnpj=destinatario_cnpj,
            destinatario_endereco=destinatario_endereco,
            destinatario_contato=destinatario_contato,
            data_solicitacao=data_solicitacao.strftime("%d/%m/%Y"),
            data_coleta=data_coleta.strftime("%d/%m/%Y"),
            horario=horario,
            tipo_mercadoria=tipo_mercadoria,
            peso=peso,
            volume=volume,
            observacoes=observacoes,
            responsavel=responsavel,
            logo=logo.read() if logo else None,
        )
        cadastrar_coleta(conn, coleta)

        pdf = OrdemColetaPDF(logo_bytes=coleta["logo"])
        pdf.add_page()
        pdf.add_ordem(coleta)
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        st.success(
            f"Ordem de Coleta {numero_coleta} cadastrada com sucesso!"
        )
        st.download_button(
            label="📥 Baixar PDF da Ordem de Coleta",
            data=pdf_buffer,
            file_name=f"ordem_coleta_{numero_coleta}.pdf",
            mime="application/pdf",
        )

conn.close()
