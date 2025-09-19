import requests
from google.colab import userdata
import json

# Hugging Face Router API
API_URL = "https://router.huggingface.co/v1/chat/completions"

# API token'ı Google Colab secrets'tan al
hf_token = userdata.get('HF_TOKEN')
headers = {
    "Authorization": f"Bearer {hf_token}",
    "Content-Type": "application/json"
}

def test_model(model_name):
    """Modelin çalışıp çalışmadığını test et"""
    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
        "model": model_name,
        "max_tokens": 10
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status: {response.status_code}, Error: {response.text[:200]}"
    except Exception as e:
        return False, str(e)

def get_motivation_message(user_goal, model_name):
    """Kullanıcının hedefine göre motivasyon mesajı üret"""
    
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
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Hata: {response.status_code} - {response.text[:100]}"
            
    except Exception as e:
        return f"Bağlantı hatası: {str(e)}"

# Test edilecek modeller
models_to_test = [
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.1-70B-Instruct", 
    "microsoft/Phi-3.5-mini-instruct",
    "Qwen/Qwen2.5-32B-Instruct",
    "microsoft/Phi-3-medium-4k-instruct"
]

print("🔍 Hugging Face Router API modelleri test ediliyor...\n")

working_model = None

for model in models_to_test:
    print(f"Test: {model}")
    success, result = test_model(model)
    
    if success:
        print(f"✅ {model} çalışıyor!")
        working_model = model
        break
    else:
        print(f"❌ {model}: {result}")

print("\n" + "="*60)

if working_model:
    print(f"🌟 {working_model.split('/')[-1]} modeli ile motivasyon uygulaması! 🌟\n")
    
    # İlk test mesajı
    print("📋 İlk test:")
    test_message = get_motivation_message("kendime güvenmek", working_model)
    print(f"💡 Test mesajı: {test_message}\n")
    print("-" * 50)
    
    # Farklı hedefler için motivasyon mesajları
    goals = [
        "üretkenliğimi artırmak",
        "spor yapmaya başlamak", 
        "yeni bir dil öğrenmek",
        "erken kalkmak",
        "daha çok kitap okumak",
        "sağlıklı beslenmeye başlamak"
    ]

    for goal in goals:
        print(f"📌 Hedef: {goal}")
        message = get_motivation_message(goal, working_model)
        print(f"💡 Motivasyon: {message}\n")
        print("-" * 40)
        
else:
    print("❌ Hiçbir model çalışmıyor.")
    print("\n🔧 Kontrol listesi:")
    print("1. HF_TOKEN doğru mu?")
    print("2. Token'ın 'read' yetkisi var mı?") 
    print("3. Hugging Face hesabı aktif mi?")
    print("4. İnternet bağlantısı stabil mi?")
    
    print("\n🔄 Manuel test için:")
    print("response = requests.get('https://huggingface.co/api/whoami', headers=headers)")
    print("print(response.json())")  # Bu sizin kullanıcı bilgilerinizi gösterecek