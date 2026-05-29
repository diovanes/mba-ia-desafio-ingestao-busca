from search import search_prompt


def main():
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Chat iniciado. Digite 'sair' para encerrar.\n")

    while True:
        pergunta = input("PERGUNTA: ").strip()

        if pergunta.lower() in ("sair", "exit", "quit"):
            break

        if not pergunta:
            continue

        resposta = chain.invoke(pergunta)
        print(f"\nRESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()