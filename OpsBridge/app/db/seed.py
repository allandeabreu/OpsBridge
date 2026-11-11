"""Create demonstrative tickets only when explicitly run: python -m app.db.seed"""
from sqlalchemy import select
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.services.ticket_service import create_ticket, update_ticket


def seed() -> None:
    init_db()
    examples = [
        ("VPN não estabelece ligação", "Ligação remota falha com erro de autenticação.", "network", "critical", "Inês Martins", "in_progress", "Tiago Oliveira"),
        ("Outlook não sincroniza", "Novos emails não aparecem na caixa de entrada.", "software", "high", "Beatriz Costa", "waiting", "Maria Santos"),
        ("Pedido de acesso ao CRM", "É necessário criar permissões para novo colaborador.", "access", "medium", "André Silva", "new", None),
        ("Portátil aquece demasiado", "O equipamento desliga após 20 minutos de utilização.", "hardware", "high", "Rita Pereira", "in_progress", "João Lopes"),
        ("Atualização do navegador", "Versão antiga impede utilização do portal interno.", "software", "low", "Sara Lopes", "resolved", "Maria Santos"),
        ("Recuperação de palavra-passe", "Colaborador já conseguiu recuperar o acesso.", "access", "medium", "Miguel Sousa", "closed", "Tiago Oliveira"),
    ]
    with SessionLocal() as db:
        if db.scalar(select(Ticket.id).limit(1)) is not None:
            print("Já existem tickets. Seed ignorada para preservar os dados existentes.")
            return
        for title, description, category, priority, requester, desired, technician in examples:
            ticket = create_ticket(db, TicketCreate(
                title=title, description=description, category=category, priority=priority, requester=requester
            ))
            if desired != "new" or technician:
                if desired == "closed":
                    update_ticket(db, ticket.id, TicketUpdate(status="resolved", assigned_to=technician))
                    update_ticket(db, ticket.id, TicketUpdate(status="closed"))
                else:
                    update_ticket(db, ticket.id, TicketUpdate(status=desired, assigned_to=technician))
        print(f"Criados {len(examples)} tickets de demonstração.")


if __name__ == "__main__":
    seed()
