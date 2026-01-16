"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تطبيق اختبار الحب الرومانسي
Romantic Love Quiz Web Application
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version: 2.0
Language: Python 3.7+
Framework: Flask 2.3.3
Author: Love Quiz Team
Date: 2024
Description: تطبيق ويب تفاعلي يختبر مشاعر الحب الرومانسية
            مع دعم أنواع أسئلة متعددة (MCQ، True/False)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ==================== المكتبات والاستيراد ====================
from flask import (
    Flask, render_template, request, jsonify, 
    redirect, url_for, session
)
import json
import os
from functools import wraps
import secrets


# ==================== تهيئة التطبيق ====================
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


# ==================== الإعدادات والثوابت ====================
class Config:
    """إعدادات التطبيق"""
    QUESTIONS_FILE = 'questions_ar.json'
    ADMIN_PASSWORD = 'love2024'
    MAX_QUESTIONS = 100
    ENCODING = 'utf-8'


# ==================== دوال المساعدة ====================

def load_questions():
    """
    تحميل الأسئلة من ملف JSON
    
    Returns:
        list: قائمة الأسئلة أو قائمة فارغة في حالة عدم وجود الملف
    
    Raises:
        JSONDecodeError: عند فشل فك تشفير JSON
    """
    try:
        if os.path.exists(Config.QUESTIONS_FILE):
            with open(Config.QUESTIONS_FILE, 'r', encoding=Config.ENCODING) as f:
                questions = json.load(f)
                # التحقق من صحة البيانات
                if isinstance(questions, list):
                    return questions
                return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"خطأ في تحميل الأسئلة: {e}")
        return []
    
    return []


def save_questions(questions):
    """
    حفظ الأسئلة في ملف JSON
    
    Args:
        questions (list): قائمة الأسئلة للحفظ
    
    Returns:
        bool: True عند النجاح، False عند الفشل
    """
    try:
        with open(Config.QUESTIONS_FILE, 'w', encoding=Config.ENCODING) as f:
            json.dump(
                questions, f, 
                indent=2, 
                ensure_ascii=False,
                sort_keys=False
            )
        return True
    except IOError as e:
        print(f"خطأ في حفظ الأسئلة: {e}")
        return False


def find_question_by_id(questions, q_id):
    """
    البحث عن سؤال بواسطة المعرف
    
    Args:
        questions (list): قائمة الأسئلة
        q_id (int): معرف السؤال
    
    Returns:
        dict or None: السؤال المطلوب أو None
    """
    return next((q for q in questions if q.get('id') == q_id), None)


def validate_question_data(data):
    """
    التحقق من صحة بيانات السؤال
    
    Args:
        data (dict): بيانات السؤال
    
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['question', 'options', 'correct_answer']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"الحقل '{field}' مطلوب"
    
    if data.get('type') not in ['mcq', 'tf']:
        return False, "نوع السؤال يجب أن يكون 'mcq' أو 'tf'"
    
    return True, None


def require_admin(f):
    """
    ديكوريتور للتحقق من مصادقة المسؤول
    
    Args:
        f (function): الدالة المراد حمايتها
    
    Returns:
        function: دالة مزينة
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== المسارات الأساسية ====================

@app.route('/')
def index():
    """
    صفحة الاختبار الرئيسية
    Main Quiz Page
    """
    questions = load_questions()
    return render_template(
        'index_ar.html', 
        questions=questions
    )


@app.route('/api/submit', methods=['POST'])
def submit_quiz():
    """
    نقطة API لإرسال الإجابات والحصول على النتائج
    Submit quiz answers and calculate score
    
    JSON Request Format:
        {
            "answers": {
                "question_id": "selected_answer",
                ...
            }
        }
    
    Returns:
        JSON: {
            "score": int,
            "total": int,
            "percentage": float
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'بيانات غير صحيحة. يرجى التأكد من إرسال الإجابات بشكل صحيح'}), 400
        
        answers = data.get('answers', {})
        if not isinstance(answers, dict):
            return jsonify({'error': 'الإجابات يجب أن تكون قاموس صحيح'}), 400
        
        questions = load_questions()
        
        if not questions:
            return jsonify({'error': 'لا توجد أسئلة محفوظة. يرجى إضافة أسئلة من لوحة التحكم'}), 404
        
        score = 0
        total = len(questions)
        
        # حساب النتيجة بمقارنة الإجابات الصحيحة
        for q_id, user_answer in answers.items():
            question = find_question_by_id(questions, int(q_id))
            if question:
                correct_answer = question.get('correct_answer')
                # تحويل الإجابات للمقارنة الصحيحة
                try:
                    # محاولة تحويل كلا الطرفين إلى رقم للمقارنة
                    correct_int = int(correct_answer) if isinstance(correct_answer, (int, str)) else correct_answer
                    user_int = int(user_answer) if isinstance(user_answer, str) else user_answer
                    
                    if user_int == correct_int:
                        score += 1
                except (ValueError, TypeError):
                    # إذا فشل التحويل، قارن كـ نصوص
                    if str(correct_answer) == str(user_answer):
                        score += 1
        
        percentage = (score / total * 100) if total > 0 else 0
        
        return jsonify({
            'score': score,
            'total': total,
            'percentage': round(percentage, 2)
        })
    
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'خطأ في معالجة البيانات: {str(e)}'}), 400
    except Exception as e:
        print(f"خطأ غير متوقع في /api/submit: {e}")
        return jsonify({'error': 'حدث خطأ غير متوقع. يرجى المحاولة لاحقاً'}), 500


# ==================== مسارات لوحة التحكم ====================

@app.route('/admin', methods=['GET', 'POST'])
@require_admin
def admin_dashboard():
    """
    لوحة تحكم المسؤول لإدارة الأسئلة
    Admin Dashboard for Question Management
    """
    return render_template('admin_ar.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    صفحة دخول المسؤول
    Admin Login Page
    
    POST Parameters:
        password (str): كلمة مرور المسؤول
    """
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        
        if not password:
            return render_template(
                'admin_login_ar.html', 
                error='الرجاء إدخال كلمة المرور'
            )
        
        if password == Config.ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            session.permanent = False  # جلسة المتصفح
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template(
                'admin_login_ar.html', 
                error='كلمة المرور غير صحيحة'
            )
    
    return render_template('admin_login_ar.html')


