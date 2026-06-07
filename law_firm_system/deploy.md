# 小型律所管理系统 - 阿里云 Linux 服务器部署手册

> 适用于：阿里云轻量应用服务器 / ECS（2GB 内存）  
> 操作系统：CentOS 7+ / Ubuntu 20.04+ / Alibaba Cloud Linux 3  
> 最后更新：2026-06-06

---

## 一、服务器准备

### 1.1 购买与登录

1. 登录阿里云控制台，购买 **轻量应用服务器**（2核 2GB 内存即可）。
2. 选择操作系统镜像：**Alibaba Cloud Linux 3** 或 **CentOS 7.9**。
3. 在控制台重置 root 密码，并记录 **公网 IP**。
4. 本地通过 SSH 登录：
   ```bash
   ssh root@你的服务器公网IP
   ```

### 1.2 阿里云安全组 / 防火墙放通

部署前务必先放行端口：

| 端口 | 用途 | 授权对象 |
|------|------|----------|
| 22 | SSH 远程登录 | 你的办公 IP |
| 5066 | 律所系统（Flask/Gunicorn） | 0.0.0.0/0 或你的办公 IP |
| 80 | HTTP（Nginx 反向代理，可选） | 0.0.0.0/0 |
| 443 | HTTPS（Nginx + SSL，可选） | 0.0.0.0/0 |

**轻量应用服务器防火墙配置：**
```bash
# 登录服务器后执行
firewall-cmd --permanent --add-port=5066/tcp
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload
```

**或在阿里云控制台 → 安全组 / 防火墙 → 手动添加规则。**

---

## 二、环境安装

### 2.1 安装 Python 3 和 pip

```bash
# CentOS / Alibaba Cloud Linux
yum install -y python3 python3-pip

# Ubuntu
apt update
apt install -y python3 python3-pip
```

### 2.2 创建项目目录并上传代码

```bash
mkdir -p /opt/law_firm_system
cd /opt/law_firm_system
```

**上传方式（任选一种）：**

**方式 A：本地打包上传（推荐）**
```bash
# 在 Windows 本地，进入项目目录，打包
# 律所项目目录: E:\AI学习\AI项目\小型律所管理系统\law_firm_system
cd "E:\AI学习\AI项目\小型律所管理系统"
tar -czvf law_firm_system.tar.gz law_firm_system

# 使用 scp 上传到服务器
scp law_firm_system.tar.gz root@你的服务器公网IP:/opt/

# 然后在服务器上解压
ssh root@你的服务器公网IP
cd /opt
tar -xzvf law_firm_system.tar.gz
```

**方式 B：直接 Git 拉取（如果你推到了 GitHub/Gitee）**
```bash
cd /opt
git clone https://你的仓库地址.git law_firm_system
```

### 2.3 安装 Python 依赖

```bash
cd /opt/law_firm_system
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

依赖清单：
- Flask 2.3.3
- Flask-SQLAlchemy 3.1.1
- python-docx 1.1.0（Word 导出）
- openpyxl 3.1.2（Excel 导出）
- gunicorn 21.2.0（生产服务器）

---

## 三、数据库初始化

### 3.1 创建必要目录

```bash
cd /opt/law_firm_system
mkdir -p db backup upload static/uploads
chmod 777 upload static/uploads
```

### 3.2 执行初始化脚本

```bash
python3 init_data.py
```

初始化会自动完成：
- 创建 SQLite 数据库 `db/law_db.sqlite`
- 创建管理员账号 `admin / admin123`
- 预置 10 个常用文书模板
- 预置 5 个示例案例
- 预置律所基础信息

### 3.3 验证初始化

```bash
ls -lh db/law_db.sqlite
# 应该能看到数据库文件
```

---

## 四、生产环境部署（Gunicorn + Systemd）

### 4.1 使用 Gunicorn 启动（推荐）

2G 内存服务器建议配置 **1 个 worker**，避免内存溢出：

```bash
cd /opt/law_firm_system
gunicorn -w 1 -b 0.0.0.0:5066 --timeout 120 --access-logfile logs/access.log --error-logfile logs/error.log app:app
```

参数说明：
| 参数 | 说明 |
|------|------|
| `-w 1` | 1 个 worker 进程（2G 内存建议 1 个） |
| `-b 0.0.0.0:5066` | 绑定所有网卡的 5066 端口 |
| `--timeout 120` | 请求超时时间 120 秒 |
| `--access-logfile` | 访问日志路径 |
| `--error-logfile` | 错误日志路径 |

### 4.2 配置 Systemd 开机自启

创建日志目录和服务文件：

```bash
mkdir -p /opt/law_firm_system/logs

