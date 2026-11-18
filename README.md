# Campus SkillSwap

A student skill marketplace built with Python, Django 5.2 and SQLite. All application views are function-based. The interface is English; the learning guide is Chinese.

## 在 VS Code 中启动（macOS）

1. 用 VS Code 的 **File → Open Folder** 打开本项目文件夹。
2. 按提示安装 Microsoft **Python** 和 **Python Debugger** 扩展。
3. 打开 Terminal → New Terminal，首次安装运行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

当前电脑已经创建 `.venv`、安装依赖并完成迁移，因此可以直接运行：

```bash
source .venv/bin/activate
python manage.py runserver
```

4. 浏览器访问 http://127.0.0.1:8000/ 。注册自己的账号后即可发帖。
5. 在命令面板选择 **Python: Select Interpreter → .venv/bin/python**。运行调试面板选择 **Campus SkillSwap: Django**，按 F5 即可调试。若终端服务器仍在运行，先按 Ctrl+C，以免端口冲突。
6. 在 `skills/views.py` 左侧点击设置断点，浏览器打开对应页面，观察 `request`、表单和查询结果。

Windows 下创建环境使用 `py -m venv .venv`，PowerShell 激活使用 `.venv\Scripts\Activate.ps1`，并在 VS Code 选择 `.venv\Scripts\python.exe`。

## 管理后台

在另一个已激活虚拟环境的终端执行：

```bash
python manage.py createsuperuser
```

自己设置管理员用户名和密码，再访问 http://127.0.0.1:8000/admin/ 。不提供默认管理员密码。后台支持用户、技能帖、评价的管理，以及分类筛选和搜索。

## 已实现

- 注册、登录、POST 退出；Django 哈希保存密码并验证密码强度。
- 公开技能列表与详情，每页 9 条，标题／分类搜索及分类筛选。
- 登录用户创建技能帖；只有帖主可以编辑和删除。
- 个人 dashboard 仅显示自己的帖。
- 1–5 分评价，每人每帖一条；再次提交更新评价；可以删除自己的评价。
- 禁止评价自己的技能，显示平均评分；删除技能时关联评价也删除。
- Bootstrap 响应式布局、自定义配色、表单错误提示、空状态。

**范围说明：**当前没有订单、聊天、付款、校园邮箱认证或服务完成记录，无法验证用户是否为在校学生或确实使用过服务。评价页面明确标注“使用情况未经验证”。位置与交换条件是文本信息，不会自动完成交易。Bootstrap 从 CDN 加载，需要网络；自定义 CSS 在本地。

## 项目结构

```text
manage.py                     Django 命令入口
campus_skillswap/              项目配置、主路由、WSGI/ASGI
skills/
  models.py                   Skill、Review 与数据库约束
  forms.py                    注册、登录、技能及评价表单
  views.py                    函数视图、搜索、权限判断
  urls.py                     页面地址
  admin.py                    管理后台
  tests.py                    功能与权限测试
  migrations/                 数据库版本记录
 templates/                   基础布局、可复用片段和各页面
static/css/style.css          自定义样式
.vscode/                      Python 解释器、扩展和调试配置
docs/学习指南.md              逐步中文教程
```

## 检查与测试

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
python -m pip check
```

测试使用独立的临时数据库，不会清空开发数据库。

## 配置

默认是本地开发模式。SQLite 数据保存在 `db.sqlite3`，随机开发密钥保存在 `.dev-secret-key`，两者都被 Git 忽略。不要提交数据库或密钥。开发密钥首次启动自动生成，后续复用。

正式部署前应配置 `DJANGO_SECRET_KEY`、`DJANGO_DEBUG=0`、逗号分隔的 `DJANGO_ALLOWED_HOSTS`，设置 HTTPS、安全 Cookie、静态资源托管及数据库备份，并执行 `python manage.py check --deploy`。当前配置与 `runserver` 用于本地开发，不是生产部署方案。

详细步骤见 [中文学习指南](docs/学习指南.md)。

## Render 公网部署

已支持本地 SQLite、Render PostgreSQL 自动切换，并提供 Gunicorn、WhiteNoise、构建与启动脚本。按照 [Render 网页部署指南](docs/Render部署.md) 在 VS Code 上传代码后，通过 Render 网页创建数据库及 Web Service，无需自己输入终端命令。云端依赖 `DJANGO_SECRET_KEY` 和 `DATABASE_URL`，默认关闭 DEBUG；自动读取 Render 分配的主机名。未设置数据库时会拒绝启动，避免误用临时 SQLite 丢失数据。
