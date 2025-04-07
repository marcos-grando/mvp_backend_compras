from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from shared.config import configure_app
from models import db, Compra, Produto
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import shutil
import uuid

app = Flask(__name__)
configure_app(app)
db.init_app(app)
CORS(app)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

COMPRAS_FOLDER = "imgs_compras"
app.config["COMPRAS_FOLDER"] = COMPRAS_FOLDER
os.makedirs(COMPRAS_FOLDER, exist_ok=True)


@app.route('/imgs_compras/<path:filename>')
def get_compra_imagem(filename):
    return send_from_directory(app.config["COMPRAS_FOLDER"], filename)

@app.route('/compras', methods=['POST'])
def registrar_compra():
    dados = request.json
    produtos = dados.get("produtos")
    comprador_nome = dados.get("comprador_nome")
    comprador_cep = dados.get("comprador_cep")

    if not produtos or not isinstance(produtos, list):
        return jsonify({"erro": "Lista de produtos inválida"}), 400
    if not comprador_nome or not comprador_cep:
        return jsonify({"erro": "Nome e CEP do comprador são obrigatórios"}), 400

    pedido_id = str(uuid.uuid4())
    data_hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    previsao = data_hoje + timedelta(days=5)

    for item in produtos:
        produto = Produto.query.get(item.get('produto_id'))
        if not produto:
            return jsonify({"erro": f"Produto ID {item.get('produto_id')} não encontrado"}), 404

        quantidade = item.get('quantidade', 1)
        if not isinstance(quantidade, int) or quantidade <= 0:
            return jsonify({"erro": "Quantidade inválida"}), 400

        if quantidade > produto.estoque:
            return jsonify({"erro": f"Estoque insuficiente para o produto {produto.nome}"}), 400

        produto.estoque -= quantidade

        imagem_compra = None
        if produto.imagem and not produto.imagem.startswith("http"):
            nome_arquivo = f"{uuid.uuid4().hex}_{os.path.basename(produto.imagem)}"
            origem = os.path.join(app.config["UPLOAD_FOLDER"], os.path.basename(produto.imagem))
            destino = os.path.join(app.config["COMPRAS_FOLDER"], nome_arquivo)
            if os.path.exists(origem):
                shutil.copy2(origem, destino)
                imagem_compra = f"/imgs_compras/{nome_arquivo}"
            else:
                imagem_compra = produto.imagem
        else:
            imagem_compra = produto.imagem

        compra = Compra(
            pedido_id=pedido_id,
            comprador_nome=comprador_nome,
            comprador_cep=comprador_cep,
            produto_id=produto.id,
            nome=item.get('nome', produto.nome),
            valor=item.get('valor', produto.valor),
            quantidade=quantidade,
            imagem=imagem_compra,
            previsao_entrega=previsao
        )
        db.session.add(compra)

    db.session.commit()
    return jsonify({"mensagem": "Compra registrada com sucesso!", "pedido_id": pedido_id}), 201

@app.route('/compras/atualizar-status', methods=['PATCH'])
def atualizar_status_compras():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    todas = Compra.query.all()

    for compra in todas:
        dias = (agora.date() - compra.data_compra).days
        hora = agora.hour

        if compra.status_entrega in [4, 5]:
            continue

        if dias == 0:
            compra.status_entrega = 0
        elif dias == 1:
            compra.status_entrega = 1
        elif dias in [2, 3]:
            compra.status_entrega = 2
        elif dias == 4:
            compra.status_entrega = 3
        elif dias >= 5 and hora >= 12:
            compra.status_entrega = 4
            if not compra.data_status_final:
                compra.data_status_final = agora.date()
        else:
            compra.status_entrega = 5

    db.session.commit()
    return jsonify({"mensagem": "Status e datas atualizados com sucesso."})

