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
LINKEDIN_AVAILABLE = True

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
def publish_to_twitter(content, twitter_config):
    """发布到 Twitter"""
    try:
        client = twitter_config['client']
        
        # 检查内容长度
        if len(content) > 280:
            return {'success': False, 'error': '内容超过 280 字符限制'}
        
        # 发布推文
        response = client.create_tweet(text=content)
        
        return {'success': True, 'post_id': response.data['id']}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def publish_to_linkedin(content, linkedin_config):
    """发布到 LinkedIn"""
    try:
        token = linkedin_config['token']
        person_id = linkedin_config['person_id']
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # 准备发布数据
        post_data = {
            'author': f'urn:li:person:{person_id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': content
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
        
        # 发布帖子
        response = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            headers=headers,
            json=post_data
        )
        
        if response.status_code == 201:
            post_id = response.json().get('id', '')
            return {'success': True, 'post_id': post_id}
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def publish_to_weibo(content, weibo_config):
    """发布到微博"""
    try:
        token = weibo_config['token']
        
        # 微博发布 API
        url = 'https://api.weibo.com/2/statuses/update.json'
        data = {
            'access_token': token,
            'status': content
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            return {'success': True, 'post_id': result.get('id', '')}
        else:
            return {'success': False, 'error': f'微博API错误: {response.text}'}
            
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
                            'user_id': user.data.id,
                            'username': user.data.username
                        }
                        st.success(f"✅ Twitter 连接成功！用户: @{user.data.username}")
                    except Exception as e:
                        st.error(f"❌ Twitter 连接失败: {str(e)}")
                else:
                    st.warning("请填写所有 Twitter API 凭据")
    
    # LinkedIn 配置
    st.subheader("💼 LinkedIn")
    with st.expander("LinkedIn API 设置"):
        linkedin_access_token = st.text_input("Access Token", type="password", key="linkedin_token")
        linkedin_person_id = st.text_input("Person/Company ID", key="linkedin_id")
        
        if st.button("连接 LinkedIn", key="connect_linkedin"):
            if linkedin_access_token and linkedin_person_id:
                try:
                    # 验证 LinkedIn token
                    headers = {'Authorization': f'Bearer {linkedin_access_token}'}
                    response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
                    
                    if response.status_code == 200:
                        st.session_state.authenticated_platforms['linkedin'] = {
                            'token': linkedin_access_token,
                            'person_id': linkedin_person_id
                        }
                        user_info = response.json()
                        name = f"{user_info.get('localizedFirstName', '')} {user_info.get('localizedLastName', '')}"
                        st.success(f"✅ LinkedIn 连接成功！用户: {name}")
                    else:
                        st.error("❌ LinkedIn 连接失败")
                except Exception as e:
                    st.error(f"❌ LinkedIn 连接失败: {str(e)}")
            else:
                st.warning("请填写 LinkedIn 凭据")
    
    # 微博 API 配置（使用简化版本）
    st.subheader("🔴 微博")
    with st.expander("微博 API 设置（实验性）"):
        weibo_access_token = st.text_input("微博 Access Token", type="password", key="weibo_token")
        
        if st.button("连接微博", key="connect_weibo"):
            if weibo_access_token:
                try:
                    # 验证微博 token
                    response = requests.get(
                        'https://api.weibo.com/2/account/get_uid.json',
                        params={'access_token': weibo_access_token}
                    )
                    
                    if response.status_code == 200:
                        st.session_state.authenticated_platforms['weibo'] = {
                            'token': weibo_access_token
                        }
                        st.success("✅ 微博连接成功！")
                    else:
                        st.error("❌ 微博连接失败")
                except Exception as e:
                    st.error(f"❌ 微博连接失败: {str(e)}")
    
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
        
        ### 💼 LinkedIn API  
        1. 访问 [developer.linkedin.com](https://developer.linkedin.com)
        2. 创建应用
        3. 申请 w_member_social 权限
        4. 获取访问令牌
        
        ### 🔴 微博 API
        1. 访问 [open.weibo.com](https://open.weibo.com)
        2. 创建应用
        3. 获取访问令牌
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
                            st.image(image, caption=uploaded_file.name, use_column_width=True)
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
                    'linkedin': '💼 LinkedIn', 
                    'weibo': '🔴 微博'
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
                                    result = publish_to_twitter(final_content, st.session_state.authenticated_platforms['twitter'])
                                elif platform == 'linkedin':
                                    result = publish_to_linkedin(final_content, st.session_state.authenticated_platforms['linkedin'])
                                elif platform == 'weibo':
                                    result = publish_to_weibo(final_content, st.session_state.authenticated_platforms['weibo'])
                                else:
                                    result = {'success': False, 'error': 'Unsupported platform'}
                                
                                publish_results[platform] = result
                                
                            except Exception as e:
                                publish_results[platform] = {'success': False, 'error': str(e)}
                    
                    # 显示发布结果
                    st.header("📊 发布结果")
                    success_count = 0
                    for platform, result in publish_results.items():
                        platform_icon = {'twitter': '🐦', 'linkedin': '💼', 'weibo': '🔴'}.get(platform, '📱')
                        
                        if result['success']:
                            st.success(f"✅ {platform_icon} {platform.title()}: 发布成功！")
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
                            'status': f"{success_count}/{len(selected_platforms)} 成功"
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
                platform_icon = {'twitter': '🐦', 'linkedin': '💼', 'weibo': '🔴'}.get(platform, '📱')
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
        **版本**: 1.0.0
        **已连接平台**: {len(st.session_state.authenticated_platforms)}
        **发布记录**: {len(st.session_state.publish_history)} 条
        **依赖状态**: {"✅ 完整" if all(dependencies_status.values()) else "⚠️ 部分缺失"}
        """)

# 底部信息
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        📱 多平台社交媒体发布工具 | Made with Streamlit<br>
        🔒 所有数据仅在您的浏览器会话中存储，确保隐私安全
    </div>
    """, 
    unsafe_allow_html=True
)