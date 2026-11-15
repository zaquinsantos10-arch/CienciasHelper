# 🔬 CiênciasHelper

Chatbot de IA que responde dúvidas simples e médias de ciências (biologia, física, química, geologia e astronomia). Feito com Flask e a API da Anthropic.

## Recursos

- Respostas em tempo real (o texto aparece aos poucos)
- Tema claro/escuro (segue o do sistema e lembra a sua escolha)
- Botão para limpar a conversa

## Como rodar

1. Clone o repositório e entre na pasta:
   ```bash
   git clone https://github.com/SEU_USUARIO/CienciasHelper.git
   cd CienciasHelper
   ```

2. Crie o ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate   # no Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copie o `.env.example` para `.env` e coloque sua chave da API (pegue em https://console.anthropic.com):
   ```bash
   cp .env.example .env
   ```

4. Rode:
   ```bash
   python app.py
   ```
   e abra http://127.0.0.1:5000

## Estrutura

```
app.py              # servidor Flask e chamada à API
templates/index.html # interface do chat
requirements.txt
.env.example
```

## Personalizando

O comportamento do bot está na variável `INSTRUCOES` no `app.py`. Dá pra mudar o tom, o nível das respostas ou as matérias.

## Observação

Nunca suba o arquivo `.env` pro GitHub (ele já está no `.gitignore`).
