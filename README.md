![alt text](https://github.com/Horusprg/uxtracking.com/blob/main/UX-Tracking%20Banner.png)
 # UX-Tracking: Web Server
Repositório do servidor web do framework [UX-Tracking: User eXperience Tracking](https://uxtracking.andrepereira.eng.br/)

## Tabela de conteúdos

*  [Pré Requisitos](#pré-requisitos)
*  [Topologia](#topologia)
*  [Ambiente de desenvolvimento](#ambiente-de-desenvolvimento)
*  [Utilização](#utilização)
* * [Distribuição](#distribuição)
* * [Ambiente de desenvolvimento](#ambiente-de-desenvolvimento)
*  [Módulos](#Módulos)
* * [Cliente](#cliente)
* * * [Rastreamento de mouse](#rastreamento-de-mouse)
* * * [Rastreamento ocular](#rastreamento-ocular)
* * * [Keylogging](#keylogging)
* * * [Think aloud](#Transcrição-de-voz)
* * [Armazenamento](#armazenamento)
* * [Web App](#Web-App)
* * [Visualizador](#Visualizador)
* * * [Reprodução de sessão](#reproducao-de-sessao)
* * * [Rastreamento ocular](#rastreamento-ocular)
* * * [Análise de métricas](#analise-de-metricas)
* * * [Download do estudo](#download-do-estudo)
*  [Tecnologias](#tecnologias)

 ## Pré-requisitos

📃 Para a abertura dos projetos contidos neste repositório, estabelecem-se os seguintes requisitos:

*  [Python (Utilizada versão 3.11.4)](https://www.python.org/)
*  [Visual Studio Code](https://code.visualstudio.com/download)
*  [Google Chrome](https://www.google.com/chrome/)

## Topologia

- [static](https://github.com/Colab-UNIRIO-UFPA/uxtracking.com/tree/main/static) - `Arquivos estáticos carregados pelo flask no servidor`
- [templates](https://github.com/Colab-UNIRIO-UFPA/uxtracking.com/tree/main/templates) - `Templates (html + css + js) das páginas renderizadas pelo flask`
  - base.html - `Template base para as demais páginas`
  - dashboard.html - `Não implementado`
  - data_analysis.html - `Página de análise dos dados`
  - data_filter.html - `Página de coletas`
  - data_view.html - `Página de visualização dos dados`
  - email.html - `Email enviado para recuperação de senha do usuário`
  - forgot_pass.html - `Página de recuperação de senha`
  - index.html - `Página principal`
  - login.html - `Página de login`
  - register.html - `Página de registro`
- [.gitignore](https://github.com/Colab-UNIRIO-UFPA/uxtracking.com/tree/main/.gitignore) - `Lista de arquivos ignorados no commit`
- [README.md](https://github.com/Colab-UNIRIO-UFPA/uxtracking.com/tree/main/README.md) - `Documentação`
- [app.py](https://github.com/Colab-UNIRIO-UFPA/uxtracking.com/tree/main/app.py) - `Script python para declarar a aplicação web`
- [functions.py](https://github.com/Colab-UNIRIO-UFPA/uxtracking.com/tree/main/functions.py) - `Script python de funções chamadas pela aplicação`
- [requirements.txt](https://github.com/Colab-UNIRIO-UFPA/uxtracking.com/tree/main/requirements.txt) - `Arquivo de requisítos para a aplicação`
- [wsgi.py](https://github.com/Colab-UNIRIO-UFPA/uxtracking.com/tree/main/wsgi.py) - `Script wsgi`

## Ambiente de desenvolvimento
1. Abra o VSCode, crie um ambiente virtual e ative-o
   ```bash
   python -m venv venv
   ```
   Ativar o ambiente virtual:
   | Sistema   | Shell       | Comando                           |
   | :---------- | :--------- | :---------------------------------- |
   | Windows | CMD | `venv/scripts/activate.bat` |
   | Windows | PowerShell | `venv/bin/Activate.ps1` |
   | Linux | bash | `source venv/bin/activate` |
   
2. Faça a instalação das bibliotecas necessárias
   ```bash
   pip install -r requirements.txt
   ```
3. Crie um arquivo `.env` e adicione as seguintes variáveis de ambiente no seu arquivo .env

     `SECRET_KEY` - Chave secreta da aplicação Flask
     
     `MAIL_NAME` - Nome de usuário do serviço de email
     
     `MAIL_PASSWORD` - Senha do serviço de email
     
     `URI_DATABASE` - String de conexão com a base de dados mongo
4. Adicione o modelo BERTimbau ao código, faça o [download](https://drive.google.com/drive/folders/1gE6JdtHgSw9GOqtS-u8xs0x9hjxZwwWA?usp=sharing) da pasta e insira-a nos arquivos da aplicação.

5. Para iniciar a aplicação, basta executar o arquivo app.py pelo vscode apertando a tecla `F5` ou pelo terminal

6. A aplicação estará rodando em dois IP's, um somente na máquina executada e outro na rede local.

## Utilização
Para utilizar a ferramenta, pode-se fazer o uso da aplicação distribuída ou no ambiente de desenvolvimento criado.
### Distribuição
Para utilização da ferramenta distribuída, acesse o site da [UX-Tracking](https://uxtracking.andrepereira.eng.br), faça seu cadastro e faça o download da extensão disponibilizada para as coletas no seu navegador.

1. Após o download da extensão UX-Tracking, faça sua descompressão e ative o [modo de programador no navegador Chrome](https://www.techtudo.com.br/noticias/2015/01/como-entrar-no-modo-desenvolvedor-do-google-chrome.ghtml)
2. Carregue a extensão apertando o botão `Carregar expandida` na aba de extensões
3. Faça seu login apertando no botão da extensão carregada e estará pronta pra utilizar
4. Os dados coletados serão armazenados em nosso servidor e você poderá acessá-los diretamente na página da aplicação, bem como processar, visualizar e filtrar suas coletas.
   
### Ambiente de desenvolvimento
Para utilização no ambiente de desenvolvimento construído, acesse um dos IP's gerados pelo servidor. Para carregar a extensão que irá apontar para o IP do servidor:
1. Acesse o arquivo `background.js` que está na pasta `UX-Tracking Extension`
2. Na linha `const serverUrl = "<SEU_IP";` insira o IP gerado pelo servidor
3. Realize os passos para carregar a extensão da pasta `UX-Tracking Extension`
4. A extensão estará apontando para o seu servidor local e você poderá realizar todas as operações que quiser
## Módulos
A UX-Tracking é constituída de 3 módulos: Cliente, Web App e visualizador. Os três módulos são responsáveis respectivamente por coletar dados de interação; organizar e armazenar; e prover formas de visualizar os dados capturados. Os módulos são descritos a seguir.
### Cliente
Desenvolvido como uma extensão do navegador Google Chrome utilizando Javascript, este módulo é responsável por capturar - do lado cliente - as interações dos desenvolvedores, no papel de usuários do portal, a partir das técnicas de rastreamento do mouse, do olho e do teclado, além de transcrição de fala. As versões do módulo cliente encontram-se no diretório `clients`.


#### Rastreamento de mouse
A captura de interações do mouse contempla 4 tipos de interação:
* Movimento
* Clique
* Pausa
#### Rastreamento ocular
O rastreamento ocular é realizado por meio de uma versão modificada do [WebGazer](https://github.com/brownhci/WebGazer) (Copyright © 2016-2021, Brown HCI Group).
#### Keylogging
A extensão também pode capturar entradas de teclado, registrando a digitação de caracteres.
#### Transcrição de voz
Utilizando o [WebKit Voice Recognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition), o módulo cliente é capaz de capturar voz, incluindo pausas, transcrevendo e enviando como entradas de texto.

### Web App
Após o registro do usuário, a aplicação web, através do login do usuário, disponibilizará os dados coletados, de forma condensada, para o usuário através de um CSV com data e hora da coleta. Os dados do CSV incluem sites visitados, voz, rastreio do mouse e rastreio dos olhos. 

### Pós-processamento de dados
A aplicação conta, atualmente, com quatro módulos de pós-processamento de dados de dados, sendo eles:
#### K-means clustering
Este componente, ou submódulo, reproduz individualmente cada amostra capturada, conforme a escolha do usuário permitindo a visualização dos dados clusterizados do modelo de agrupamento k-means.
#### Agglomerated-Cluster
Este componente produz um agrupamento hierárquico de clusters, conforme a entrada do usuário, e é um método de análise de cluster que busca construir uma hierarquia de clusters.
#### Mean-Shift-Clustering
Este componente gera o deslocamento médio do dado de entrada escolhido pelo usuário.

### Visualizador
A aplicação desktop é responsável por permitir a visualização dos dados. Possui três recursos de visualização, descritos a seguir:
#### Reprodução de sessão
Este componente, ou submódulo, reproduz individualmente cada amostra capturada, permitindo a visualização quadro-a-quadro dos movimentos do desenvolvedor registrados a partir das técnicas de rastreamento domouse e do olho. Para a composição da visualização, o módulo utiliza captura de telas registradas durante a interação, e sobre essas posiciona pontos e linhas contínuas representando o caminho percorrido e ações realizadas pelo usuário.
#### Mapa de calor
Este componente produz um mapa de calor para o rastreamento do mouse e do olho. É possível a geração de mapas individuais ou de grupo de desenvolvedores. As representações são constituídas de capturas de tela sobrepostas e encontradas nos dados capturados, de forma a reproduzir a tela da aplicação. Este componente permite a detecção de áreas de interesse, desvios de atenção, zonas não visualizadas, entre outras possibilidades.
#### Análise de métricas

#### Download do estudo
O procedimento:<br/>
1º - Acesse o link -> https://uxtracking.andrepereira.eng.br/ <br/>
2º - Clique no botão "Download Research" <br/>
Após os passos acima, o download do zip da pasta Samples será iniciado. <br/>
Para o download da ferramenta de visualização, basta clicar no botão "Ferramenta de Pós-processamento" e o download será iniciado. <br>
## Tecnologias
* [JavaScript](https://www.javascript.com/)
* [Python](https://www.python.org/)
* [HTML](https://developer.mozilla.org/pt-BR/docs/Web/HTML)
* [CSS](https://developer.mozilla.org/pt-BR/docs/Web/CSS)
