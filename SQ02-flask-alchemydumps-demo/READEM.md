

## 使用示例

备份数据

    python manage.py alchemydumps create

显示已经备份的数据

    python manage.py alchemydumps history

恢复备份

    python manage.py alchemydumps restore -d 20141115172107

删除备份

    python manage.py alchemydumps remove -d 20141115172107


`autoclean`命令作用

- It keeps all the backups from the last 7 days.
- It keeps the most recent backup from each week of the last month.
- It keeps the most recent backup from each month of the last year.
- It keeps the most recent backup from each remaining year.


---

- alchemydumps github: https://github.com/cuducos/alchemydumps

