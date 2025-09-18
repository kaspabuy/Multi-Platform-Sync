import streamlit as st
import tweepy
import facebook
import requests
import json
import base64
from datetime import datetime, timedelta
import os
import tempfile
from PIL import Image
import io

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

# 初始化 session state
if 'authenticated_platforms' not in st.session_state:
    st.session_state.authenticated_platforms = {}

# 侧边栏 - 平台配置
with st.sidebar:
    st.header("🔑 平台配置")
    
    # Twitter/X 配置
    st.subheader("🐦 Twitter/X")
    with st.expander("Twitter API 设置"):
        twitter_api_key = st.text_input("Twitter API Key", type="password", key="twitter_key")
        twitter_api_secret = st.text_input("Twitter API Secret", type="password", key="twitter_secret")
        twitter_access_token = st.text_input("Twitter Access Token", type="password", key="twitter_token")
        twitter_access_secret = st.text_input("Twitter Access Token Secret", type="password", key="twitter_token_secret")
        
        if st.button("连接 Twitter", key="connect_twitter"):
            if all([twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret]):
                try:
                    # 验证 Twitter API
                    auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
                    auth.set_access_token(twitter_access_token, twitter_access_secret)
                    api = tweepy.API(auth)
                    
                    # 测试连接
                    api.verify_credentials()
                    st.session_state.authenticated_platforms['twitter'] = {
                        'api': api,
                        'auth': auth,
                        'credentials': {
                            'api_key': twitter_api_key,
                            'api_secret': twitter_api_secret,
                            'access_token': twitter_access_token,
                            'access_secret': twitter_access_secret
                        }
                    }
                    st.success("✅ Twitter 连接成功！")
                except Exception as e:
                    st.error(f"❌ Twitter 连接失败: {str(e)}")
            else:
                st.warning("请填写所有 Twitter API 凭据")
    
    # Facebook 配置
    st.subheader("📘 Facebook")
    with st.expander("Facebook API 设置"):
        fb_page_access_token = st.text_input("Facebook Page Access Token", type="password", key="fb_token")
        fb_page_id = st.text_input("Facebook Page ID", key="fb_page_id")
        
        if st.button("连接 Facebook", key="connect_facebook"):
            if fb_page_access_token and fb_page_id:
                try:
                    # 验证 Facebook token
                    graph = facebook.GraphAPI(access_token=fb_page_access_token, version="3.1")
                    page_info = graph.get_object(fb_page_id)
                    
                    st.session_state.authenticated_platforms['facebook'] = {
                        'graph': graph,
                        'page_id': fb_page_id,
                        'token': fb_page_access_token
                    }
                    st.success(f"✅ Facebook 连接成功！页面: {page_info.get('name', 'Unknown')}")
                except Exception as e:
                    st.error(f"❌ Facebook 连接失败: {str(e)}")
            else:
                st.warning("请填写 Facebook 凭据")
    
    # LinkedIn 配置
    st.subheader("💼 LinkedIn")
    with st.expander("LinkedIn API 设置"):
        linkedin_access_token = st.text_input("LinkedIn Access Token", type="password", key="linkedin_token")
        linkedin_person_id = st.text_input("LinkedIn Person/Company ID", key="linkedin_id")
        
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
                        st.success(f"✅ LinkedIn 连接成功！用户: {user_info.get('localizedFirstName', '')} {user_info.get('localizedLastName', '')}")
                    else:
                        st.error("❌ LinkedIn 连接失败")
                except Exception as e:
                    st.error(f"❌ LinkedIn 连接失败: {str(e)}")
            else:
                st.warning("请填写 LinkedIn 凭据")
    
    # 显示已连接平台
    st.header("✅ 已连接平台")
    for platform in st.session_state.authenticated_platforms:
        st.success(f"✅ {platform.title()}")

