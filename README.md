# calorites-tg-bot

* В github actions собирается докер образ и пушится в docker hub https://hub.docker.com/r/tfonferm/calorites-tg-bot/tags
* Секреты лежат на виртуальной машине в .env файле. SSH к ней лежит в секретах репозитория.
* Деплой на виртуальный хост в yandex cloud происходит через github actions автоматически.