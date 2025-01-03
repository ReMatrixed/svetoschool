<p align="center"><img src="https://raw.githubusercontent.com/ReMatrixed/docs/refs/heads/main/img/rounded/svetoschool-logo-rounded.png" width=256></p>
<h1 align="center">SvetoSchool</h1><p align="center"><i>Многофункциональная информационная платформа</i></p>

# Начало работы
Для запуска платформе требуются базы данных *PostgreSQL* и *Redis*. Рекомендуемым способом для их развертывания является *Docker*. 

> [!TIP]
> *Docker* (а именно *Docker Compose*) также советуется использовать для развертывания самой платформы, так как это самый стабильный способ, который был протестирован на моей инфраструктуре и доказал свою надёжность. В папке *docker* вы сможете найти файл примера (docker-compose.yml), а также файлы настроек.

> [!WARNING]
> Обратите внимание: все данные, применяемые для настройки платформы, требуется указывать в файле .env или с помощью переменных среды (environment variables).