# 主内容区域
if not st.session_state.authenticated_platforms:
    st.warning("请在侧边栏配置并连接至少一个社交媒体平台")
    st.info("""
    ### 如何获取 API 凭据：
    
    **Twitter/X:**
    1. 访问 [developer.twitter.com](https://developer.twitter.com)
    2. 创建应用获取 API Keys 和 Tokens
    
    **Facebook:**
    1. 访问 [developers.facebook.com](https://developers.facebook.com)
    2. 创建应用并获取页面访问令牌
    
    **LinkedIn:**
    1. 访问 [developer.linkedin.com](https://developer.linkedin.com)
    2. 创建应用并获取访问令牌
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
                height=200
            )
            
            # 媒体上传
            uploaded_files = st.file_uploader(
                "上传图片",
                accept_multiple_files=True,
                type=['png', 'jpg', 'jpeg', 'gif']
            )
            
            # 链接添加
            link_url = st.text_input("添加链接（可选）", placeholder="https://...")
            
            # 预览上传的图片
            if uploaded_files:
                st.subheader("📷 图片预览")
                cols = st.columns(min(len(uploaded_files), 3))
                for i, uploaded_file in enumerate(uploaded_files):
                    with cols[i % 3]:
                        image = Image.open(uploaded_file)
                        st.image(image, caption=uploaded_file.name, use_column_width=True)
        
        with col2:
            st.subheader("🎯 发布设置")
            
            # 选择平台
            selected_platforms = []
            for platform in st.session_state.authenticated_platforms:
                if st.checkbox(f"发布到 {platform.title()}", value=True, key=f"select_{platform}"):
                    selected_platforms.append(platform)
            
            # 发布时间
            publish_now = st.radio("发布时间", ["立即发布", "定时发布"])
            
            if publish_now == "定时发布":
                schedule_date = st.date_input("选择日期", min_value=datetime.now().date())
                schedule_time = st.time_input("选择时间")
                st.info("定时发布功能需要后台服务支持")
            
            # 平台特定设置
            st.subheader("🔧 平台设置")
            
            # Twitter 特定设置
            if 'twitter' in selected_platforms:
                st.write("**Twitter 设置**")
                twitter_thread = st.checkbox("作为推特串发布（超过280字符时）")
            
            # Facebook 特定设置
            if 'facebook' in selected_platforms:
                st.write("**Facebook 设置**")
                fb_privacy = st.selectbox("隐私设置", ["PUBLIC", "FRIENDS", "SELF"])
        
        # 发布按钮
        if st.button("🚀 发布到选中平台", type="primary", use_container_width=True):
            if not post_content.strip() and not uploaded_files:
                st.error("请输入内容或上传图片")
            elif not selected_platforms:
                st.error("请至少选择一个发布平台")
            else:
                publish_results = {}
                
                # 发布到各个平台
                for platform in selected_platforms:
                    with st.spinner(f"正在发布到 {platform.title()}..."):
                        try:
                            if platform == 'twitter':
                                result = publish_to_twitter(
                                    post_content, 
                                    uploaded_files, 
                                    link_url,
                                    st.session_state.authenticated_platforms['twitter']
                                )
                                publish_results[platform] = result
                                
                            elif platform == 'facebook':
                                result = publish_to_facebook(
                                    post_content, 
                                    uploaded_files, 
                                    link_url,
                                    st.session_state.authenticated_platforms['facebook'],
                                    fb_privacy if 'facebook' in selected_platforms else 'PUBLIC'
                                )
                                publish_results[platform] = result
                                
                            elif platform == 'linkedin':
                                result = publish_to_linkedin(
                                    post_content, 
                                    uploaded_files, 
                                    link_url,
                                    st.session_state.authenticated_platforms['linkedin']
                                )
                                publish_results[platform] = result
                                
                        except Exception as e:
                            publish_results[platform] = {'success': False, 'error': str(e)}
                
                # 显示发布结果
                st.header("📊 发布结果")
                for platform, result in publish_results.items():
                    if result['success']:
                        st.success(f"✅ {platform.title()}: 发布成功！")
                        if 'post_id' in result:
                            st.code(f"帖子 ID: {result['post_id']}")
                    else:
                        st.error(f"❌ {platform.title()}: {result['error']}")
    
    with tab2:
        st.header("📊 发布历史")
        st.info("发布历史功能需要数据库支持来存储历史记录")
        
        # 这里可以添加数据库查询逻辑来显示历史发布记录
        if 'publish_history' not in st.session_state:
            st.session_state.publish_history = []
        
        if st.session_state.publish_history:
            for i, record in enumerate(st.session_state.publish_history):
                with st.expander(f"发布记录 {i+1} - {record['timestamp']}"):
                    st.write(f"**内容**: {record['content'][:100]}...")
                    st.write(f"**平台**: {', '.join(record['platforms'])}")
                    st.write(f"**状态**: {record['status']}")
        else:
            st.info("暂无发布历史")
    
    with tab3:
        st.header("⚙️ 应用设置")
        
        # 断开平台连接
        st.subheader("🔌 平台连接管理")
        for platform in list(st.session_state.authenticated_platforms.keys()):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"✅ {platform.title()} - 已连接")
            with col2:
                if st.button(f"断开", key=f"disconnect_{platform}"):
                    del st.session_state.authenticated_platforms[platform]
                    st.rerun()
        
        # 清除所有连接
        if st.button("🔄 重置所有连接", type="secondary"):
            st.session_state.authenticated_platforms = {}
            st.rerun()

# 发布函数定义
def publish_to_twitter(content, images, link, twitter_config):
    """发布到 Twitter"""
    try:
        api = twitter_config['api']
        
        # 处理内容长度（Twitter 限制）
        full_content = content
        if link:
            full_content += f"\n{link}"
        
        media_ids = []
        
        # 上传图片
        if images:
            for image_file in images:
                # 将图片保存为临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    image = Image.open(image_file)
                    image.save(tmp_file.name, 'JPEG')
                    
                    # 上传媒体
                    media = api.media_upload(tmp_file.name)
                    media_ids.append(media.media_id)
                    
                    # 清理临时文件
                    os.unlink(tmp_file.name)
        
        # 发布推文
        if media_ids:
            tweet = api.update_status(status=full_content, media_ids=media_ids)
        else:
            tweet = api.update_status(status=full_content)
        
        return {'success': True, 'post_id': tweet.id_str}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def publish_to_facebook(content, images, link, fb_config, privacy='PUBLIC'):
    """发布到 Facebook"""
    try:
        graph = fb_config['graph']
        page_id = fb_config['page_id']
        
        # 准备发布数据
        post_data = {
            'message': content,
            'privacy': {'value': privacy}
        }
        
        if link:
            post_data['link'] = link
        
        # 如果有图片，使用 photos 端点
        if images:
            # Facebook 支持多图片发布，但需要先上传图片
            photo_ids = []
            for image_file in images:
                # 上传图片
                image_data = image_file.read()
                image_file.seek(0)  # 重置文件指针
                
                photo = graph.put_photo(
                    image=image_data,
                    album_path=f"{page_id}/photos",
                    published=False  # 先不发布
                )
                photo_ids.append({'media_fbid': photo['id']})
            
            # 发布带图片的帖子
            post = graph.put_object(
                parent_object=page_id,
                connection_name='feed',
                message=content,
                attached_media=photo_ids
            )
        else:
            # 发布纯文本或带链接的帖子
            post = graph.put_object(
                parent_object=page_id,
                connection_name='feed',
                **post_data
            )
        
        return {'success': True, 'post_id': post['id']}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def publish_to_linkedin(content, images, link, linkedin_config):
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
        
        # 如果有链接，添加到分享内容
        if link:
            post_data['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory'] = 'ARTICLE'
            post_data['specificContent']['com.linkedin.ugc.ShareContent']['media'] = [{
                'status': 'READY',
                'originalUrl': link
            }]
        
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

# 依赖包安装提示
st.sidebar.markdown("""
---
### 📦 安装依赖
运行此应用需要安装以下包：
```bash
pip install streamlit tweepy facebook-sdk requests pillow
```
""")