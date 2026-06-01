import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, date
from io import BytesIO

# ──────────────────────────────────────────────────────────────
# CONFIG DA PÁGINA
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Análise RFV",
    page_icon="📊",
    layout="wide",
)

# ──────────────────────────────────────────────────────────────
# DICIONÁRIO DE AÇÕES DE MARKETING
# ──────────────────────────────────────────────────────────────
dict_acoes = {
    # ── CAMPEÕES ──
    'AAA': 'Enviar cupons de desconto, pedir para indicar o produto a amigos, enviar amostras grátis em novos lançamentos.',
    # ── LEAIS ──
    'AAB': 'Oferecer produtos premium e programa de fidelidade.',
    'AAC': 'Incentivar frequência com programa de pontos.',
    'AAD': 'Desconto progressivo para aumentar ticket médio.',
    'ABA': 'Manter engajamento com newsletters personalizadas.',
    'ABB': 'Oferecer produtos complementares (cross-sell).',
    'ABC': 'Incentivar próxima compra com frete grátis.',
    'ABD': 'Enviar cupom para próxima compra.',
    'ACA': 'Enviar ofertas personalizadas pelo histórico.',
    'ACB': 'Criar programa de pontos para fidelizar.',
    'ACC': 'E-mail de boas-vindas com desconto de retorno.',
    'ACD': 'Desconto na próxima compra.',
    'ADA': 'Recuperar com oferta especial de alto valor.',
    'ADB': 'Enviar catálogo dos produtos mais vendidos.',
    'ADC': 'Frete grátis para próxima compra.',
    'ADD': 'Cliente novo com baixo gasto: nutrir com conteúdo educativo.',
    # ── EM RISCO ──
    'BAA': 'Reativar com cupom especial e lembrete de produtos favoritos.',
    'BAB': 'Enviar oferta personalizada de reengajamento.',
    'BAC': 'Desconto de reativação.',
    'BAD': 'Enviar pesquisa de satisfação.',
    'BBA': 'Newsletters com novidades e promoções.',
    'BBB': 'Programa de indicação com benefícios mútuos.',
    'BBC': 'Incentivar próxima compra com desconto.',
    'BBD': 'Oferecer pacotes combinados.',
    'BCA': 'Oferta de upsell baseada no histórico.',
    'BCB': 'Desconto em categoria específica.',
    'BCC': 'Lembrete de itens no carrinho.',
    'BCD': 'Fidelização com pontos.',
    'BDA': 'Oferta especial de recuperação.',
    'BDB': 'Promoção relâmpago para reativação.',
    'BDC': 'E-mail com melhores ofertas do mês.',
    'BDD': 'Nutrição leve com conteúdo relevante.',
    # ── QUASE PERDIDOS ──
    'CAA': 'Churn! Clientes de alto valor: enviar cupons de desconto para recuperar.',
    'CAB': 'Reativação com desconto agressivo.',
    'CAC': 'Campanha de win-back.',
    'CAD': 'Pesquisa de motivo de saída.',
    'CBA': 'Cupom de desconto de reativação.',
    'CBB': 'Condições especiais para retorno.',
    'CBC': 'Frete grátis para reativar.',
    'CBD': 'Promoção por e-mail.',
    'CCA': 'Tentar reativar com oferta personalizada.',
    'CCB': 'Facilitar condições de pagamento.',
    'CCC': 'Enviar boletim informativo.',
    'CCD': 'Monitorar para possível churn.',
    'CDA': 'Risco de churn iminente: oferta urgente de recuperação.',
    'CDB': 'Pesquisa de satisfação.',
    'CDC': 'Nenhuma ação por ora.',
    'CDD': 'Nenhuma ação.',
    # ── PERDIDOS (CHURN) ──
    'DAA': 'Churn! Clientes que gastaram bastante: enviar cupons para recuperar.',
    'DAB': 'Campanha agressiva de win-back.',
    'DAC': 'Desconto exclusivo de retorno.',
    'DAD': 'Pesquisa de motivo de churn.',
    'DBA': 'Promoção especial de recuperação.',
    'DBB': 'Oferta de retorno.',
    'DBC': 'Newsletter leve de reativação.',
    'DBD': 'Monitorar por mais 30 dias.',
    'DCA': 'Última tentativa de reativação.',
    'DCB': 'Pesquisa de satisfação.',
    'DCC': 'Remover da lista ativa.',
    'DCD': 'Nenhuma ação.',
    'DDA': 'Win-back com desconto forte — última tentativa.',
    'DDB': 'Última tentativa de reativação.',
    'DDC': 'Remover da lista ativa.',
    'DDD': 'Churn! Clientes com baixíssimo engajamento. Nenhuma ação recomendada.',
}


