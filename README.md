# Philips Pocket Zapper

PROMPT MESTRE — PHILIPS SMART REMOTE



CONTROLE REMOTO UNIVERSAL PARA PHILIPS 26PFL3404



VERSÃO: MASTER 1.0

PROJETO: PHILIPS REMOTE CONTROL

DISPOSITIVO-ALVO: Philips 26PFL3404

PLATAFORMA: Android

IDIOMA: Português brasileiro

OBJETIVO: Criar um aplicativo funcional de controle remoto por infravermelho (IR).



---



1. PAPEL DA INTELIGÊNCIA ARTIFICIAL



Atue como uma equipe sênior especializada em:



- Desenvolvimento Android.

- Kotlin e Android SDK.

- Comunicação por infravermelho (IR).

- Protocolos de controle remoto Philips.

- Engenharia reversa de sinais IR, quando legalmente e tecnicamente possível.

- Design UI/UX de aplicativos premium.

- Arquitetura de software.

- Testes de hardware e compatibilidade.



Você deverá desenvolver um aplicativo real, funcional, estável e pronto para instalação em dispositivos Android compatíveis.



Não desenvolva apenas um protótipo visual.



Todos os botões deverão possuir funcionalidades reais e estar conectados à camada de comunicação infravermelha.



2. IDENTIDADE DO PROJETO



Nome: Philips Remote



Descrição: Controle remoto digital para televisores Philips.



Criar uma experiência que reproduza a praticidade de um controle físico, aproveitando a tela sensível ao toque do celular.



O aplicativo deverá ser especializado inicialmente no modelo:



Philips 26PFL3404



A arquitetura deverá permitir adicionar outros modelos Philips futuramente.



3. TECNOLOGIA E ARQUITETURA



Utilize preferencialmente:



- Kotlin.

- Android Studio.

- Android SDK.

- Jetpack Compose para interface.

- Material Design 3 com personalização visual.

- ConsumerIrManager para transmissão infravermelha.

- Room ou armazenamento local para configurações.

- Arquitetura MVVM.

- Separação entre interface, lógica e comunicação IR.



Utilize recursos nativos do Android.



Não dependa de conexão com servidores para executar os comandos básicos do controle remoto.



O aplicativo deverá funcionar offline depois de instalado.



4. COMPATIBILIDADE COM INFRAVERMELHO



Esta é uma das partes mais importantes do projeto.



Antes de permitir qualquer comando, o aplicativo deverá verificar:



1. Se o dispositivo Android possui emissor infravermelho.

2. Se o hardware disponibiliza suporte ao ConsumerIrManager.

3. Se o dispositivo aceita transmissão de sinais IR.

4. Se a frequência necessária é suportada.

5. Se existe um perfil de controle compatível com a Philips 26PFL3404.



Utilizar as APIs nativas do Android para verificar a compatibilidade.



Caso o aparelho não tenha emissor infravermelho:



- Exibir aviso explicativo.

- Informar que o celular não possui hardware IR compatível.

- Não simular transmissão de sinais.

- Não apresentar comandos como enviados quando não foram enviados.

- Disponibilizar orientação sobre transmissores infravermelhos externos compatíveis.



IMPORTANTE:



Não afirmar que qualquer celular Android consegue controlar uma televisão por infravermelho.



Não confundir Wi-Fi, Bluetooth e infravermelho.



5. PROTOCOLO E CÓDIGOS PHILIPS



Desenvolver uma camada independente para gerenciamento dos comandos infravermelhos.



Pesquisar e identificar o protocolo efetivamente utilizado pelo controle original da Philips 26PFL3404.



Investigar a possibilidade de utilização dos protocolos Philips RC5 e RC6, sem presumir que qualquer um deles seja necessariamente o protocolo correto deste modelo.



Implementar:



- Frequência da portadora configurável.

- Sequências de pulsos e intervalos.

- Codificação dos comandos.

- Controle de repetição.

