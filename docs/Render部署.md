# Render 网页部署（不用自己输入终端命令）

本地使用 SQLite；Render 使用独立的 PostgreSQL。现有本地账号和帖子不会自动上传。生产环境通过环境变量配置，禁止将数据库 URL 和密钥放入 GitHub。

## 1. 在 VS Code 上传配置

打开左侧 Source Control，检查变更。消息填写 `Prepare Render deployment`，点击 Commit。如询问是否暂存这些更改，确认本次部署文件；再点击 Sync Changes（或 Push）。不要使用 Discard Changes。代码必须上传后 Render 才能读取。

## 2. 在 Render 创建数据库

登录 Render Dashboard → New → Postgres。

- Name：`campus-skillswap-db`
- Region：选择一个区域，并记住，Web Service 使用同一区域。
- 数据库凭据可由 Render 自动生成。
- Instance Type：选择 Free（如果当前账户提供该选项）。提交前确认显示的费用。

创建完成后，在数据库详情找到 `Internal Database URL`。它包含密码，只粘贴到 Render 的 DATABASE_URL 环境变量中，不要发聊天截图、写进代码或提交 GitHub。

免费 Render PostgreSQL 在创建后 30 天过期，应确保覆盖作业评阅期。免费 Web Service 也有休眠和使用额度限制。以账户页面显示的条款及费用为准。

## 3. 创建 Web Service

New → Web Service → Git Provider → 连接自己的 GitHub 仓库 `Django-Project`。

| 字段 | 填写 |
| --- | --- |
| Name | campus-skillswap（重名时可加后缀） |
| Language | Python |
| Branch | main |
| Region | 与数据库相同 |
| Root Directory | 留空，manage.py 在仓库根目录 |
| Build Command | `bash build.sh` |
| Start Command | `bash start.sh` |
| Instance Type | Free（确认不是收费规格） |

根目录 `.python-version` 已指定 Python 3.13，无需另填 PYTHON_VERSION。如果已有这个环境变量，删除冲突值或使用兼容的完整 3.13.x 版本。

## 4. Environment Variables

| Key | Value |
| --- | --- |
| DJANGO_DEBUG | `0` |
| DJANGO_SECRET_KEY | 使用 Render 的 Generate 随机生成，并保持固定 |
| DATABASE_URL | 刚创建的 PostgreSQL 的 Internal Database URL |

Render 自动设置 RENDER 和 RENDER_EXTERNAL_HOSTNAME。代码自动允许当前服务的实际域名，无需填写通配符 ALLOWED_HOSTS。自定义域名以后另行配置。

确认配置和费用后，由你点击 Deploy Web Service。构建会安装依赖、收集样式并迁移 PostgreSQL；启动使用 Gunicorn。无需上传 db.sqlite3，无需在网页终端手动建表。

## 5. 验证

部署成功后，点击 Render 提供的 https 地址。注册两个新的测试账号，测试发帖、搜索、评价和退出。数据库起初为空属正常。本地旧账号不会出现在云端。

再执行 Manual Deploy → Deploy latest commit，部署后重新登录，确认帖子仍在。源码仍由 GitHub 管理，线上数据由 PostgreSQL 保存。

管理员账号不是网站上线的前提。普通注册账号不是超级管理员；后续确有后台管理需要时再单独安全创建，绝不把管理员密码写进仓库或构建脚本。

## 6. 出错时

- Build failed：查看 Logs 中第一条实际错误，不只看最后一行。
- 数据库连接失败：检查 DATABASE_URL、数据库状态及两个服务的区域。不要公开连接串。
- Missing DJANGO_SECRET_KEY / DATABASE_URL：补上对应环境变量，再部署。
- DisallowedHost：核对 RENDER_EXTERNAL_HOSTNAME 是否由 Render 提供，以及是否运行最新代码。
- 样式缺失：检查 collectstatic 构建日志和 WhiteNoise 配置。
- 首页加载慢：免费 Web Service 休眠后首次访问可能需要启动。

本地已验证配置、静态文件和应用测试；真正的 PostgreSQL 连通性和 Render 构建，必须在服务创建并部署后验证。

官方参考：https://render.com/docs/deploy-django 、https://render.com/docs/free 、https://render.com/docs/python-version 。
