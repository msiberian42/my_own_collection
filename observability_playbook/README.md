# Observability playbook

Плейбук создаёт три VM в Yandex Cloud, добавляет их в динамический inventory,
дожидается доступности по SSH и запускает на каждой VM соответствующую Ansible-роль.

## Перед запуском

1. В `main.yml` проверьте параметры VM, subnet/image ID, публичный SSH-ключ и путь
   к соответствующему приватному ключу, cloud-id.
2. Установите роли в каталог `roles`:

   ```bash
   ansible-galaxy role install -r requirements.yml -p roles
   ```

3. Убедитесь, что `yc` установлен и авторизован в профиле с нужным `folder-id`.

## Запуск

Из этого каталога выполните:

```bash
ansible-playbook -i localhost main.yml
```

Ansible загружает `yc_instance` напрямую из исходной collection в репозитории
через `ansible.cfg`; отдельная установленная копия collection не требуется.
