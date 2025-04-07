from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo


db = SQLAlchemy()

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=100)
    imagem = db.Column(db.String(255), nullable=True)

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    pedido_id = db.Column(db.String(36), nullable=False)
    comprador_nome = db.Column(db.String(200), nullable=False)
    comprador_cep = db.Column(db.String(20), nullable=False)
    visivel_adm = db.Column(db.Boolean, default=True)
    
    produto_id = db.Column(db.Integer, nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    data_compra = db.Column(db.Date, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")).date())
    previsao_entrega = db.Column(db.Date)
    data_status_final = db.Column(db.Date)
    status_entrega = db.Column(db.Integer, default=0)
    imagem = db.Column(db.String(255), nullable=True)