# ──────────────────────────────────────────────────────────────
# FUNÇÕES DE CLASSIFICAÇÃO
# ──────────────────────────────────────────────────────────────
def recencia_class(x, r, q_dict):
    if x <= q_dict[r][0.25]: return 'A'
    elif x <= q_dict[r][0.50]: return 'B'
    elif x <= q_dict[r][0.75]: return 'C'
    else: return 'D'


def freq_val_class(x, fv, q_dict):
    if x <= q_dict[fv][0.25]: return 'D'
    elif x <= q_dict[fv][0.50]: return 'C'
    elif x <= q_dict[fv][0.75]: return 'B'
    else: return 'A'


# ──────────────────────────────────────────────────────────────
# FUNÇÃO PRINCIPAL DE ANÁLISE RFV
# ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def calcular_rfv(df_raw: pd.DataFrame, dia_atual: datetime) -> pd.DataFrame:
    df = df_raw.copy()
    df['DiaCompra'] = pd.to_datetime(df['DiaCompra'])

    # Recência
    df_recencia = (
        df.groupby('ID_cliente', as_index=False)['DiaCompra'].max()
    )
    df_recencia.columns = ['ID_cliente', 'DiaUltimaCompra']
    df_recencia['Recencia'] = df_recencia['DiaUltimaCompra'].apply(
        lambda x: (dia_atual - x).days
    )
    df_recencia.drop('DiaUltimaCompra', axis=1, inplace=True)

    # Frequência
    df_frequencia = (
        df.groupby('ID_cliente')['CodigoCompra']
        .count().reset_index()
    )
    df_frequencia.columns = ['ID_cliente', 'Frequencia']

    # Valor
    df_valor = (
        df.groupby('ID_cliente')['ValorTotal']
        .sum().reset_index()
    )
    df_valor.columns = ['ID_cliente', 'Valor']

    # Merge
    df_RFV = (
        df_recencia
        .merge(df_frequencia, on='ID_cliente')
        .merge(df_valor, on='ID_cliente')
    )
    df_RFV.set_index('ID_cliente', inplace=True)

    # Quartis
    quartis = df_RFV.quantile(q=[0.25, 0.5, 0.75])

    # Classificação
    df_RFV['R_quartil'] = df_RFV['Recencia'].apply(
        recencia_class, args=('Recencia', quartis))
    df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(
        freq_val_class, args=('Frequencia', quartis))
    df_RFV['V_quartil'] = df_RFV['Valor'].apply(
        freq_val_class, args=('Valor', quartis))

    df_RFV['RFV_Score'] = (
        df_RFV['R_quartil'] + df_RFV['F_quartil'] + df_RFV['V_quartil']
    )
    df_RFV['Ações de Marketing / CRM'] = df_RFV['RFV_Score'].map(dict_acoes)

    return df_RFV, quartis


# ──────────────────────────────────────────────────────────────
# FUNÇÃO DE EXPORT EXCEL
# ──────────────────────────────────────────────────────────────
def to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True, sheet_name='RFV')
    return output.getvalue()


# ──────────────────────────────────────────────────────────────
# INTERFACE
# ──────────────────────────────────────────────────────────────
st.title('📊 Análise RFV — Segmentação de Clientes')
st.markdown(
    'A análise **RFV (Recência · Frequência · Valor)** segmenta clientes '
    'pelo comportamento de compra, permitindo ações de CRM e marketing mais precisas.'
)

st.divider()

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.header('⚙️ Configurações')

    uploaded_file = st.file_uploader(
        'Carregar CSV de compras',
        type=['csv'],
        help='Colunas esperadas: ID_cliente, CodigoCompra, DiaCompra, ValorTotal',
    )

    st.markdown('**Data de referência**')
    data_ref = st.date_input(
        'Data atual (base do cálculo de recência)',
        value=date(2021, 12, 9),
    )

    st.divider()
    st.markdown('**Formato esperado do CSV:**')
    st.code('ID_cliente, CodigoCompra,\nDiaCompra, ValorTotal', language='')

