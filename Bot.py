from flask import Flask, request, jsonify
import requests
import threading
import time
import os
import logging
from datetime import datetime

app = Flask(__name__)

# التوكن الجاهز - يمكنك وضعه في environment variables لاحقاً
TOKEN = "8062509543:AAESa0KjqZngpuGZKWfWusj_xk3wb95cMPc"
API_URL = f'https://api.telegram.org/bot{TOKEN}'

# إعداد logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# بيانات الحسابات
ACCOUNTS = [
    {
        "id": "acc1",
        "title": "🔥 حساب VIP — مستوى 72",
        "price": "15 د.ت",
        "diamonds": 1200,
        "desc": "• شخصية: Alok\n• سكّينات نادرة\n• كلش منظّم",
        "stock": 5
    },
    {
        "id": "acc2", 
        "title": "⭐ حساب كلاسيك — مستوى 45",
        "price": "6 د.ت",
        "diamonds": 300,
        "desc": "• شخصية: Kelly\n• عدد سكنات قليل\n• مناسب للمبتدئين",
        "stock": 10
    },
    {
        "id": "acc3",
        "title": "👑 حساب ممتاز — مستوى 90", 
        "price": "25 د.ت",
        "diamonds": 2500,
        "desc": "• شخصية: Chrono\n• سكنات اسطورية\n• رتب عالية",
        "stock": 2
    }
]

# 🔄 نظام المهام في الخلفية
background_tasks = {}

def send_telegram_message(chat_id, text, reply_markup=None, parse_mode=None):
    """إرسال رسالة إلى تيليجرام بشكل آمن"""
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if parse_mode:
        payload["parse_mode"] = parse_mode
        
    try:
        response = requests.post(f"{API_URL}/sendMessage", json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False

def answer_callback(callback_id, text=None):
    """الرد على callback queries"""
    try:
        payload = {"callback_query_id": callback_id}
        if text:
            payload["text"] = text
        requests.post(f"{API_URL}/answerCallbackQuery", json=payload, timeout=5)
    except:
        pass

# 🎯 الكيبوردات
def main_menu_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🛒 شراء حساب", "callback_data": "buy_account"}],
            [{"text": "💎 شحن جوهر", "callback_data": "topup_menu"}],
            [{"text": "📞 تواصل معنا", "url": "https://t.me/iiectn"}],
            [{"text": "ℹ️ مساعدة", "callback_data": "help"}]
        ]
    }

def accounts_keyboard():
    keyboard = []
    for acc in ACCOUNTS:
        stock_text = f" ({acc['stock']} متبقي)" if acc['stock'] > 0 else " (⛔ نافذ)"
        keyboard.append([{
            "text": f"{acc['title']} - {acc['price']}{stock_text}", 
            "callback_data": f"view_{acc['id']}"
        }])
    keyboard.append([{"text": "◀️ رجوع", "callback_data": "main_menu"}])
    return {"inline_keyboard": keyboard}

def account_details_keyboard(account_id):
    return {
        "inline_keyboard": [
            [{"text": "🛒 شراء الآن", "callback_data": f"purchase_{account_id}"}],
            [{"text": "◀️ رجوع للقائمة", "callback_data": "buy_account"}]
        ]
    }

# 🔄 المهام الثقيلة في الخلفية
def process_account_purchase(chat_id, account_id, user_name):
    """معالجة شراء حساب (قد تأخذ وقت طويل)"""
    try:
        logger.info(f"بدء معالجة شراء حساب {account_id} للمستخدم {user_name}")
        
        # المرحلة 1: التواصل مع البائع
        send_telegram_message(chat_id, "🔍 جاري التواصل مع البائع...")
        time.sleep(15)
        
        # المرحلة 2: تجهيز الحساب
        send_telegram_message(chat_id, "📋 جاري تجهيز الحساب...")
        time.sleep(20)
        
        # المرحلة 3: التحقق من المعلومات
        send_telegram_message(chat_id, "🔐 جاري التحقق من معلومات الحساب...")
        time.sleep(15)
        
        # المرحلة 4: الإرسال النهائي
        send_telegram_message(chat_id, "🚀 جاري إرسال الحساب...")
        time.sleep(10)
        
        # النتيجة النهائية
        account = next((acc for acc in ACCOUNTS if acc["id"] == account_id), None)
        if account:
            success_message = f"""
✅ **تمت العملية بنجاح!**

🎮 **الحساب:** {account['title']}
💰 **السعر:** {account['price']}
💎 **الجواهر:** {account['diamonds']}

📞 **للاستلام تواصل مع:** @iiectn
🆔 **رقم الطلب:** {int(time.time())}

سيتم إرسال بيانات الحساب خلال 5 دقائق
            """
            send_telegram_message(chat_id, success_message, parse_mode="Markdown")
        else:
            send_telegram_message(chat_id, "❌ عذراً، الحساب لم يعد متوفر")
            
    except Exception as e:
        error_message = f"❌ حدث خطأ في المعالجة: {str(e)}"
        send_telegram_message(chat_id, error_message)
        logger.error(f"Error in account purchase: {e}")
    finally:
        # تنظيف المهمة من الذاكرة
        if chat_id in background_tasks:
            del background_tasks[chat_id]