# 查找 gunicorn 完整路径
which gunicorn
# 通常输出：/usr/local/bin/gunicorn
```

创建 Systemd 服务文件：

```bash
cat > /etc/systemd/system/lawfirm.service << 'EOF'
[Unit]
Description=Law Firm Management System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/law_firm_system
ExecStart=/usr/local/bin/gunicorn -w 1 -b 0.0.0.0:5066 --timeout 120 --access-logfile /opt/law_firm_system/logs/access.log --error-logfile /opt/law_firm_system/logs/error.log app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

启动并设为开机自启：

```bash
systemctl daemon-reload
systemctl start lawfirm
systemctl enable lawfirm
systemctl status lawfirm
```

常用命令：
```bash
systemctl start lawfirm      # 启动
systemctl stop lawfirm       # 停止
systemctl restart lawfirm    # 重启
systemctl status lawfirm     # 查看状态
journalctl -u lawfirm -f     # 查看实时日志
```

---

## 五、Nginx 反向代理（可选但推荐）

使用 Nginx 可以：
- 隐藏后端端口，对外只暴露 80/443
- 配置域名和 HTTPS
- 静态文件加速
- 负载均衡（未来扩展）

### 5.1 安装 Nginx

```bash
# CentOS / Alibaba Cloud Linux
yum install -y nginx

# Ubuntu
apt install -y nginx
```

### 5.2 配置 Nginx

```bash
cat > /etc/nginx/conf.d/lawfirm.conf << 'EOF'
server {
    listen 80;
    server_name _;  # 如果有域名，填写域名；无域名用 _ 通配

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5066;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件直接由 Nginx 处理，减轻 Flask 负担
    location /static {
        alias /opt/law_firm_system/static;
        expires 7d;
    }
}
EOF
```

测试配置并启动：
```bash
nginx -t
systemctl start nginx
systemctl enable nginx
```

配置完成后，访问 `http://你的服务器公网IP` 即可（无需加 :5066 端口）。

### 5.3 配置 HTTPS（可选）

如果有域名，可使用 Let's Encrypt 免费 SSL：

```bash
# 安装 certbot
yum install -y certbot python3-certbot-nginx   # CentOS
apt install -y certbot python3-certbot-nginx   # Ubuntu

# 申请证书（将 your-domain.com 替换为你的域名）
certbot --nginx -d your-domain.com

# 自动续期测试
certbot renew --dry-run
```

---

## 六、访问与登录

### 6.1 浏览器访问

```
http://你的服务器公网IP:5066
```

如果配置了 Nginx：
```
http://你的服务器公网IP
```

### 6.2 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 律师 | lawyer1 | lawyer123 |
| 助理 | assistant1 | assistant123 |

> ⚠️ **首次登录后请立即修改密码！**

---

## 七、2G 内存服务器优化建议

### 7.1 Gunicorn 调优

```bash
# 使用 1 个 worker，避免内存溢出
gunicorn -w 1 -b 0.0.0.0:5066 --timeout 120 app:app
```

### 7.2 系统级优化

```bash
# 关闭不必要的服务
systemctl stop firewalld  # 如果用轻量服务器防火墙，可关闭系统防火墙
systemctl disable firewalld

# 配置 swap（防止内存不足）
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 7.3 日志管理

```bash
# 安装 logrotate 自动清理日志
yum install -y logrotate   # CentOS
apt install -y logrotate   # Ubuntu