# ── CONTEÚDO PRINCIPAL ───────────────────────────────────────
if uploaded_file is None:
    st.info('⬅️  Carregue um arquivo CSV na barra lateral para iniciar a análise.')

    st.subheader('Exemplo do formato esperado')
    exemplo = pd.DataFrame({
        'ID_cliente':   [12747, 12747, 12748],
        'CodigoCompra': [537215, 538537, 540001],
        'DiaCompra':    ['2020-12-05', '2020-12-13', '2021-01-10'],
        'ValorTotal':   [358.56, 347.71, 1200.00],
    })
    st.dataframe(exemplo, use_container_width=True)
    st.stop()

# ── CARREGA E PROCESSA ────────────────────────────────────────
try:
    df_raw = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f'Erro ao ler o arquivo: {e}')
    st.stop()

colunas_esperadas = {'ID_cliente', 'CodigoCompra', 'DiaCompra', 'ValorTotal'}
if not colunas_esperadas.issubset(df_raw.columns):
    faltantes = colunas_esperadas - set(df_raw.columns)
    st.error(f'Colunas faltando no CSV: {faltantes}')
    st.stop()

dia_atual = datetime.combine(data_ref, datetime.min.time())

with st.spinner('Calculando RFV...'):
    df_RFV, quartis = calcular_rfv(df_raw, dia_atual)

# ── MÉTRICAS RESUMO ───────────────────────────────────────────
st.subheader('📋 Resumo geral')

col1, col2, col3, col4 = st.columns(4)
col1.metric('Total de clientes',   f'{len(df_RFV):,}')
col2.metric('Clientes AAA 🏆',     f'{(df_RFV["RFV_Score"] == "AAA").sum():,}')
col3.metric('Clientes DDD ⚠️',     f'{(df_RFV["RFV_Score"] == "DDD").sum():,}')
col4.metric('Receita total',        f'R$ {df_RFV["Valor"].sum():,.2f}')

st.divider()

# ── DISTRIBUIÇÃO DOS SCORES ────────────────────────────────────
st.subheader('🏷️ Distribuição dos RFV Scores')

score_counts = df_RFV['RFV_Score'].value_counts().reset_index()
score_counts.columns = ['RFV_Score', 'Quantidade']

col_a, col_b = st.columns([2, 1])
with col_a:
    st.bar_chart(score_counts.set_index('RFV_Score')['Quantidade'])
with col_b:
    st.dataframe(score_counts.head(15), use_container_width=True, hide_index=True)

st.divider()

# ── TABELA RFV COMPLETA ────────────────────────────────────────
st.subheader('📄 Tabela RFV completa')

filtro_score = st.multiselect(
    'Filtrar por RFV Score',
    options=sorted(df_RFV['RFV_Score'].unique()),
    default=[],
    placeholder='Todos os scores',
)

df_exibir = df_RFV if not filtro_score else df_RFV[df_RFV['RFV_Score'].isin(filtro_score)]

st.dataframe(
    df_exibir.style.format({
        'Recencia':   '{:.0f} dias',
        'Frequencia': '{:.0f}',
        'Valor':      'R$ {:,.2f}',
    }),
    use_container_width=True,
    height=420,
)

st.caption(f'{len(df_exibir):,} clientes exibidos de {len(df_RFV):,} no total.')

st.divider()

# ── QUARTIS ───────────────────────────────────────────────────
with st.expander('📐 Ver quartis utilizados na classificação'):
    st.dataframe(quartis.style.format('{:.2f}'), use_container_width=True)
    st.markdown(
        '- **Recência:** menor = melhor (A). Maior = pior (D).\n'
        '- **Frequência e Valor:** maior = melhor (A). Menor = pior (D).'
    )

# ── DOWNLOAD ──────────────────────────────────────────────────
st.subheader('⬇️ Download do resultado')

excel_bytes = to_excel(df_exibir)

st.download_button(
    label='📥 Baixar RFV em Excel (.xlsx)',
    data=excel_bytes,
    file_name='RFV_output.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
)

st.divider()
st.caption('Análise RFV · EBAC — Cientista de Dados · M31')
