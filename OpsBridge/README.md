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

## Future Improvements

The OpsBridge MVP is functional, with ticket management, status tracking, technician assignment, an interactive dashboard, and automated API tests.

The following improvements are planned for future development:

- [ ] **Workflow Automation:** Integrate with Make or Microsoft Power Automate using webhooks to automatically notify IT teams when critical tickets are created.
- [ ] **Email Notifications:** Send automatic notifications when tickets are assigned, updated, or resolved.
- [ ] **User Authentication:** Implement secure login and role-based access control for employees, IT technicians, and administrators.
- [ ] **AI-Powered Ticket Classification:** Explore automatic categorization and prioritization of incoming requests using AI.
- [ ] **Advanced Analytics:** Expand the dashboard with resolution times, ticket trends, and operational performance indicators.
- [ ] **Deployment:** Deploy the application to a cloud environment for remote access and demonstration.

These improvements are part of the project's roadmap and are not included in the current MVP.

## Limites desta versão

Protótipo de portfólio, não pronto para produção. Não tem autenticação, permissões, migrações Alembic, tratamento de auditoria por utilizador, nem notificações Make. Não coloques dados sensíveis reais. This project was developed with the assistance of ChatGPT. The application was tested locally to validate its core functionality.
