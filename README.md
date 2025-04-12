### Desenvolvimento Full Stack - PUC-Rio

## MVP Back End com Flask + Interface React:
# 🛒 Big Loja (loja virtual) 

O objetivo do MVP foi desenvolver uma loja virtual, contemplando tanto a experiência do usuário quanto o gerenciamento administrativo do sistema. 

👤 Usuário: pode navegar entre produtos, filtrar por categoria ou preço, adicionar e manipular itens no carrinho, finalizar compras e acompanhar pedidos no histórico.

🛠️ Administrador: conta com um painel de controle que permite o cadastro e gerenciamento de produtos e categorias, além de visualizar todos os pedidos realizados (incluindo a opção de cancelamento de pedidos).

---

## 💳 API de Compras (backend_compras)

Esse repositório é o backend responsável por registrar e consultar compras feitas pelos clientes na loja virtual. Ele também cuida dos status de entrega, armazena os pedidos e atualiza o estoque dos produtos comprados. Tudo roda com Flask e é integrado aos demais serviços do sistema.

---

## 🚀 O que essa API faz

- 🛒 **Registrar novas compras**, com agrupamento por pedido
- 📋 **Listar pedidos por nome e CEP**
- 📈 **Atualizar automaticamente o status de entrega**
- 👀 **Visualizar pedidos no painel admin**
- ❌ **Cancelar pedidos ou remover da visualização**
- 🖼️ **Copiar imagem do produto para a pasta `imgs_compras/`**

---

## 🧪 `newbuy.py`

- Este repositório inclui também o `newbuy.py`, um script útil para testes. Ele permite adicionar compras com IDs de produtos existentes e um status de entrega pré-definido, facilitando a simulação e verificação de cada etapa do processo de entrega.

---

## 🔄 Principais rotas

| Método | Rota                          | Função                                        |
|--------|-------------------------------|-----------------------------------------------|
| POST   | `/compras`                    | Registra uma nova compra                      |
| GET    | `/compras`                    | Lista as compras do cliente (por nome e CEP)  |
| GET    | `/compras/adm`                | Lista todos os pedidos para o painel admin    |
| PATCH  | `/compras/atualizar-status`   | Atualiza automaticamente os status de entrega |
| GET    | `/compras/validar`            | Valida nome e CEP do cliente                  |
| DELETE | `/compras/<pedido_id>`        | Cancela ou oculta um pedido                   |

---

## 🛠️ Tecnologias utilizadas

- **Python 3.10**
- **Flask** com `flask_sqlalchemy` e `flask_cors`
- **uuid**, **datetime**, **zoneinfo**, **os** e **shutil** para controle de pedidos, datas e cópia de imagens
- **Docker** para containerização

---

## 📦 Como rodar o projeto

Esse container faz parte de um sistema completo e depende dos seguintes repositórios para funcionar corretamente:

### Estrutura do sistema:

- 🌐 **API externa**: [FakeStore](https://fakestoreapi.com/) → usada para popular a base com produtos fictícios. O modelo `Produto` foi estruturado com base nos dados dessa API (nome, valor, imagem, etc).
- 🔹 [`backend_categorias`](https://github.com/marcos-grando/mvp_backend_categorias) → responsável pelo cadastro e gerenciamento das categorias dos produtos
- 🔹 [`backend_produtos`](https://github.com/marcos-grando/mvp_backend_produtos) → responsável pelo gerenciamento dos produtos (incluindo uploads das imagens dos produtos)
- 🔹 [`backend_compras`] ← Você está nesse repositório
- 🔸 [`backend_shared`](https://github.com/marcos-grando/mvp_backend_shared) → módulo auxiliar compartilhado (banco de dados, pastas de upload, etc)
- 💠 [`frontend`](https://github.com/marcos-grando/mvp_frontend_bigloja) → interface React responsável pela exibição dos produtos, carrinho, compras e painel administrativo, conectando-se às APIs

**Esse container precisa acessar um volume compartilhado (`backend_shared`) para acessar:**
 - O banco de dados SQLite
 - A pasta `uploads/` (de onde copia as imagens dos produtos)
 - A pasta `imgs_compras/` (onde salva as imagens dos pedidos)
 - Configuração centralizada da aplicação Flask em `config.py`

***OBS: `docker-compose`***  
 - O sistema utiliza 3 APIs diferentes, com dependências entre os módulos  
 - Por isso, é recomendado utilizar o `docker-compose`, que está no repositório `frontend`  
 - Isso evita a necessidade de buildar e subir manualmente cada componente um por um

---

## ▶️ Como rodar

1. Clone esse repositório  
2. Certifique-se de que os outros containers estão na mesma estrutura  
3. No terminal, execute:

```bash
docker-compose up --build -d
```

---

## 🧠 Observações
Esse repositório faz parte de um MVP acadêmico. O sistema foi dividido em partes que se comunicam entre si por rotas. O backend foi feito com Flask (Python) e frontend com React.js.

### 🙋‍♂️ Autor
Desenvolvido por Marcos Grando ✌️

"""
