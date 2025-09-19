import streamlit as st
import requests
import json
import time

# Streamlit sayfa yapılandırması
st.set_page_config(
    page_title="🌟 Motivasyon Koçun",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile stil ekleme
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .goal-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4ECDC4;
        margin: 1rem 0;
    }
    .motivation-box {
        background-color: #fff8dc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF6B6B;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sidebar-info {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown('<h1 class="main-header">🌟 Kişisel Motivasyon Koçun 🌟</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## ⚙️ Ayarlar")

# API Token girişi
api_token = st.sidebar.text_input(
    "🔑 Hugging Face API Token:",
    type="password",
    help="Hugging Face hesabınızdan Settings > Access Tokens'dan alabilirsiniz"
)

# Model seçimi
models_list = [
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.1-70B-Instruct", 
    "microsoft/Phi-3.5-mini-instruct",
    "Qwen/Qwen2.5-32B-Instruct",
    "microsoft/Phi-3-medium-4k-instruct"
]

selected_model = st.sidebar.selectbox(
    "🤖 Model Seçimi:",
    models_list,
    index=2,  # Phi-3.5-mini varsayılan
    help="Daha büyük modeller daha iyi sonuç verir ama daha yavaştır"
)

# Sidebar bilgilendirme
st.sidebar.markdown("""
<div class="sidebar-info">
<h4>📝 Nasıl Kullanılır?</h4>
<ol>
<li>API Token'ınızı girin</li>
<li>Hedefinizi yazın</li>
<li>Motivasyon mesajınızı alın!</li>
</ol>
</div>
""", unsafe_allow_html=True)

# API ayarları
API_URL = "https://router.huggingface.co/v1/chat/completions"

@st.cache_data(ttl=300)  # 5 dakika cache
def test_model(model_name, token):
    """Modelin çalışıp çalışmadığını test et"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
        "model": model_name,
        "max_tokens": 10
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        return response.status_code == 200, response.status_code
    except Exception as e:
        return False, str(e)

def get_motivation_message(user_goal, model_name, token):
    """Motivasyon mesajı üret"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": '''Sen samimi bir kişisel motivasyon koçusun ve insanlara olabildiğince motive
                 edici mesajlar yazarak onlara hedeflerine göre motive verirsin eğer senden etik olmayan konularda motive isterlerse onlara bu konudan kibarca uyarıp
                 etik olmayan konularda mesaj yazamayacağını belirtmelisin.Motivasyon mesajların olabildiğince kısa ve net olsun.
                '''
            },
            {
                "role": "user", 
                "content": f"'{user_goal}' hedefi için bana kısa ve ilham verici bir motivasyon mesajı yaz. Sadece motivasyon mesajını ver, ekstra açıklama yapma."
            }
        ],
        "model": model_name,
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        with st.spinner('🤖 Motivasyon mesajınız hazırlanıyor...'):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            return True, result["choices"][0]["message"]["content"]
        else:
            return False, f"Hata: {response.status_code} - {response.text[:200]}"
            
    except Exception as e:
        return False, f"Bağlantı hatası: {str(e)}"

# Ana uygulama alanı
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 🎯 Hedefinizi Belirleyin")
    
    # Hedef girişi
    user_goal = st.text_input(
        "Hangi konuda motivasyona ihtiyacınız var?",
        placeholder="Örnek: üretkenliğimi artırmak, spor yapmaya başlamak...",
        help="Hedefinizi açık ve net bir şekilde yazın"
    )
    
    # Hazır hedefler
    st.markdown("### 💡 Popüler Hedefler:")
    quick_goals = [
        "üretkenliğimi artırmak",
        "spor yapmaya başlamak", 
        "yeni bir dil öğrenmek",
        "erken kalkmak",
        "daha çok kitap okumak",
        "sağlıklı beslenmeye başlamak",
        "meditasyon yapmak",
        "yeni bir hobi edinmek"
    ]
    
    # Hazır hedefleri 2 sütunda göster
    goal_col1, goal_col2 = st.columns(2)
    
    for i, goal in enumerate(quick_goals):
        target_col = goal_col1 if i % 2 == 0 else goal_col2
        
        if target_col.button(f"🎯 {goal}", key=f"goal_{i}"):
            st.session_state.selected_goal = goal
            user_goal = goal
            st.rerun()

with col2:
    st.markdown("## 📊 Durum")
    
    # API Token kontrolü
    if api_token:
        st.success("✅ API Token girildi")
        
        # Model test et
        if st.button("🧪 Modeli Test Et"):
            with st.spinner("Model test ediliyor..."):
                success, result = test_model(selected_model, api_token)
                
            if success:
                st.success(f"✅ {selected_model.split('/')[-1]} modeli çalışıyor!")
            else:
                st.error(f"❌ Model testi başarısız: {result}")
    else:
        st.warning("⚠️ API Token gerekli")
    
    # Seçilen model bilgisi
    st.info(f"🤖 **Seçili Model:**\n{selected_model.split('/')[-1]}")

# Motivasyon oluşturma
if st.button("🌟 Motivasyon Mesajı Al", type="primary", use_container_width=True):
    if not api_token:
        st.error("❌ Lütfen API Token'ınızı girin!")
    elif not user_goal:
        st.error("❌ Lütfen bir hedef belirleyin!")
    else:
        success, message = get_motivation_message(user_goal, selected_model, api_token)
        
        if success:
            st.markdown(f"""
            <div class="goal-box">
                <h4>🎯 Hedef: {user_goal}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="motivation-box">
                <h4>💡 Motivasyon Mesajınız:</h4>
                <p style="font-size: 1.2rem; line-height: 1.6;">{message}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Başarı efekti
            st.balloons()
            
            # Paylaşma butonları
            st.markdown("### 📤 Paylaş")
            share_text = f"🌟 Motivasyon: {message}"
            
            col_share1, col_share2, col_share3 = st.columns(3)
            
            with col_share1:
                st.markdown(f"[📱 WhatsApp'ta Paylaş](https://wa.me/?text={share_text})")
            
            with col_share2:
                st.markdown(f"[🐦 Twitter'da Paylaş](https://twitter.com/intent/tweet?text={share_text})")
            
            with col_share3:
                if st.button("📋 Kopyala"):
                    st.code(message)
        else:
            st.error(f"❌ {message}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🌟 Kişisel Motivasyon Koçunuz - Powered by Hugging Face</p>
    <p><small>Her gün yeni hedefler, her gün yeni motivasyon! 💪</small></p>
</div>
""", unsafe_allow_html=True)

# Session state başlatma
if 'selected_goal' not in st.session_state:
    st.session_state.selected_goal = ""
