from flask import Flask
from shared.config import configure_app
from models import db, Produto, Compra
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import uuid

app = Flask(__name__)
configure_app(app)
db.init_app(app)

produtos_para_pedido = [
    [
        {"id": 1, "status": 0},
        {"id": 2, "status": 0}
    ],
    [
        {"id": 5, "status": 1},
        {"id": 6, "status": 1}
    ],
    [
        {"id": 9, "status": 2},
        {"id": 10, "status": 2}
    ],
    [
        {"id": 14, "status": 3},
        {"id": 15, "status": 3}
    ],
    [
        {"id": 3, "status": 4},
        {"id": 7, "status": 4},
        {"id": 11, "status": 4},
        {"id": 17, "status": 4}
    ]
]
pedido_id = str(uuid.uuid4())

with app.app_context():
    for grupo in produtos_para_pedido:
        pedido_id = str(uuid.uuid4())

        for item in grupo:
            produto = Produto.query.get(item["id"])
            status = item["status"]

            if not produto:
                print(f"Produto ID {item['id']} não encontrado.")
                continue

            hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()

            if status == 5:
                data_compra = hoje - timedelta(days=1)
                previsao_entrega = data_compra + timedelta(days=5)
            elif status == 4:
                data_compra = hoje - timedelta(days=5)
                previsao_entrega = data_compra + timedelta(days=5)
            else:
                dias_passados = status
                data_compra = hoje - timedelta(days=dias_passados)
                previsao_entrega = data_compra + timedelta(days=5)

            nova_compra = Compra(
                pedido_id=pedido_id,
                comprador_nome="Exemplo_comprador",
                comprador_cep="11111-222",
                produto_id=produto.id,
                nome=produto.nome,
                valor=produto.valor,
                quantidade=1,
                imagem=produto.imagem,
                data_compra=data_compra,
                previsao_entrega=previsao_entrega,
                status_entrega=status
            )

            db.session.add(nova_compra)
            print(f"Produto {produto.nome} inserido com status {status}")

    db.session.commit()
    print("Todos os pedidos foram criados com sucesso.")