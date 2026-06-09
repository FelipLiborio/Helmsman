from fastapi import FastAPI
from random import randint, choice
import time

app = FastAPI()

nomes = ["Mario", "Joao", "Maria", "Ana", "Pedro", "Lucas", "Julia", "Carla"]

cargos = ["Analista", "Desenvolvedor", "Gerente", "Arquiteto", "Estagiario", "Tester"]


@app.get("/usuarios")
def usuarios():

    quantidade = randint(20, 100)

    usuarios = []

    for i in range(quantidade):
        usuarios.append(
            {
                "id": i,
                "nome": choice(nomes),
                "idade": randint(18, 65),
                "cargo": choice(cargos),
                "salario": randint(2000, 20000),
            }
        )

    return {"total": quantidade, "usuarios": usuarios}


@app.get("/relatorio")
def relatorio():

    quantidade = randint(50, 300)

    registros = []

    for i in range(quantidade):
        registros.append(
            {
                "evento": f"evento_{i}",
                "valor": randint(1, 10000),
                "status": choice(["OK", "WARNING", "ERROR"]),
                "timestamp": time.time(),
            }
        )

    return {"gerado_em": time.time(), "registros": registros}


@app.get("/documento")
def documento():

    tamanho = randint(5000, 50000)

    texto = "Lorem ipsum dolor sit amet consectetur adipiscing elit. " * (tamanho // 56)

    return {"titulo": "Documento de Teste", "conteudo": texto}
