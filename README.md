# Nvoip People Hub

Protótipo navegável do sistema de RH e Digital Office da Nvoip.

## Arquivos principais

- `index.html`: entrada rápida para abrir o protótipo.
- `outputs/nvoip-rh-platform.html`: protótipo navegável completo.
- `outputs/nvoip-people-hub-blueprint.md`: blueprint de produto, arquitetura, permissões e regras.
- `server.py`: servidor local com banco SQLite para testar o fluxo real em `localhost`.

## Teste local com banco zerado

O servidor local sobe em `http://localhost:5173` e cria o banco em `data/people_hub.local.sqlite`.

```powershell
C:\Users\guilh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe server.py --reset --port 5173
```

Use `--reset` quando quiser zerar tudo. O banco nasce só com o administrador inicial.

## Acesso de demonstração

- E-mail: `guilherme.faria@nvoip.com.br`
- Senha: não precisa nesta fase do protótipo.

No teste local, o administrador inicial entra direto. Os demais usuários são cadastrados no RH/DP, recebem um link de primeiro acesso que expira em 12 horas, criam senha e preenchem o cadastro obrigatório antes de acessar o People Hub.

## Atualizações recentes

- RH/DP separado do People Hub, com menu próprio.
- Cadastro de colaboradores centralizado no RH/DP, com busca, modal de cadastro/edição e link de primeiro acesso.
- Modelos de permissão por grupo: Colaborador, Líder, RH, Líder de RH, Diretor e Admin.
- Ponto, atestados, justificativas, banco de horas, férias e folha de pagamento no desenho do produto.
