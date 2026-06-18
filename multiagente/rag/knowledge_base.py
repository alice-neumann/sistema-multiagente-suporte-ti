"""Base de conhecimento para o sistema de suporte de TI."""

IT_SUPPORT_DOCUMENTS = [
    {
        "id": "ti_falha_conexao_rede",
        "title": "Diagnóstico de Falha de Conexão de Rede e Internet",
        "content": """
        1. Verifique se o cabo de rede está conectado corretamente no computador e na parede, ou se o Wi-Fi está ativado.
        2. Abra o Prompt de Comando (menu Iniciar > cmd).
        3. Para redefinir a conexão e limpar conflitos de rede, digite os seguintes comandos, pressionando Enter após cada um:
           - ipconfig /release
           - ipconfig /renew
           - ipconfig /flushdns
        4. Após executar os comandos, digite 'ping 8.8.8.8' e pressione Enter.
        5. Se HOUVER resposta ao ping, mas os sites continuarem sem abrir, será necessário abrir um chamado para a TI configurar o DNS manualmente.
        6. Se NÃO HOUVER resposta ao ping, reinicie o computador. Se o problema persistir, o cabo ou o ponto de rede podem estar com defeito e a TI deve ser acionada.
        """,
        "category": "redes"
    },
    {
        "id": "ti_reset_senha",
        "title": "Procedimento de Redefinição de Senha",
        "content": """
        1. Acesse a tela de login do sistema desejado.
        2. Clique na opção 'Esqueci minha senha' ou 'Primeiro Acesso' localizada abaixo do campo de senha.
        3. Insira o CPF ou número de matrícula e clique em 'Enviar'.
        4. Acesse o e-mail corporativo ou verifique o SMS do celular para pegar o código de verificação recebido.
        5. Insira o código de verificação na tela do sistema.
        6. Crie uma nova senha contendo no mínimo 8 caracteres, incluindo letras e números.
        """,
        "category": "acessos"
    },
    {
        "id": "ti_limpeza_cache_navegador",
        "title": "Resolução de Erros de Exibição em Sites (Limpeza de Cache)",
        "content": """
        1. Com o navegador aberto, pressione as teclas 'Ctrl + Shift + Del' simultaneamente.
        2. Na janela de Limpeza de Dados, altere o período para 'Todo o período' ou 'Desde o começo'.
        3. Marque apenas as opções 'Cookies e outros dados do site' e 'Imagens e arquivos armazenados em cache'.
        4. Certifique-se de que a opção de senhas esteja desmarcada.
        5. Clique em 'Limpar dados'.
        6. Feche todas as janelas do navegador, abra novamente e acesse o site.
        """,
        "category": "software"
    },
    {
        "id": "ti_computador_lento",
        "title": "Diagnóstico Básico para Computador Lento",
        "content": """
        1. Clique no menu Iniciar, clique no botão de Energia e selecione 'Reiniciar' (desligar apenas o monitor não reinicia o sistema).
        2. Pressione 'Ctrl + Shift + Esc' para abrir o Gerenciador de Tarefas e feche os aplicativos ou abas do navegador que não estão em uso.
        3. Pressione as teclas Windows + R, digite '%temp%' e pressione Enter.
        4. Na pasta que abrir, pressione 'Ctrl + A' para selecionar todos os arquivos temporários e exclua-os. Caso o sistema informe que um arquivo está em uso, clique em 'Ignorar'.
        """,
        "category": "hardware"
    }
]

def get_all_documents():
    """Retorna todos os documentos da base de conhecimento."""
    return IT_SUPPORT_DOCUMENTS