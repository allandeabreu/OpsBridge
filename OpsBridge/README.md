# OpsBridge — IT Support Ticket Management System

Sistema demonstrativo de gestão de tickets de suporte. **FastAPI + SQLAlchemy + SQLite + HTML/CSS/JavaScript**.
Esta entrega continua o protótipo inicial, preservando o modelo `Ticket` e os endpoints `/` e `/health`.

## Executar no Windows (PowerShell)

Se já tens a `.venv` ativada, **não é necessário recriá-la**. Na pasta `OpsBridge`:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

- Interface: <http://127.0.0.1:8000/ui>
- Documentação interativa API: <http://127.0.0.1:8000/docs>
- Estado: <http://127.0.0.1:8000/health>

As tabelas `tickets` e `ticket_history` são criadas automaticamente quando a aplicação arranca. A base de dados existente `opsbridge.db` **não é apagada**.

## Funcionalidades

- Criar, consultar e atualizar tickets (incluindo prioridade e técnico responsável)
- Filtrar por estado, prioridade, categoria e atribuição; pesquisa por texto
- Estados: new → in_progress / waiting / resolved → closed
- Tickets closed/cancelled são finais; transições inválidas geram HTTP 409
- `DELETE /tickets/{id}` executa **cancelamento lógico**, sem eliminar dados
- Histórico de criação/alterações e dashboard com métricas
- Interface responsiva sem frameworks frontend adicionais

## Endpoints

| Método | URL | Descrição |
|--|--|--|
| POST | `/tickets` | Criar ticket |
| GET | `/tickets` | Listar/filtrar tickets |
| GET | `/tickets/stats` | Métricas |
| GET | `/tickets/{id}` | Detalhe |
| PUT | `/tickets/{id}` | Atualizar campos enviados |
| DELETE | `/tickets/{id}` | Cancelamento lógico |
| GET | `/tickets/{id}/history` | Histórico |

Exemplo de criação:

```json
{"title":"VPN não liga","description":"Não consigo aceder à rede da empresa.","category":"network","priority":"high","requester":"Ana"}
```

## Dados fictícios para veres o dashboard preenchido

Em base de dados vazia, executa opcionalmente:

```powershell
python -m app.db.seed
```

Cria seis tickets de demonstração. Se já houver tickets, não altera os dados.

## Testes

```powershell
python -m pytest -v
```

## Nota de arquitetura

`app/api` recebe pedidos HTTP; `app/services` valida regras de negócio; `app/repositories` executa queries SQLAlchemy; `app/models` modela tabelas; `app/schemas` valida os dados. Os testes isolam uma BD SQLite temporária.

## Limites desta versão

Protótipo de portfólio, não pronto para produção. Não tem autenticação, permissões, migrações Alembic, tratamento de auditoria por utilizador, nem notificações Make. Não coloques dados sensíveis reais. Para produção serão necessários autenticação e controlos de acesso, migrações, monitorização e deploy seguro.
