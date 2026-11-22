# Painel Vila Aurora · Streamlit

ENG4550 · Projeto Integrado em Sistemas Produtivos · Grupo 1

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

O painel abre em http://localhost:8501.

## Estrutura

- `app.py`: o painel, com quatro abas (Visão geral, Previsão de demanda, Políticas de estoque, Plano de ação) e filtros de família e canal na barra lateral.
- `data/`: 13 CSVs com os dados do caso (Blocos 1 e 2) e os resultados do grupo (Q4, Bloco 2, Q11, Q12).
- `.streamlit/config.toml`: cores do tema.

## Publicar online (opcional)

Suba a pasta para um repositório no GitHub e conecte em https://share.streamlit.io (Streamlit Community Cloud), apontando para `app.py`.
