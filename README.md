# 多平台社交媒体发布工具

一个基于 Streamlit 的多平台社交媒体内容发布工具，支持 Twitter、LinkedIn、微博等平台的一键同步发布。

## ✨ 功能特色

- 🚀 **多平台发布**: 支持 Twitter、LinkedIn、微博
- 📱 **直接 API 连接**: 无需第三方服务，直接连接官方 API
- 🖼️ **图片上传**: 支持多图片上传和预览（需要 Pillow）
- 🔗 **链接分享**: 自动添加链接到帖子
- ⚙️ **平台特定设置**: 每个平台的个性化选项
- 📊 **发布结果跟踪**: 实时显示发布状态
- 👀 **预览模式**: 发布前预览内容
- 💾 **会话历史**: 本地存储发布记录

## 🚀 GitHub + Streamlit Cloud 部署

### 1. 创建 GitHub 仓库

1. 在 GitHub 上创建新仓库
2. 将以下文件上传到仓库：
   - `app.py` (主应用文件)
   - `requirements.txt` (依赖文件)
   - `README.md` (说明文档)

### 2. 部署到 Streamlit Cloud

1. 访问 [share.streamlit.io](https://share.streamlit.io)
2. 使用 GitHub 账户登录
3. 选择您的仓库和 `app.py` 文件
4. 点击 "Deploy" 开始部署

### 3. 文件结构
```
your-repo/
├── app.py              # 主应用文件（重命名 multisync.py）
├── requirements.txt    # 依赖包列表
└── README.md          # 说明文档
```

## 📦 依赖管理

应用采用**渐进式依赖加载**：

### 核心功能（必需）
- `streamlit` - Web 应用框架
- `requests` - HTTP 请求库

### 增强功能（可选）
- `Pillow` - 图片处理和预览
- `tweepy` - Twitter API 支持
- `python-dateutil` - 时间处理

### 安装策略

**最小安装**（仅基础功能）:
```txt
streamlit>=1.28.0
requests>=2.31.0
```

**推荐安装**（完整功能）:
```txt
streamlit>=1.28.0
requests>=2.31.0
Pillow>=10.0.0
tweepy>=4.14.0
python-dateutil>=2.8.2
```

## 🔑 API 配置指南

### Twitter API (X)
1. 访问 [developer.twitter.com](https://developer.twitter.com)
2. 申请开发者账户
3. 创建新应用，获取：
   - API Key
   - API Secret Key  
   - Access Token
   - Access Token Secret

### LinkedIn API
1. 访问 [developer.linkedin.com](https://developer.linkedin.com)
2. 创建应用
3. 申请 `w_member_social` 权限
4. 获取访问令牌和个人/公司 ID

### 微博 API
1. 访问 [open.weibo.com](https://open.weibo.com)
2. 创建应用并通过审核
3. 获取访问令牌

## 🎯 使用方法

### 基础使用
1. 打开部署后的应用链接
2. 在侧边栏配置 API 凭据
3. 连接想要使用的平台
4. 在主页面写内容并发布

### 高级功能
- **预览模式**: 发布前查看内容效果
- **平台特定设置**: 为不同平台定制内容
- **发布历史**: 查看历史发布记录
- **批量管理**: 一键连接/断开多个平台

## 🔒 安全特性

- **无服务器存储**: 所有数据仅存储在浏览器会话中
- **API 凭据加密**: 密码输入框保护敏感信息
- **最小权限原则**: 仅请求必要的 API 权限
- **错误隔离**: 单个平台故障不影响其他平台

## 🐛 故障排除

### 常见问题

**Q: 部署后提示缺少依赖**
A: 检查 `requirements.txt` 文件是否包含所需包

**Q: Twitter 发布失败**  
A: 检查 API v2 权限，确保 Access Token 有写入权限

**Q: LinkedIn 连接失败**
A: 确认应用已申请 `w_member_social` 权限

**Q: 图片功能不可用**
A: 在 `requirements.txt` 中添加 `Pillow>=10.0.0`

### 调试技巧

1. 查看 Streamlit Cloud 部署日志
2. 使用预览模式测试内容
3. 检查 API 凭据有效性
4. 确认平台 API 限额

## 📈 功能路线图

### v1.1 (计划中)
- [ ] 定时发布功能
- [ ] 内容模板系统
- [ ] 发布数据统计

### v1.2 (规划中)  
- [ ] 更多平台支持
- [ ] 内容 AI 优化建议
- [ ] 团队协作功能

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 📞 技术支持

- 🐛 问题报告：kapsabuy@gmail.com
- 💬 功能建议：kaspabuy@gmail.com
- 📧 联系方式：通过 kaspabuy@gmail.com 联系

---

⭐ **如果这个项目对您有帮助，请给个星标支持！**

🚀 **立# 多平台社交媒体发布工具

一个基于 Streamlit 的多平台社交媒体内容发布工具，支持 Twitter、Facebook、LinkedIn 等平台的一键同步发布。

## ✨ 功能特色

- 🚀 **多平台发布**: 支持 Twitter、Facebook、LinkedIn
- 📱 **直接 API 连接**: 无需第三方服务，直接连接官方 API
- 🖼️ **图片上传**: 支持多图片上传和预览
- 🔗 **链接分享**: 自动添加链接到帖子
- ⚙️ **平台特定设置**: 每个平台的个性化选项
- 📊 **发布结果跟踪**: 实时显示发布状态

## 🛠️ 安装方法

### 方法一：自动安装（推荐）

1. 下载所有文件到同一目录
2. 运行安装脚本：
```bash
python setup.py
```

### 方法二：手动安装

1. 安装基础依赖：
```bash
pip install streamlit requests pillow python-dateutil
```

2. 根据需要安装平台支持：
```bash
# Twitter 支持
pip install tweepy

# Facebook 支持
pip install facebook-sdk
```

### 方法三：使用 requirements.txt

```bash
pip install -r requirements.txt
```

## 🚀 快速开始

1. 启动应用：
```bash
streamlit run multisync.py
```

2. 在浏览器中打开显示的 URL（通常是 `http://localhost:8501`）

3. 在侧边栏配置社交媒体平台 API 凭据

## 🔑 API 凭据获取

### Twitter API
1. 访问 [developer.twitter.com](https://developer.twitter.com)
2. 创建开发者账户
3. 创建新应用
4. 获取以下凭据：
   - API Key
   - API Secret Key
   - Access Token
   - Access Token Secret

### Facebook API
1. 访问 [developers.facebook.com](https://developers.facebook.com)
2. 创建应用
3. 添加 Facebook Pages API
4. 获取页面访问令牌和页面 ID

### LinkedIn API
1. 访问 [developer.linkedin.com](https://developer.linkedin.com)
2. 创建应用
3. 申请必要的权限
4. 获取访问令牌和个人/公司 ID

## 📁 文件结构

```
project/
├── multisync.py          # 主应用文件
├── requirements.txt      # 依赖包列表
├── setup.py             # 自动安装脚本
└── README.md            # 说明文档
```

## 🐛 故障排除

### 常见问题

**Q: 导入错误 "ModuleNotFoundError"**
A: 运行 `python setup.py` 或手动安装缺失的包

**Q: Twitter API 连接失败**
A: 检查 API 凭据是否正确，确保应用有必要的权限

**Q: Facebook 发布失败**
A: 确保页面令牌有发布权限，页面 ID 正确

**Q: 图片上传失败**
A: 检查图片格式和大小，确保符合平台要求

### 调试模式

在代码中添加以下行来启用调试：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 安全注意事项

- 永远不要在代码中硬编码 API 凭据
- 使用环境变量存储敏感信息
- 定期轮换 API 密钥
- 确保应用权限最小化

## 📝 更新日志

### v1.0.0
- 初始版本
- 支持 Twitter、Facebook、LinkedIn
- 基础图片上传功能
- 多平台同步发布

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如果遇到问题，请：
1. 检查常见问题部分
2. 查看平台 API 文档
3. 提交 Issue 描述问题

---

⭐ 如果这个工具对您有帮助，请给个星标！