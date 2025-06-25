# 🛠️ Dev Notes – DataPulse Backend

Este arquivo contém boas práticas, dicas e comandos úteis para desenvolver com Django + Docker neste projeto.

---

## 🚀 Comandos úteis

### Subir o ambiente com Docker

```bash
docker compose up --build
```

### Acessar o terminal da aplicação Django

```bash
docker compose exec web bash
```

### Criar migrações (sempre que um modelo mudar)

```bash
docker compose exec web python manage.py makemigrations
```

### Aplicar migrações no banco de dados

```bash
docker compose exec web python manage.py migrate
```

### Criar um superusuário (admin)

```bash
docker compose exec web python manage.py createsuperuser
```

## 📌 Boas práticas e pegadinhas

1. Sempre crie as migrações antes de migrar
   Se você criar um modelo novo (como User) e tentar rodar migrate direto sem makemigrations, o Django não vai entender que precisa criar aquela tabela, e isso causará erros de “tabela não existe”.

👉 Sempre execute:

```bash
docker compose exec web python manage.py makemigrations
```

2. Ordem correta quando criar modelo de usuário customizado
   Se estiver usando AUTH_USER_MODEL, você precisa registrar o modelo antes de rodar qualquer migração.
   Caso contrário, o app admin tentará usar o modelo padrão do Django.

3. Resetando o banco de dados (em dev)
   Se algo der muito errado nas migrações:

```bash
docker compose down -v       # apaga containers e banco
rm -rf backend/*/migrations  # apaga todas as migrações (exceto __init__.py)
```

Depois, recrie:

```bash
docker compose up --build
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

## ✅ Checklist para criar um novo app Django

1. docker compose exec web python manage.py startapp nome_do_app

2. Adicionar o app no INSTALLED_APPS

3. Criar modelos, serializers, views e rotas

4. Rodar makemigrations e migrate