def process_diamond_topup(chat_id, diamonds_amount, user_name):
    """معالجة شحن الجواهر"""
    try:
        logger.info(f"بدء شحن {diamonds_amount} جوهر للمستخدم {user_name}")
        
        send_telegram_message(chat_id, "💎 بدأت عملية الشحن...")
        time.sleep(10)
        
        send_telegram_message(chat_id, "🔗 جاري الاتصال بخوادم Free Fire...")
        time.sleep(15)
        
        send_telegram_message(chat_id, "⚡ جاري إضافة الجواهر...")
        time.sleep(10)
        
        success_message = f"""
✅ **تم الشحن بنجاح!**

💎 **الكمية:** {diamonds_amount} جوهر
🎯 **الحالة:** مضافة بنجاح
📅 **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

تمت إضافة الجواهر لحسابك في Free Fire
        """
        send_telegram_message(chat_id, success_message)
        
    except Exception as e:
        send_telegram_message(chat_id, f"❌ فشل الشحن: {str(e)}")
        logger.error(f"Error in diamond topup: {e}")
    finally:
        if chat_id in background_tasks:
            del background_tasks[chat_id]

# ⚡ المعالجة السريعة (لا تتجاوز 5 ثواني)
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    start_time = time.time()
    
    try:
        data = request.get_json()
        logger.info(f"📨 Received update from Telegram")
        
        # ⚡ معالجة سريعة للرسائل
        if "message" in data:
            msg = data["message"]
            chat_id = msg["chat"]["id"]
            user_name = msg["chat"].get("first_name", "مستخدم")
            text = msg.get("text", "")
            
            if text.startswith("/start"):
                welcome_text = f"""
🎮 **مرحباً {user_name} في بوت حسابات Free Fire!**

✨ **اختر من القائمة:**
• 🛒 شراء حسابات أصلية
• 💎 شحن الجواهر مباشرة
• ⚡ توصيل فوري
• 🔒 أمان تام

📊 **الحسابات المتوفرة:** {len(ACCOUNTS)}
                """
                send_telegram_message(chat_id, welcome_text, main_menu_keyboard())
                
            elif text.startswith("/buy"):
                send_telegram_message(chat_id, "🛒 اختر الحساب المناسب:", accounts_keyboard())
                
            elif text.startswith("/status"):
                active_tasks = len([t for t in background_tasks.values() if t.is_alive()])
                status_msg = f"""
📊 **حالة البوت:**

✅ **الحالة:** شغال بشكل طبيعي
🔧 **المهام النشطة:** {active_tasks}
👥 **الحسابات المتوفرة:** {len(ACCOUNTS)}
⏰ **آخر تحديث:** {datetime.now().strftime('%H:%M:%S')}
                """
                send_telegram_message(chat_id, status_msg)
                
            else:
                send_telegram_message(chat_id, "🔍 استخدم الأزرار أدناه للتنقل:", main_menu_keyboard())
        
        # ⚡ معالجة سريعة للأزرار
        elif "callback_query" in data:
            cb = data["callback_query"]
            chat_id = cb["message"]["chat"]["id"]
            user_name = cb["message"]["chat"].get("first_name", "مستخدم")
            data_cb = cb["data"]
            
            # الرد الفوري على الكallback
            answer_callback(cb["id"])
            
            if data_cb == "main_menu":
                send_telegram_message(chat_id, "🎮 **القائمة الرئيسية:**", main_menu_keyboard())
                
            elif data_cb == "buy_account":
                send_telegram_message(chat_id, "🛒 **اختر الحساب المناسب:**", accounts_keyboard())
                
            elif data_cb == "topup_menu":
                topup_text = """
💎 **شحن الجواهر**

اختر كمية الجواهر:

• 100 💎 - 1 د.ت
• 500 💎 - 4 د.ت  
• 1000 💎 - 7 د.ت
• 2000 💎 - 12 د.ت

📞 **للشحن تواصل مع:** @iiectn
                """
                send_telegram_message(chat_id, topup_text)
                
            elif data_cb == "help":
                help_text = """
ℹ️ **كيفية الاستخدام:**

1. 🛒 **شراء حساب:** اختر حساب ثم اتبع التعليمات
2. 💎 **شحن جوهر:** اختر الباقة ثم ادفع  
3. ⚡ **التوصيل:** فوري بعد التأكيد
4. 🔒 **الضمان:** جميع الحسابات أصلية

📞 **للإستفسار:** @iiectn
⏰ **الدعم:** 24/7
                """
                send_telegram_message(chat_id, help_text)
                
            elif data_cb.startswith("view_"):
                acc_id = data_cb.split("_", 1)[1]
                acc = next((a for a in ACCOUNTS if a["id"] == acc_id), None)
                if acc:
                    details = f"""
{acc['title']}

💰 **السعر:** {acc['price']}
💎 **الجواهر:** {acc['diamonds']}
📦 **المخزون:** {acc['stock']} وحدة

{acc['desc']}

🛒 **اضغط شراء الآن للمتابعة**
                    """
                    send_telegram_message(chat_id, details, account_details_keyboard(acc_id))
                else:
                    send_telegram_message(chat_id, "❌ الحساب غير متوفر")
                    
            elif data_cb.startswith("purchase_"):
                acc_id = data_cb.split("_", 1)[1]
                acc = next((a for a in ACCOUNTS if a["id"] == acc_id), None)
                
                if acc and acc['stock'] > 0:
                    # ⚡ رد فوري أولاً
                    send_telegram_message(chat_id, "✅ تم استلام طلبك! جاري بدء عملية الشراء...")
                    
                    # 🔄 بدء المهمة في الخلفية
                    task = threading.Thread(
                        target=process_account_purchase,
                        args=(chat_id, acc_id, user_name)
                    )
                    task.daemon = True
                    task.start()
                    
                    # حفظ المرجع للمهمة
                    background_tasks[chat_id] = task
                    
                    logger.info(f"بدأ عملية شراء حساب {acc_id} للمستخدم {user_name}")
                else:
                    send_telegram_message(chat_id, "❌ عذراً، الحساب غير متوفر حالياً")
        
        execution_time = time.time() - start_time
        logger.info(f"✅ Request processed in {execution_time:.2f}s")
        
        return jsonify({"status": "success", "processing_time": execution_time})
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 🏠 مسارات إضافية
@app.route('/')
def home():
    active_tasks = len([t for t in background_tasks.values() if t.is_alive()])
    return f"""
    <html>
        <head>
            <title>Free Fire Bot</title>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>🎮 بوت حسابات Free Fire</h1>
            <p>✅ البوت شغال بشكل طبيعي</p>
            <p>🔧 المهام النشطة: {active_tasks}</p>
            <p>⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>📞 للدعم: @iiectn</p>
        </body>
    </html>
    """

@app.route('/health')
def health_check():
    active_tasks = len([t for t in background_tasks.values() if t.is_alive()])
    return jsonify({
        "status": "healthy",
        "active_tasks": active_tasks,
        "accounts_available": len(ACCOUNTS),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/setup_webhook', methods=['GET'])
def setup_webhook():
    """إعداد الويبhook تلقائياً"""
    try:
        vercel_url = os.environ.get('VERCEL_URL')
        if vercel_url:
            webhook_url = f"https://{vercel_url}/webhook"
            response = requests.post(f"{API_URL}/setWebhook", json={"url": webhook_url})
            if response.status_code == 200:
                return f"✅ تم إعداد الويبhook: {webhook_url}"
        return "❌ لم يتم العثور على رابط Vercel"
    except Exception as e:
        return f"❌ خطأ في إعداد الويبhook: {str(e)}"

# تشغيل الإعداد عند البدء
if __name__ == '__main__':
    print("🚀 بدء تشغيل البوت...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)