# 配置日志轮转
cat > /etc/logrotate.d/lawfirm << 'EOF'
/opt/law_firm_system/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 root root
}
EOF
```

---

## 八、数据备份

### 8.1 手动备份

```bash
cd /opt/law_firm_system
cp db/law_db.sqlite backup/law_db_$(date +%Y%m%d_%H%M%S).sqlite
```

### 8.2 自动备份（定时任务）

```bash
crontab -e
```

添加以下内容（每天凌晨 2 点自动备份，保留最近 30 天）：
```
0 2 * * * cd /opt/law_firm_system && cp db/law_db.sqlite backup/law_db_$(date +\%Y\%m\%d_\%H\%M\%S).sqlite && find backup -name "law_db_*.sqlite" -mtime +30 -delete
```

### 8.3 下载备份到本地

```bash
# 在本地 Windows 执行
scp root@你的服务器公网IP:/opt/law_firm_system/backup/law_db_20260606_120000.sqlite C:\Users\lvping\Desktop\
```

---

## 九、故障排查

### 9.1 服务无法启动

```bash
# 查看详细错误
journalctl -u lawfirm -n 50

# 查看 Gunicorn 错误日志
cat /opt/law_firm_system/logs/error.log

# 检查端口占用
netstat -tunlp | grep 5066
ss -tunlp | grep 5066
```

### 9.2 访问 502 Bad Gateway（Nginx 场景）

```bash
# 检查 Gunicorn 是否在运行
systemctl status lawfirm

# 检查防火墙
firewall-cmd --list-ports
# 或检查阿里云控制台安全组
```

### 9.3 数据库文件损坏

```bash
cd /opt/law_firm_system

# 停止服务
systemctl stop lawfirm

# 用最新备份恢复
cp backup/law_db_xxxx.sqlite db/law_db.sqlite

# 重启服务
systemctl start lawfirm
```

### 9.4 内存不足导致进程被杀

```bash
# 查看内存使用
free -h

# 查看 OOM 日志
dmesg | grep -i 'out of memory'

# 解决：减少 Gunicorn worker 数量到 1，或增加 swap
```

### 9.5 上传文件失败

```bash
# 检查目录权限
ls -ld /opt/law_firm_system/upload
ls -ld /opt/law_firm_system/static/uploads

# 修复权限
chmod -R 777 /opt/law_firm_system/upload
chmod -R 777 /opt/law_firm_system/static/uploads
```

---

## 十、项目目录结构

```
/opt/law_firm_system/
├── app.py                  # Flask 主入口
├── config.py               # 配置文件
├── models.py               # 数据库模型
├── init_data.py            # 初始化脚本
├── requirements.txt        # Python 依赖
├── deploy.md               # 本部署手册
├── README.md               # 系统说明文档
├── static/                 # 静态资源（CSS/JS/图片）
│   └── uploads/            # 上传文件存储
├── templates/              # Jinja2 HTML 模板
│   ├── base.html
│   ├── index.html
│   ├── client/
│   ├── case/
│   ├── document/
│   ├── case_library/
│   ├── finance/
│   └── system/
├── db/
│   └── law_db.sqlite       # SQLite 数据库（重要！需备份）
├── backup/                 # 数据库备份目录
├── upload/                 # 案件附件上传目录
└── logs/                   # Gunicorn 日志目录
```

---

## 十一、升级维护

### 11.1 更新代码

```bash
cd /opt/law_firm_system

# 备份数据库
cp db/law_db.sqlite backup/law_db_before_update_$(date +%Y%m%d).sqlite

# 拉取新代码（如果是 Git 部署）
git pull

# 重启服务
systemctl restart lawfirm
```

### 11.2 更新依赖

```bash
cd /opt/law_firm_system
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
systemctl restart lawfirm
```

---

## 十二、安全建议

1. **修改默认密码**：首次登录后立即修改 admin 密码
2. **限制访问来源**：阿里云安全组中 5066 端口只放行办公室公网 IP
3. **定期备份**：数据库每天至少备份一次
4. **使用 HTTPS**：如有域名，配置 Let's Encrypt 免费证书
5. **关闭调试模式**：生产环境 `debug=False`（已在 config.py 中配置）
6. **定期更新系统**：`yum update` 或 `apt update && apt upgrade`

---

> 如有问题，请检查 `logs/error.log` 和 `journalctl -u lawfirm` 日志。  
> 祝部署顺利！
