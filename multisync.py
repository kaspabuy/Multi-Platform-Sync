import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import io
import base64

# 尝试导入可选的第三方库
try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# LinkedIn 使用标准 requests 库，无需额外依赖
TELEGRAM_AVAILABLE = True
INSTAGRAM_AVAILABLE = True

# 页面配置
st.set_page_config(
    page_title="多平台发布工具",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题
st.title("📱 多平台社交媒体发布工具")
st.markdown("*无需第三方服务，直接连接各平台API*")

# 检查依赖状态
st.sidebar.header("📦 依赖状态")
dependencies_status = {
    "✅ Streamlit": True,
    "✅ Requests": True,
    "📷 PIL/Pillow": PIL_AVAILABLE,
    "🐦 Twitter (tweepy)": TWITTER_AVAILABLE,
    "📨 Telegram": TELEGRAM_AVAILABLE,
    "📸 Instagram": INSTAGRAM_AVAILABLE,
}

for dep, status in dependencies_status.items():
    if status:
        st.sidebar.success(dep)
    else:
        st.sidebar.error(dep + " - 未安装")

if not PIL_AVAILABLE:
    st.sidebar.warning("⚠️ PIL 未安装，图片功能受限")

# 初始化 session state
if 'authenticated_platforms' not in st.session_state:
    st.session_state.authenticated_platforms = {}
if 'publish_history' not in st.session_state:
    st.session_state.publish_history = []

# 发布函数定义（需要在调用前定义）
def publish_to_twitter(content, twitter_config, media_files=None):
    """发布到 Twitter，支持图片上传"""
    try:
        client = twitter_config['client']
        
        # 检查内容长度
        if len(content) > 280:
            return {'success': False, 'error': '内容超过 280 字符限制'}
        
        # 处理图片上传
        media_ids = []
        if media_files:
            # 创建 API v1.1 客户端用于媒体上传
            auth = tweepy.OAuth1UserHandler(
                twitter_config.get('consumer_key'),
                twitter_config.get('consumer_secret'),
                twitter_config.get('access_token'),
                twitter_config.get('access_token_secret')
            )
            api_v1 = tweepy.API(auth)
            
            for media_file in media_files[:4]:  # Twitter 最多支持4张图片
                try:
                    # 将上传的文件转换为字节
                    media_file.seek(0)  # 重置文件指针
                    media_data = media_file.read()
                    
                    # 上传媒体
                    media = api_v1.media_upload(filename=media_file.name, file=io.BytesIO(media_data))
                    media_ids.append(media.media_id)
                except Exception as e:
                    st.warning(f"图片 {media_file.name} 上传失败: {str(e)}")
        
        # 发布推文
        if media_ids:
            response = client.create_tweet(text=content, media_ids=media_ids)
        else:
            response = client.create_tweet(text=content)
        
        return {'success': True, 'post_id': response.data['id'], 'media_count': len(media_ids)}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def publish_to_telegram(content, telegram_config, media_files=None):
    """发布到 Telegram 频道，支持图片"""
    try:
        bot_token = telegram_config['bot_token']
        channel_id = telegram_config['channel_id']
        
        # 如果有图片，发送图片+文字
        if media_files:
            # Telegram 支持多种媒体类型
            if len(media_files) == 1:
                # 单张图片
                media_file = media_files[0]
                media_file.seek(0)
                
                url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
                
                files = {'photo': (media_file.name, media_file, 'image/jpeg')}
                data = {
                    'chat_id': channel_id,
                    'caption': content,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, data=data, files=files)
            else:
                # 多张图片 - 使用 media group
                media_group = []
                files = {}
                
                for i, media_file in enumerate(media_files[:10]):  # Telegram 最多10张
                    media_file.seek(0)
                    file_key = f"photo{i}"
                    files[file_key] = (media_file.name, media_file, 'image/jpeg')
                    
                    media_item = {
                        'type': 'photo',
                        'media': f'attach://{file_key}'
                    }
                    
                    # 第一张图片添加caption
                    if i == 0:
                        media_item['caption'] = content
                        media_item['parse_mode'] = 'HTML'
                    
                    media_group.append(media_item)
                
                url = f"https://api.telegram.org/bot{bot_token}/sendMediaGroup"
                data = {
                    'chat_id': channel_id,
                    'media': json.dumps(media_group)
                }
                
                response = requests.post(url, data=data, files=files)
        else:
            # 纯文本消息
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': channel_id,
                'text': content,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result['ok']:
                message_id = result['result']['message_id'] if 'message_id' in result['result'] else result['result'][0]['message_id']
                return {'success': True, 'post_id': message_id}
            else:
                return {'success': False, 'error': result.get('description', 'Unknown error')}
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def publish_to_instagram(content, instagram_config):
    """发布到 Instagram（使用 Instagram Basic Display API）"""
    try:
        access_token = instagram_config['access_token']
        user_id = instagram_config['user_id']
        
        # Instagram Basic Display API - 创建媒体容器
        # 注意：Instagram API 需要图片，纯文本无法发布
        if 'media_url' not in instagram_config:
            return {'success': False, 'error': 'Instagram 需要图片才能发布内容'}
        
        media_url = instagram_config['media_url']
        
        # 第一步：创建媒体容器
        container_url = f"https://graph.instagram.com/v18.0/{user_id}/media"
        container_data = {
            'image_url': media_url,
            'caption': content,
            'access_token': access_token
        }
        
        container_response = requests.post(container_url, data=container_data)
        
        if container_response.status_code != 200:
            return {'success': False, 'error': f'创建媒体容器失败: {container_response.text}'}
        
        container_id = container_response.json().get('id')
        
        # 第二步：发布媒体
        publish_url = f"https://graph.instagram.com/v18.0/{user_id}/media_publish"
        publish_data = {
            'creation_id': container_id,
            'access_token': access_token
        }
        
        publish_response = requests.post(publish_url, data=publish_data)
        
        if publish_response.status_code == 200:
            result = publish_response.json()
            return {'success': True, 'post_id': result.get('id', '')}
        else:
            return {'success': False, 'error': f'发布失败: {publish_response.text}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

# 侧边栏 - 平台配置
with st.sidebar:
    st.header("🔑 平台配置")
    
    # Twitter/X 配置
    st.subheader("🐦 Twitter/X")
    if not TWITTER_AVAILABLE:
        st.error("❌ 需要安装 tweepy 包")
        st.info("在 requirements.txt 中添加: tweepy>=4.14.0")
    else:
        with st.expander("Twitter API 设置"):
            twitter_api_key = st.text_input("API Key", type="password", key="twitter_key")
            twitter_api_secret = st.text_input("API Secret", type="password", key="twitter_secret")
            twitter_access_token = st.text_input("Access Token", type="password", key="twitter_token")
            twitter_access_secret = st.text_input("Access Token Secret", type="password", key="twitter_token_secret")
            
            if st.button("连接 Twitter", key="connect_twitter"):
                if all([twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret]):
                    try:
                        # 创建 Twitter API v2 客户端
                        client = tweepy.Client(
                            consumer_key=twitter_api_key,
                            consumer_secret=twitter_api_secret,
                            access_token=twitter_access_token,
                            access_token_secret=twitter_access_secret
                        )
                        
                        # 测试连接
                        user = client.get_me()
                        st.session_state.authenticated_platforms['twitter'] = {
                            'client': client,
                            'consumer_key': twitter_api_key,
                            'consumer_secret': twitter_api_secret,
                            'access_token': twitter_access_token,
                            'access_token_secret': twitter_access_secret,
                            'user_id': user.data.id,
                            'username': user.data.username
                        }
                        st.success(f"✅ Twitter 连接成功！用户: @{user.data.username}")
                    except Exception as e:
                        st.error(f"❌ Twitter 连接失败: {str(e)}")
                else:
                    st.warning("请填写所有 Twitter API 凭据")
    
    # Telegram 配置
    st.subheader("📨 Telegram")
    with st.expander("Telegram Bot API 设置"):
        telegram_bot_token = st.text_input("Bot Token", type="password", key="telegram_token", 
                                         help="从 @BotFather 获取")
        telegram_channel_id = st.text_input("频道 ID", key="telegram_channel", 
                                          placeholder="@your_channel 或 -100xxxxxxxxx",
                                          help="频道用户名（@开头）或频道 ID")
        
        if st.button("连接 Telegram", key="connect_telegram"):
            if telegram_bot_token and telegram_channel_id:
                try:
                    # 验证 bot token
                    test_url = f"https://api.telegram.org/bot{telegram_bot_token}/getMe"
                    response = requests.get(test_url)
                    
                    if response.status_code == 200:
                        bot_info = response.json()
                        if bot_info['ok']:
                            st.session_state.authenticated_platforms['telegram'] = {
                                'bot_token': telegram_bot_token,
                                'channel_id': telegram_channel_id
                            }
                            bot_name = bot_info['result']['first_name']
                            st.success(f"✅ Telegram 连接成功！Bot: {bot_name}")
                        else:
                            st.error("❌ Bot Token 无效")
                    else:
                        st.error("❌ Telegram 连接失败")
                except Exception as e:
                    st.error(f"❌ Telegram 连接失败: {str(e)}")
            else:
                st.warning("请填写 Bot Token 和频道 ID")
    
    # Instagram 配置  
    st.subheader("📸 Instagram")
    with st.expander("Instagram API 设置"):
        instagram_access_token = st.text_input("Access Token", type="password", key="instagram_token")
        instagram_user_id = st.text_input("Instagram User ID", key="instagram_user_id")
        
        st.info("⚠️ Instagram 需要图片才能发布内容，纯文本无法发布")
        
        if st.button("连接 Instagram", key="connect_instagram"):
            if instagram_access_token and instagram_user_id:
                try:
                    # 验证 Instagram token
                    test_url = f"https://graph.instagram.com/v18.0/{instagram_user_id}"
                    params = {'fields': 'id,username', 'access_token': instagram_access_token}
                    response = requests.get(test_url, params=params)
                    
                    if response.status_code == 200:
                        user_info = response.json()
                        st.session_state.authenticated_platforms['instagram'] = {
                            'access_token': instagram_access_token,
                            'user_id': instagram_user_id
                        }
                        username = user_info.get('username', 'Unknown')
                        st.success(f"✅ Instagram 连接成功！用户: @{username}")
                    else:
                        st.error(f"❌ Instagram 连接失败: {response.text}")
                except Exception as e:
                    st.error(f"❌ Instagram 连接失败: {str(e)}")
            else:
                st.warning("请填写 Instagram 凭据")
    
    # 显示已连接平台
    st.header("✅ 已连接平台")
    for platform in st.session_state.authenticated_platforms:
        st.success(f"✅ {platform.title()}")

# 主内容区域
if not st.session_state.authenticated_platforms:
    st.warning("请在侧边栏配置并连接至少一个社交媒体平台")
    
    # 显示API获取指南
    with st.expander("📖 API 获取指南", expanded=True):
        st.markdown("""
        ### 🐦 Twitter API
        1. 访问 [developer.twitter.com](https://developer.twitter.com)
        2. 申请开发者账户
        3. 创建新应用
        4. 生成 API Keys 和 Access Tokens
        
        ### 📨 Telegram Bot API  
        1. 在 Telegram 中找到 @BotFather
        2. 发送 `/newbot` 创建新 bot
        3. 获取 Bot Token
        4. 将 bot 添加到您的频道并设为管理员
        5. 频道 ID 格式：@channel_name 或 -100xxxxxxxxx
        
        ### 📸 Instagram API
        1. 访问 [developers.facebook.com](https://developers.facebook.com)
        2. 创建 Facebook 应用
        3. 添加 Instagram Basic Display 产品
        4. 获取用户访问令牌和用户 ID
        5. ⚠️ 注意：Instagram 只能发布带图片的内容
        """)
else:
    # 发布功能
    tab1, tab2, tab3 = st.tabs(["📝 发布内容", "📊 发布历史", "⚙️ 设置"])
    
    with tab1:
        st.header("📝 创建新帖子")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 内容输入
            post_content = st.text_area(
                "帖子内容",
                placeholder="写下您想要分享的内容...",
                height=200,
                max_chars=2000
            )
            
            # 字符计数
            char_count = len(post_content)
            if char_count > 280:
                st.warning(f"⚠️ 内容长度 {char_count} 字符，Twitter 限制 280 字符")
            else:
                st.info(f"📝 内容长度: {char_count} 字符")
            
            # 图片上传（如果PIL可用）
            uploaded_files = None
            if PIL_AVAILABLE:
                uploaded_files = st.file_uploader(
                    "上传图片",
                    accept_multiple_files=True,
                    type=['png', 'jpg', 'jpeg', 'gif']
                )
                
                # 预览上传的图片
                if uploaded_files:
                    st.subheader("📷 图片预览")
                    cols = st.columns(min(len(uploaded_files), 3))
                    for i, uploaded_file in enumerate(uploaded_files):
                        with cols[i % 3]:
                            image = Image.open(uploaded_file)
                            # 修复：使用 use_container_width 替代 use_column_width
                            st.image(image, caption=uploaded_file.name, use_container_width=True)
            else:
                st.info("💡 安装 Pillow 包以支持图片上传功能")
            
            # 链接添加
            link_url = st.text_input("添加链接（可选）", placeholder="https://...")
        
        with col2:
            st.subheader("🎯 发布设置")
            
            # 选择平台
            selected_platforms = []
            for platform in st.session_state.authenticated_platforms:
                platform_name = {
                    'twitter': '🐦 Twitter',
                    'telegram': '📨 Telegram', 
                    'instagram': '📸 Instagram'
                }.get(platform, platform.title())
                
                if st.checkbox(f"发布到 {platform_name}", value=True, key=f"select_{platform}"):
                    selected_platforms.append(platform)
            
            # 发布模式
            st.subheader("📤 发布模式")
            publish_mode = st.radio(
                "选择发布方式",
                ["立即发布", "预览模式"],
                help="预览模式不会实际发布，只显示将要发布的内容"
            )
            
            # 平台特定设置
            st.subheader("⚙️ 平台设置")
            
            # Twitter 特定设置
            if 'twitter' in selected_platforms:
                st.write("**🐦 Twitter 设置**")
                add_hashtags = st.checkbox("自动添加热门标签", key="twitter_hashtags")
                if add_hashtags:
                    hashtags = st.text_input("标签（用空格分隔）", value="#社交媒体 #分享", key="twitter_hashtag_input")
                else:
                    hashtags = ""
            
            # Telegram 特定设置
            if 'telegram' in selected_platforms:
                st.write("**📨 Telegram 设置**")
                telegram_format = st.selectbox("消息格式", ["普通文本", "HTML", "Markdown"], key="telegram_format")
                disable_preview = st.checkbox("禁用链接预览", key="telegram_preview")
            
            # Instagram 特定设置
            if 'instagram' in selected_platforms:
                st.write("**📸 Instagram 设置**")
                st.warning("⚠️ Instagram 需要图片才能发布")
                if uploaded_files:
                    st.success(f"✅ 已上传 {len(uploaded_files)} 张图片")
                else:
                    st.error("❌ 请上传至少一张图片")
                
                # 图片URL输入（用于Instagram API）
                image_url_for_instagram = st.text_input(
                    "图片公开URL（Instagram API需要）", 
                    placeholder="https://example.com/image.jpg",
                    help="Instagram API需要公开可访问的图片URL"
                )
        
        # 发布按钮
        button_text = "👀 预览发布内容" if publish_mode == "预览模式" else "🚀 发布到选中平台"
        button_type = "secondary" if publish_mode == "预览模式" else "primary"
        
        if st.button(button_text, type=button_type, use_container_width=True):
            if not post_content.strip():
                st.error("请输入帖子内容")
            elif not selected_platforms:
                st.error("请至少选择一个发布平台")
            else:
                if publish_mode == "预览模式":
                    # 预览模式
                    st.header("👀 发布预览")
                    for platform in selected_platforms:
                        with st.expander(f"预览: {platform.title()}", expanded=True):
                            preview_content = post_content
                            
                            # 添加平台特定内容
                            if platform == 'twitter' and add_hashtags and hashtags:
                                preview_content += f"\n\n{hashtags}"
                            
                            if link_url:
                                preview_content += f"\n🔗 {link_url}"
                            
                            st.write("**发布内容:**")
                            st.info(preview_content)
                            
                            if uploaded_files:
                                st.write(f"**附件:** {len(uploaded_files)} 张图片")
                                # 显示图片预览
                                cols = st.columns(min(len(uploaded_files), 4))
                                for i, uploaded_file in enumerate(uploaded_files):
                                    with cols[i % 4]:
                                        image = Image.open(uploaded_file)
                                        st.image(image, use_container_width=True)
                else:
                    # 实际发布
                    publish_results = {}
                    
                    # 发布到各个平台
                    for platform in selected_platforms:
                        with st.spinner(f"正在发布到 {platform.title()}..."):
                            try:
                                final_content = post_content
                                
                                # 添加平台特定内容
                                if platform == 'twitter' and add_hashtags and hashtags:
                                    final_content += f"\n\n{hashtags}"
                                
                                if link_url:
                                    final_content += f"\n{link_url}"
                                
                                if platform == 'twitter':
                                    result = publish_to_twitter(
                                        final_content, 
                                        st.session_state.authenticated_platforms['twitter'],
                                        uploaded_files
                                    )
                                elif platform == 'telegram':
                                    # 为Telegram准备特殊格式
                                    telegram_content = final_content
                                    if 'telegram_format' in locals():
                                        if telegram_format == "HTML":
                                            telegram_content = final_content.replace('\n', '<br>')
                                        elif telegram_format == "Markdown":
                                            telegram_content = final_content
                                    
                                    result = publish_to_telegram(
                                        telegram_content, 
                                        st.session_state.authenticated_platforms['telegram'],
                                        uploaded_files
                                    )
                                elif platform == 'instagram':
                                    # Instagram需要图片URL
                                    instagram_config = st.session_state.authenticated_platforms['instagram'].copy()
                                    if 'image_url_for_instagram' in locals() and image_url_for_instagram:
                                        instagram_config['media_url'] = image_url_for_instagram
                                        result = publish_to_instagram(final_content, instagram_config)
                                    else:
                                        result = {'success': False, 'error': '需要提供图片URL'}
                                else:
                                    result = {'success': False, 'error': 'Unsupported platform'}
                                
                                publish_results[platform] = result
                                
                            except Exception as e:
                                publish_results[platform] = {'success': False, 'error': str(e)}
                    
                    # 显示发布结果
                    st.header("📊 发布结果")
                    success_count = 0
                    for platform, result in publish_results.items():
                        platform_icon = {'twitter': '🐦', 'telegram': '📨', 'instagram': '📸'}.get(platform, '📱')
                        
                        if result['success']:
                            success_msg = f"✅ {platform_icon} {platform.title()}: 发布成功！"
                            if 'media_count' in result and result['media_count'] > 0:
                                success_msg += f" (包含 {result['media_count']} 张图片)"
                            st.success(success_msg)
                            
                            if 'post_id' in result:
                                st.code(f"帖子 ID: {result['post_id']}")
                            success_count += 1
                        else:
                            st.error(f"❌ {platform_icon} {platform.title()}: {result['error']}")
                    
                    # 记录到历史
                    if success_count > 0:
                        history_record = {
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'content': post_content[:50] + "..." if len(post_content) > 50 else post_content,
                            'platforms': [p for p, r in publish_results.items() if r['success']],
                            'status': f"{success_count}/{len(selected_platforms)} 成功",
                            'media_count': len(uploaded_files) if uploaded_files else 0
                        }
                        st.session_state.publish_history.append(history_record)
                    
                    # 成功提示
                    if success_count == len(selected_platforms):
                        st.balloons()
                        st.success(f"🎉 所有平台发布成功！({success_count}/{len(selected_platforms)})")
                    elif success_count > 0:
                        st.warning(f"⚠️ 部分平台发布成功 ({success_count}/{len(selected_platforms)})")
    
    with tab2:
        st.header("📊 发布历史")
        
        if st.session_state.publish_history:
            st.info(f"共 {len(st.session_state.publish_history)} 条发布记录")
            
            for i, record in enumerate(reversed(st.session_state.publish_history)):
                with st.expander(f"#{len(st.session_state.publish_history)-i} - {record['timestamp']} - {record['status']}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**内容**: {record['content']}")
                        st.write(f"**平台**: {', '.join([p.title() for p in record['platforms']])}")
                        if record.get('media_count', 0) > 0:
                            st.write(f"**图片**: {record['media_count']} 张")
                    with col2:
                        st.write(f"**时间**: {record['timestamp']}")
                        st.write(f"**状态**: {record['status']}")
        else:
            st.info("暂无发布历史")
            st.markdown("发布第一条内容来开始记录历史！")
    
    with tab3:
        st.header("⚙️ 应用设置")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔌 平台连接管理")
            for platform in list(st.session_state.authenticated_platforms.keys()):
                platform_icon = {'twitter': '🐦', 'telegram': '📨', 'instagram': '📸'}.get(platform, '📱')
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"{platform_icon} {platform.title()} - 已连接")
                with col_b:
                    if st.button(f"断开", key=f"disconnect_{platform}"):
                        del st.session_state.authenticated_platforms[platform]
                        st.rerun()
        
        with col2:
            st.subheader("📊 数据管理")
            if st.button("🗑️ 清空发布历史"):
                st.session_state.publish_history = []
                st.success("发布历史已清空")
                
            if st.button("🔄 重置所有连接", type="secondary"):
                st.session_state.authenticated_platforms = {}
                st.session_state.publish_history = []
                st.success("所有设置已重置")
                st.rerun()
        
        st.subheader("ℹ️ 应用信息")
        st.info(f"""
        **版本**: 1.0.1 (已修复图片上传问题)
        **已连接平台**: {len(st.session_state.authenticated_platforms)}
        **发布记录**: {len(st.session_state.publish_history)} 条
        **依赖状态**: {"✅ 完整" if all(dependencies_status.values()) else "⚠️ 部分缺失"}
        """)
        
        # 新增：修复说明
        with st.expander("🔧 最新修复内容", expanded=False):
            st.markdown("""
            ### ✅ 已修复问题:
            1. **图片上传到 Twitter**: 现在支持同时上传文字和图片到 Twitter (最多4张)
            2. **图片上传到 Telegram**: 支持单张或多张图片发布 (最多10张)  
            3. **弃用参数修复**: 将 `use_column_width` 更新为 `use_container_width`
            4. **发布历史增强**: 现在会记录包含的图片数量
            5. **错误处理改进**: 更详细的错误信息和状态反馈
            
            ### 📋 使用说明:
            - **Twitter**: 支持文字+图片，自动处理媒体上传
            - **Telegram**: 单图用 sendPhoto，多图用 sendMediaGroup
            - **Instagram**: 仍需要提供公开图片URL (API限制)
            
            ### 🔧 技术改进:
            - 使用 Twitter API v1.1 进行媒体上传
            - 使用 Twitter API v2 进行推文发布  
            - 改进了文件处理和错误恢复机制
            """)

# 底部信息
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        📱 多平台社交媒体发布工具 v1.0.1 | Made with Streamlit<br>
        🔒 所有数据仅在您的浏览器会话中存储，确保隐私安全<br>
        ✅ 已修复图片上传和弃用参数问题
    </div>
    """, 
    unsafe_allow_html=True
)