- Intervalo entre transmissões.

- Tratamento de comandos inválidos.



Os códigos deverão ser obtidos de fontes técnicas confiáveis, bancos de códigos compatíveis ou aprendizado de sinais utilizando hardware receptor adequado.



Não inventar códigos hexadecimais.



Não cadastrar comandos fictícios.



Manter os códigos organizados em um perfil específico:



Philips26PFL3404Profile.



Permitir atualizar o perfil sem precisar reconstruir toda a interface do aplicativo.



6. INTERFACE PRINCIPAL



Utilizar a imagem enviada pelo usuário como referência de organização e disposição dos controles.



Criar uma interface moderna, elegante, responsiva e intuitiva.



Identidade visual



- Fundo cinza-escuro ou grafite.

- Botões circulares.

- Ícones minimalistas.

- Elementos em branco.

- Azul Philips como cor de destaque.

- Botão de energia em vermelho.

- Sombras suaves.

- Efeitos táteis ao pressionar.

- Animações rápidas e discretas.



Evitar aparência de aplicativo genérico.



7. LAYOUT DO CONTROLE REMOTO



Organizar os componentes da seguinte maneira:



Cabeçalho



Exibir:



- Logotipo Philips Remote.

- Nome da televisão: Philips 26PFL3404.

- Indicador de compatibilidade IR.

- Ícone de configurações.



Área superior



Adicionar:



- Botão Favoritos.

- Botão Power.



O botão Power deverá transmitir o comando de ligar/desligar correspondente ao perfil da televisão.



Controle de canais



Adicionar:



- CH+.

- CH-.



Organizar os comandos verticalmente na lateral esquerda.



Controle direcional



Criar um grande controle circular central.



Disponibilizar:



- Seta para cima.

- Seta para baixo.

- Seta para esquerda.

- Seta para direita.

- Botão OK central.



Cada direção deverá possuir uma área de toque independente.



Adicionar feedback visual ao pressionar cada botão.



Controle de volume



Organizar na lateral direita:



- VOL+.

- VOL-.

- Mute.



Botões inferiores



Adicionar:



- MENU.

- VOLTAR.

- EXIT.

- Botões numéricos.

- Botão de opções.



8. TECLADO NUMÉRICO



Criar um teclado numérico expansível.



Disponibilizar:



0, 1, 2, 3, 4, 5, 6, 7, 8 e 9.



Incluir:



- Teclas de seleção direta de canais.

- Botão de confirmação.

- Botão de apagar.

- Botão para fechar o teclado.



A interface numérica deverá abrir em painel inferior ou modal elegante.



9. FUNÇÕES ADICIONAIS



Criar uma área de funções adicionais.



Disponibilizar, quando suportadas pelos códigos do modelo:



- Source/Input.

- TV.

- AV.

- HDMI.

- Info.

- Guide.

- Menu de imagem.

- Menu de som.

- Sleep.

- Mute.



Não presumir que todos os comandos estejam disponíveis.



Cada função deverá possuir seu respectivo código IR validado.



10. EXPERIÊNCIA DO USUÁRIO



Implementar:



- Vibração tátil opcional.

- Animação ao pressionar botões.

- Resposta visual de transmissão.

- Interface adaptada a diferentes tamanhos de tela.

- Orientação vertical.

- Botões grandes para facilitar o uso.

- Boa acessibilidade.

- Persistência das configurações.

- Inicialização rápida.

- Funcionamento offline.



Não bloquear a interface durante uma transmissão.



11. CONFIGURAÇÕES



Criar uma tela de configurações com:



- Modelo da televisão.

- Perfil de infravermelho.

- Frequência configurada.

- Teste de transmissão.

- Vibração ligada/desligada.

- Intensidade de feedback visual.

- Tema claro/escuro.

- Informações sobre compatibilidade.



Adicionar uma seção de diagnóstico para identificar problemas de transmissão.



12. SISTEMA DE DIAGNÓSTICO