@app.route('/admin/logout')
def admin_logout():
    """
    تسجيل خروج المسؤول
    Admin Logout
    """
    session.pop('admin_authenticated', None)
    return redirect(url_for('index'))


# ==================== API endpoints لإدارة الأسئلة ====================

@app.route('/api/admin/add-question', methods=['POST'])
@require_admin
def add_question():
    """
    نقطة API لإضافة سؤال جديد
    Add New Question Endpoint
    
    JSON Request Format:
        {
            "type": "mcq" or "tf",
            "question": "نص السؤال",
            "options": ["خيار1", "خيار2", ...],
            "correct_answer": "الإجابة الصحيحة",
            "category": "الفئة"
        }
    
    Returns:
        JSON: {
            "success": bool,
            "question": dict or error message
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'بيانات غير صحيحة'}), 400
        
        # التحقق من صحة البيانات
        is_valid, error_msg = validate_question_data(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        questions = load_questions()
        
        # إنشاء سؤال جديد بمعرف فريد
        new_id = max([q.get('id', 0) for q in questions], default=0) + 1
        
        new_question = {
            'id': new_id,
            'type': data.get('type', 'mcq'),
            'question': data.get('question'),
            'options': data.get('options'),
            'correct_answer': data.get('correct_answer'),
            'category': data.get('category', 'رومانسي')
        }
        
        questions.append(new_question)
        
        if save_questions(questions):
            return jsonify({'success': True, 'question': new_question}), 201
        else:
            return jsonify({
                'success': False, 
                'error': 'فشل حفظ السؤال'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'خطأ سيرفر: {str(e)}'
        }), 500


@app.route('/api/admin/update-question/<int:q_id>', methods=['POST', 'PUT'])
@require_admin
def update_question(q_id):
    """
    نقطة API لتحديث سؤال موجود
    Update Existing Question Endpoint
    
    Parameters:
        q_id (int): معرف السؤال
    
    JSON Request: (نفس صيغة إضافة سؤال)
    
    Returns:
        JSON: {
            "success": bool,
            "question": dict or error message
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'بيانات غير صحيحة'}), 400
        
        questions = load_questions()
        question = find_question_by_id(questions, q_id)
        
        if not question:
            return jsonify({
                'success': False, 
                'error': 'السؤال غير موجود'
            }), 404
        
        # تحديث بيانات السؤال
        question['type'] = data.get('type', question.get('type', 'mcq'))
        question['question'] = data.get('question', question['question'])
        question['options'] = data.get('options', question['options'])
        question['correct_answer'] = data.get(
            'correct_answer', 
            question.get('correct_answer')
        )
        question['category'] = data.get(
            'category', 
            question.get('category', 'رومانسي')
        )
        
        if save_questions(questions):
            return jsonify({'success': True, 'question': question})
        else:
            return jsonify({
                'success': False, 
                'error': 'فشل حفظ التحديثات'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'خطأ سيرفر: {str(e)}'
        }), 500


@app.route('/api/admin/delete-question/<int:q_id>', methods=['DELETE'])
@require_admin
def delete_question(q_id):
    """
    نقطة API لحذف سؤال
    Delete Question Endpoint
    
    Parameters:
        q_id (int): معرف السؤال
    
    Returns:
        JSON: {"success": bool}
    """
    try:
        questions = load_questions()
        initial_count = len(questions)
        questions = [q for q in questions if q.get('id') != q_id]
        
        if len(questions) == initial_count:
            return jsonify({
                'success': False, 
                'error': 'السؤال غير موجود'
            }), 404
        
        if save_questions(questions):
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False, 
                'error': 'فشل حذف السؤال'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'خطأ سيرفر: {str(e)}'
        }), 500


@app.route('/api/questions')
def get_questions():
    """
    نقطة API للحصول على جميع الأسئلة
    Get All Questions Endpoint
    
    Returns:
        JSON: قائمة جميع الأسئلة
    """
    questions = load_questions()
    return jsonify(questions)


# ==================== معالجة الأخطاء ====================

@app.errorhandler(404)
def not_found(error):
    """معالجة خطأ 404 - الصفحة غير موجودة"""
    return jsonify({'error': 'الصفحة غير موجودة'}), 404


@app.errorhandler(500)
def server_error(error):
    """معالجة خطأ 500 - خطأ في الخادم"""
    return jsonify({'error': 'حدث خطأ في الخادم'}), 500


@app.errorhandler(403)
def forbidden(error):
    """معالجة خطأ 403 - الوصول مرفوض"""
    return jsonify({'error': 'الوصول مرفوض'}), 403


# ==================== نقطة الدخول ====================

if __name__ == '__main__':
    # إعدادات التطوير
    # Production: debug=False, use production server (gunicorn)
    app.run(
        debug=True,
        port=5000,
        host='localhost',
        use_reloader=True
    )
