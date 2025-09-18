# 多平台社交媒体发布工具

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