Ao iniciar, executar verificações automáticas:



1. Verificar hardware IR.

2. Verificar disponibilidade da API.

3. Verificar suporte à frequência.

4. Verificar existência do perfil Philips.

5. Verificar disponibilidade dos códigos.

6. Verificar permissões necessárias.



Exibir um diagnóstico compreensível:



- Hardware IR disponível.

- Hardware IR indisponível.

- Perfil da TV carregado.

- Códigos não configurados.

- Transmissão não suportada.



IMPORTANTE: uma transmissão realizada não significa necessariamente que a televisão recebeu ou executou o comando. Não afirmar que a TV está ligada ou desligada sem confirmação independente.



13. ARQUITETURA DOS COMANDOS



Criar uma estrutura organizada para os comandos:



RemoteCommand:



- POWER

- VOLUME_UP

- VOLUME_DOWN

- MUTE

- CHANNEL_UP

- CHANNEL_DOWN

- UP

- DOWN

- LEFT

- RIGHT

- OK

- MENU

- BACK

- EXIT

- NUM_0 até NUM_9

- SOURCE

- INFO

- GUIDE



Criar uma interface de comunicação:



IrTransmitter.



Criar um serviço responsável por:



- Receber o comando.

- Localizar o código correspondente.

- Validar o perfil.

- Verificar a compatibilidade do hardware.

- Transmitir o sinal.

- Controlar repetição.

- Retornar o resultado técnico.



Separar completamente a lógica de transmissão da interface visual.



14. SEGURANÇA E QUALIDADE



O aplicativo deverá:



- Não solicitar permissões desnecessárias.

- Não coletar dados pessoais.

- Não exigir cadastro.

- Não exigir conta.

- Não depender de publicidade.

- Não transmitir dados pela internet sem necessidade.

- Armazenar as configurações localmente.



15. TESTES OBRIGATÓRIOS



Realizar testes para:



- Inicialização do aplicativo.

- Detecção de infravermelho.

- Disponibilidade do hardware.

- Carregamento do perfil Philips.

- Validação dos códigos.

- Transmissão individual.

- Repetição dos comandos.

- Navegação pela interface.

- Funcionamento em diferentes resoluções.

- Estabilidade.

- Uso offline.



Testar os comandos reais na televisão Philips 26PFL3404 quando houver hardware compatível disponível.



Não declarar testes físicos concluídos sem executá-los.



16. ENTREGA DO PROJETO



Entregar:



1. Projeto Android completo.

2. Código-fonte Kotlin.

3. Interface Jetpack Compose.

4. Arquitetura organizada.

5. Perfil Philips 26PFL3404.

6. Camada de transmissão IR.

7. Diagnóstico de hardware.

8. Documentação técnica.

9. APK de instalação, quando o ambiente permitir.

10. Instruções de compilação no Android Studio.



O projeto deverá ser organizado, documentado e preparado para manutenção.



17. REGRA FUNDAMENTAL



Não entregue somente uma tela bonita com botões que não fazem nada.



Não simule infravermelho.



Não invente compatibilidade.



Não invente códigos de controle remoto.



Não prometa que funcionará em celulares sem emissor IR.



Se não houver informações suficientes para confirmar o protocolo ou os códigos da Philips 26PFL3404, identificar exatamente o que está faltando e implementar uma estrutura preparada para receber os códigos corretos.



RESULTADO FINAL



Criar um controle remoto digital Philips, com interface premium inspirada na referência visual enviada, arquitetura Android nativa, transmissão infravermelha real e suporte inicial dedicado à televisão Philips 26PFL3404.



A prioridade absoluta é:



FUNCIONALIDADE REAL + COMPATIBILIDADE + ESTABILIDADE + DESIGN PREMIUM.

This project was built with [Lovable](https://lovable.dev).

**Live app**: https://philips-pocket-zapper.lovable.app

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/d74bae36-e3e3-4dae-a4d0-ce9a07efa174).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
