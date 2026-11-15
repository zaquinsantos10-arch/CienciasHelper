import os

from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, stream_with_context

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024  # aceita no máximo 6 MB por pedido

cliente = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODELO = os.getenv("MODELO", "openai/gpt-oss-20b")
# modelo usado só quando o aluno manda uma imagem (precisa ter visão)
MODELO_IMAGEM = os.getenv("MODELO_IMAGEM", "meta-llama/llama-4-scout-17b-16e-instruct")
MAX_MENSAGENS = 20  # limite do histórico pra não estourar o contexto
MAX_IMAGEM = 5_000_000  # tamanho máximo da imagem em texto (base64)

INSTRUCOES = """Você é o CiênciasHelper, um assistente que ajuda estudantes com ciências
(biologia, física, química, geologia, astronomia e ciências da natureza em geral).

Regras:
- Responda em português do Brasil, de forma clara e amigável.
- Foque em perguntas de nível fundamental e médio. Use exemplos do dia a dia.
- Seja curto: de preferência até 3 parágrafos. Passe fórmulas só quando precisar.
- Se não souber ou a pergunta for ambígua, diga isso em vez de inventar.
- Se o aluno mandar uma imagem (esquema, foto, exercício), descreva o que vê
  e explique o conteúdo de ciências que aparece nela.
- Se a pergunta não tiver relação com ciências, explique educadamente que você
  só ajuda com essa matéria e convide a pessoa a perguntar algo de ciências.
- Não faça a lição de casa inteira pela pessoa: explique o raciocínio."""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    dados = request.get_json(silent=True) or {}
    historico = dados.get("mensagens", [])
    imagem = dados.get("imagem")

    # só aceita o formato esperado
    mensagens = [
        {"role": m["role"], "content": str(m["content"])[:2000]}
        for m in historico
        if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")
    ][-MAX_MENSAGENS:]

    if not mensagens or mensagens[-1]["role"] != "user":
        return jsonify({"erro": "Mande uma pergunta primeiro."}), 400

    modelo = MODELO

    if imagem:
        if not (isinstance(imagem, str) and imagem.startswith("data:image/") and len(imagem) < MAX_IMAGEM):
            return jsonify({"erro": "Imagem inválida ou muito grande."}), 400
        # a imagem vai junto só na última pergunta
        texto = mensagens[-1]["content"]
        mensagens[-1] = {
            "role": "user",
            "content": [
                {"type": "text", "text": texto},
                {"type": "image_url", "image_url": {"url": imagem}},
            ],
        }
        modelo = MODELO_IMAGEM

    def gerar():
        # manda a resposta em pedacinhos conforme a IA vai escrevendo
        try:
            fluxo = cliente.chat.completions.create(
                model=modelo,
                max_tokens=1500,
                messages=[{"role": "system", "content": INSTRUCOES}] + mensagens,
                stream=True,
            )
            for parte in fluxo:
                if parte.choices and parte.choices[0].delta.content:
                    yield parte.choices[0].delta.content
        except Exception as e:
            print("erro na API:", e)
            yield "⚠️ Erro técnico: " + str(e)[:300]

    return Response(stream_with_context(gerar()), mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True)
