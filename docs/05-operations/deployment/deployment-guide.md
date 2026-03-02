# 部署说明（FJBMS Cloud）

- status: approved
- owner: <owner>
- last_updated: 2026-02-14
- source: `doc/部署说明.md`
- version: v1.0.0

> 本文是迁移后的主维护版本。

## 数据库部署


```bash
mkdir -p /www/fjia/data/pgdata  

docker run --name fjiacloud-db -d \
  --restart always \
  -p 5432:5432 \
  -e TZ=Asia/Shanghai \
  -e POSTGRES_DB=fjiacloud \
  -e POSTGRES_USER=fjia \
  -e POSTGRES_PASSWORD=<REPLACE_WITH_SECURE_PASSWORD> \
  -v /www/fjia/data/pgdata:/var/lib/postgresql/data \
  registry.cn-hangzhou.aliyuncs.com/thingspanel/timescaledb:14

```
