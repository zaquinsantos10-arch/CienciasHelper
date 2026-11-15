import os

from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, stream_with_context

load_dotenv()

app = Flask(__name__)
cliente = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODELO = os.getenv("MODELO", "llama-3.3-70b-versatile")
MAX_MENSAGENS = 20  # limite do histórico pra não estourar o contexto

INSTRUCOES = """Você é o CiênciasHelper, um assistente que ajuda estudantes com ciências
(biologia, física, química, geologia, astronomia e ciências da natureza em geral).

Regras:
- Responda em português do Brasil, de forma clara e amigável.
- Foque em perguntas de nível fundamental e médio. Use exemplos do dia a dia.
- Seja curto: de preferência até 3 parágrafos. Passe fórmulas só quando precisar.
- Se não souber ou a pergunta for ambígua, diga isso em vez de inventar.
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

    # só aceita o formato esperado
    mensagens = [
        {"role": m["role"], "content": str(m["content"])[:2000]}
        for m in historico
        if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")
    ][-MAX_MENSAGENS:]

    if not mensagens or mensagens[-1]["role"] != "user":
        return jsonify({"erro": "Mande uma pergunta primeiro."}), 400

    def gerar():
        # manda a resposta em pedacinhos conforme a IA vai escrevendo
        try:
            fluxo = cliente.chat.completions.create(
                model=MODELO,
                max_tokens=700,
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