@app.route('/compras', methods=['GET'])
def listar_compras():
    nome = request.args.get("nome")
    cep = request.args.get("cep")

    if not nome or not cep:
        return jsonify({"erro": "Nome e CEP necessários para visualizar as compras"}), 400

    compras = Compra.query.filter_by(
        comprador_nome=nome.strip(),
        comprador_cep=cep.strip()
    ).order_by(Compra.data_compra.desc(), Compra.id.desc()).all()
    # ).order_by(Compra.data_compra.desc()).all()

    pedidos = {}
    for compra in compras:
        if compra.pedido_id not in pedidos:
            pedidos[compra.pedido_id] = {
                "pedido_id": compra.pedido_id,
                "data": compra.data_compra.strftime("%Y-%m-%d"),
                "data_status_final": compra.data_status_final.strftime("%Y-%m-%d") if compra.data_status_final else None,
                "previsao_entrega": compra.previsao_entrega.strftime("%Y-%m-%d") if compra.previsao_entrega else None,
                "comprador_nome": compra.comprador_nome,
                "comprador_cep": compra.comprador_cep,
                "itens": []
            }

        pedidos[compra.pedido_id]["itens"].append({
            "produto_id": compra.produto_id,
            "nome": compra.nome,
            "valor": compra.valor,
            "status": compra.status_entrega,
            "quantidade": compra.quantidade,
            "imagem": compra.imagem if compra.imagem.startswith("http") else f"http://localhost:5003{compra.imagem}",
            "previsao_entrega": compra.previsao_entrega.strftime("%Y-%m-%d") if compra.previsao_entrega else None,
            "data_status_final": compra.data_status_final.strftime("%Y-%m-%d") if compra.data_status_final else None
        })

    pedidos_ordenados = sorted(pedidos.values(), key=lambda x: x["data"], reverse=True)
    return jsonify(pedidos_ordenados)

@app.route('/compras/validar', methods=['GET'])
def validar_comprador():
    nome = request.args.get("nome")
    cep = request.args.get("cep")

    resposta = {"nome": False, "cep": False}

    if nome:
        resposta["nome"] = bool(Compra.query.filter_by(comprador_nome=nome.strip()).first())

    if nome and cep:
        resposta["cep"] = bool(Compra.query.filter_by(comprador_nome=nome.strip(), comprador_cep=cep.strip()).first())

    return jsonify(resposta)

@app.route('/compras/adm', methods=['GET'])
def listar_compras_adm():
    # compras = Compra.query.filter_by(visivel_adm=True).order_by(Compra.data_compra.desc()).all()
    compras = Compra.query.filter_by(visivel_adm=True).order_by(Compra.data_compra.desc(), Compra.id.desc()).all()

    pedidos = {}
    for compra in compras:
        if compra.pedido_id not in pedidos:
            pedidos[compra.pedido_id] = {
                "pedido_id": compra.pedido_id,
                "data": compra.data_compra.strftime("%Y-%m-%d"),
                "status": compra.status_entrega,
                "comprador_nome": compra.comprador_nome,
                "comprador_cep": compra.comprador_cep,
                "itens": []
            }

        pedidos[compra.pedido_id]["itens"].append({
            "produto_id": compra.produto_id,
            "nome": compra.nome,
            "valor": compra.valor,
            "quantidade": compra.quantidade,
            "status": compra.status_entrega,
            "imagem": compra.imagem if compra.imagem.startswith("http") else f"http://localhost:5003{compra.imagem}",
            "previsao_entrega": compra.previsao_entrega.strftime("%Y-%m-%d") if compra.previsao_entrega else None,
            "data_status_final": compra.data_status_final.strftime("%Y-%m-%d") if compra.data_status_final else None
        })

    pedidos_ordenados = sorted(pedidos.values(), key=lambda x: x["data"], reverse=True)
    return jsonify(pedidos_ordenados)

@app.route('/compras/<string:id>', methods=['DELETE', 'OPTIONS'])
def cancelar_excluir_compra(id):
    if request.method == 'OPTIONS':
        return '', 200

    compras = Compra.query.filter_by(pedido_id=id).all()
    if not compras:
        return jsonify({"erro": "Compra não encontrada"}), 404

    agora = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    acao = ""
    for compra in compras:
        produto = Produto.query.get(compra.produto_id)

        if compra.status_entrega in [0, 1, 2, 3]:
            compra.status_entrega = 5
            compra.data_status_final = agora
            if produto:
                produto.estoque += compra.quantidade
            acao = "cancelada e estoque atualizado"
        else:
            compra.visivel_adm = False
            acao = "removida da visão do administrador"

    db.session.commit()
    return jsonify({"mensagem": f"Compra {acao} com sucesso!"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
