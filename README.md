# 📊 Análise RFV — Segmentação de Clientes

Aplicação Streamlit para análise **RFV (Recência · Frequência · Valor)**, desenvolvida como projeto do curso **Cientista de Dados – EBAC (M31)**.

## 🚀 Deploy no Render

### Passo a passo

#### 1. Suba o projeto no GitHub
1. Crie um repositório público no [github.com](https://github.com)
2. Faça upload dos arquivos:
   - `app_RFV.py`
   - `requirements.txt`
   - `render.yaml`
   - `README.md`

#### 2. Crie o serviço no Render
1. Acesse [render.com](https://render.com) e faça login (pode usar a conta do GitHub)
2. Clique em **New → Web Service**
3. Conecte ao seu repositório GitHub
4. Preencha as configurações:

| Campo | Valor |
|-------|-------|
| **Name** | `app-rfv` (ou o nome que quiser) |
| **Environment** | `Python` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app_RFV.py --server.port $PORT --server.address 0.0.0.0` |
| **Plan** | `Free` |

5. Clique em **Create Web Service**
6. Aguarde o build (~2 min) — o link ficará disponível no topo da página

> 💡 Se o repositório já tiver o `render.yaml`, as configurações são preenchidas automaticamente.

---

## 📁 Estrutura do projeto

```
rfv_app/
├── app_RFV.py          # Aplicação Streamlit
├── requirements.txt    # Dependências Python
├── render.yaml         # Configuração do Render
└── README.md           # Este arquivo
```

## 📋 Formato do CSV esperado

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `ID_cliente` | int | Identificador único do cliente |
| `CodigoCompra` | int | Código da transação |
| `DiaCompra` | date (YYYY-MM-DD) | Data da compra |
| `ValorTotal` | float | Valor gasto na compra |

## 🔑 Lógica RFV

| Componente | Critério de classificação |
|------------|--------------------------|
| **R** Recência | Menor valor = melhor (A) |
| **F** Frequência | Maior valor = melhor (A) |
| **V** Valor | Maior valor = melhor (A) |

A classificação vai de **AAA** (melhor cliente) a **DDD** (pior cliente), com ações de CRM sugeridas para cada segmento.

## 🛠️ Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app_RFV.py
```

## 📦 Dependências

- `streamlit==1.35.0`
- `pandas==2.2.2`
- `numpy==1.26.4`
- `openpyxl==3.1.2`
