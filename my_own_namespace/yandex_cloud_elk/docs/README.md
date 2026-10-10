# Коллекция `my_own_namespace.yandex_cloud_elk`

Коллекция содержит модуль `my_own_module`, который создаёт файл с заданным содержимым, и роль `single_task_role`, которая вызывает этот модуль.

## Установка из исходников

Из корня репозитория соберите и установите коллекцию:

```bash
ansible-galaxy collection build my_own_namespace/yandex_cloud_elk
ansible-galaxy collection install my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz -p ./collections
```

## Запуск примера

Playbook `single_task_playbook/main.yml` запускается локально и создаёт `/tmp/my_module.txt` с текстом `Дефолтный контент`:

```bash
ANSIBLE_COLLECTIONS_PATH="$PWD/collections" ansible-playbook \
  -i localhost, \
  my_own_namespace/yandex_cloud_elk/single_task_playbook/main.yml
```

Путь и текст можно переопределить переменными роли:

```bash
ANSIBLE_COLLECTIONS_PATH="$PWD/collections" ansible-playbook \
  -i localhost, \
  my_own_namespace/yandex_cloud_elk/single_task_playbook/main.yml \
  -e 'single_task_role_path=/tmp/custom.txt' \
  -e 'single_task_role_content=Привет'
```

Модуль поддерживает check mode; повторный запуск с теми же параметрами не должен менять файл.
