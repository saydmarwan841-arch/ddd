"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تطبيق اختبار الحب الرومانسي
Romantic Love Quiz Web Application
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version: 3.0 - Production Ready with Supabase PostgreSQL
Language: Python 3.7+
Framework: Flask 2.3.3
Database: Supabase (PostgreSQL)
Author: Love Quiz Team
Date: 2024
Description: تطبيق ويب تفاعلي يختبر مشاعر الحب الرومانسية
            مع دعم أنواع أسئلة متعددة (MCQ، True/False)
            متوافق 100% مع Vercel
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ==================== المكتبات والاستيراد ====================
from flask import (
    Flask, render_template, request, jsonify, 
    redirect, url_for, session
)
import os
from functools import wraps
import secrets
import json
from datetime import datetime

# Database imports
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


# ==================== تهيئة التطبيق ====================
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


# ==================== الإعدادات والثوابت ====================
class Config:
    """إعدادات التطبيق - يستخدم متغيرات البيئة"""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '0000')
    MAX_QUESTIONS = 100
    
    # التحقق من وجود DATABASE_URL
    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL environment variable is not set. "
                        "Please add it to your Vercel environment variables.")


# ==================== اتصال قاعدة البيانات ====================
class Database:
    """فئة للتعامل مع قاعدة البيانات"""
    
    _connection_pool = None
    
    @staticmethod
    def get_pool():
        """الحصول على connection pool"""
        if Database._connection_pool is None:
            try:
                Database._connection_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 20,
                    Config.DATABASE_URL
                )
                print("✅ Database connection pool created successfully")
            except psycopg2.Error as e:
                print(f"❌ Database connection error: {e}")
                raise
        return Database._connection_pool
    
    @staticmethod
    def get_connection():
        """الحصول على اتصال من pool"""
        try:
            pool = Database.get_pool()
            return pool.getconn()
        except psycopg2.Error as e:
            print(f"❌ Error getting connection: {e}")
            raise
    
    @staticmethod
    def return_connection(conn):
        """إرجاع الاتصال إلى pool"""
        if conn:
            Database.get_pool().putconn(conn)
    
    @staticmethod
    def execute_query(query, params=None, fetch=False):
        """تنفيذ استعلام مع معالجة الأخطاء"""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                
                if fetch:
                    result = cur.fetchall()
                    conn.commit()
                    return result
                else:
                    conn.commit()
                    return True
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Database error: {e}")
            raise
        finally:
            if conn:
                Database.return_connection(conn)
    
    @staticmethod
    def execute_query_one(query, params=None):
        """تنفيذ استعلام وإرجاع صف واحد فقط"""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                result = cur.fetchone()
                conn.commit()
                return result
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Database error: {e}")
            raise
        finally:
            if conn:
                Database.return_connection(conn)
    
    @staticmethod
    def init_db():
        """إنشء جداول قاعدة البيانات إذا لم تكن موجودة"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            type VARCHAR(10) NOT NULL,
            question TEXT NOT NULL,
            options JSONB NOT NULL,
            correct_answer TEXT NOT NULL,
            category VARCHAR(50) DEFAULT 'رومانسي',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_questions_id ON questions(id);
        """
        try:
            Database.execute_query(create_table_sql)
            print("✅ Database tables initialized successfully")
        except Exception as e:
            print(f"⚠️ Database init warning: {e}")


# ==================== دوال المساعدة ====================

def load_questions():
    """
    تحميل جميع الأسئلة من قاعدة البيانات
    
    Returns:
        list: قائمة الأسئلة
    """
    try:
        query = """
        SELECT id, type, question, options, correct_answer, category, 
               created_at, updated_at
        FROM questions
        ORDER BY id ASC
        """
        results = Database.execute_query(query, fetch=True)
        
        # تحويل النتائج إلى قاموس يسهل التعامل معه
        questions = []
        for row in results:
            question = {
                'id': row['id'],
                'type': row['type'],
                'question': row['question'],
                'options': row['options'] if isinstance(row['options'], list) else json.loads(row['options']),
                'correct_answer': row['correct_answer'],
                'category': row['category']
            }
            questions.append(question)
        
        return questions
    except Exception as e:
        print(f"❌ Error loading questions: {e}")
        return []


def find_question_by_id(q_id):
    """
    البحث عن سؤال بواسطة المعرف من قاعدة البيانات
    
    Args:
        q_id (int): معرف السؤال
    
    Returns:
        dict or None: السؤال المطلوب أو None
    """
    try:
        query = """
        SELECT id, type, question, options, correct_answer, category
        FROM questions
        WHERE id = %s
        """
        result = Database.execute_query_one(query, (q_id,))
        
        if result:
            return {
                'id': result['id'],
                'type': result['type'],
                'question': result['question'],
                'options': result['options'] if isinstance(result['options'], list) else json.loads(result['options']),
                'correct_answer': result['correct_answer'],
                'category': result['category']
            }
        return None
    except Exception as e:
        print(f"❌ Error finding question: {e}")
        return None


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
    
    if not isinstance(data.get('options'), list) or len(data.get('options', [])) == 0:
        return False, "الخيارات يجب أن تكون قائمة غير فارغة"
    
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
    try:
        questions = load_questions()
        return render_template(
            'index_ar.html', 
            questions=questions
        )
    except Exception as e:
        print(f"❌ Error in index route: {e}")
        return jsonify({'error': 'خطأ في تحميل الصفحة'}), 500


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
            question = find_question_by_id(int(q_id))
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
            return jsonify({'success': False, 'error': 'بيانات غير صحيحة. لم يتم استقبال JSON'}), 400
        
        # التحقق من صحة البيانات
        is_valid, error_msg = validate_question_data(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # إدراج السؤال الجديد في قاعدة البيانات
        insert_query = """
        INSERT INTO questions (type, question, options, correct_answer, category)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, type, question, options, correct_answer, category
        """
        
        params = (
            data.get('type', 'mcq'),
            data.get('question'),
            json.dumps(data.get('options'), ensure_ascii=False),
            data.get('correct_answer'),
            data.get('category', 'رومانسي')
        )
        
        result = Database.execute_query_one(insert_query, params)
        
        if result:
            new_question = {
                'id': result['id'],
                'type': result['type'],
                'question': result['question'],
                'options': result['options'] if isinstance(result['options'], list) else json.loads(result['options']),
                'correct_answer': result['correct_answer'],
                'category': result['category']
            }
            return jsonify({'success': True, 'question': new_question}), 201
        else:
            return jsonify({'success': False, 'error': 'فشل إنشاء السؤال'}), 500
    
    except json.JSONDecodeError as e:
        error_msg = f'خطأ في معالجة JSON: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 400
    except psycopg2.Error as e:
        error_msg = f'خطأ في قاعدة البيانات: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500
    except Exception as e:
        error_msg = f'خطأ سيرفر غير متوقع: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500


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
        
        # التحقق من وجود السؤال
        question = find_question_by_id(q_id)
        if not question:
            return jsonify({'success': False, 'error': f'السؤال برقم {q_id} غير موجود'}), 404
        
        # تحديث السؤال في قاعدة البيانات
        update_query = """
        UPDATE questions
        SET type = %s,
            question = %s,
            options = %s,
            correct_answer = %s,
            category = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, type, question, options, correct_answer, category
        """
        
        params = (
            data.get('type', question.get('type', 'mcq')),
            data.get('question', question.get('question')),
            json.dumps(data.get('options', question.get('options')), ensure_ascii=False),
            data.get('correct_answer', question.get('correct_answer')),
            data.get('category', question.get('category', 'رومانسي')),
            q_id
        )
        
        result = Database.execute_query_one(update_query, params)
        
        if result:
            updated_question = {
                'id': result['id'],
                'type': result['type'],
                'question': result['question'],
                'options': result['options'] if isinstance(result['options'], list) else json.loads(result['options']),
                'correct_answer': result['correct_answer'],
                'category': result['category']
            }
            return jsonify({'success': True, 'question': updated_question})
        else:
            return jsonify({'success': False, 'error': 'فشل تحديث السؤال'}), 500
    
    except json.JSONDecodeError as e:
        error_msg = f'خطأ في معالجة JSON: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 400
    except psycopg2.Error as e:
        error_msg = f'خطأ في قاعدة البيانات: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500
    except Exception as e:
        error_msg = f'خطأ سيرفر غير متوقع: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500


@app.route('/api/admin/delete-question/<int:q_id>', methods=['DELETE'])
@require_admin
def delete_question(q_id):
    """
    نقطة API لحذف سؤال
    Delete Question Endpoint
    
    Parameters:
        q_id (int): معرف السؤال
    
    Returns:
        JSON: {"success": bool, "error": error message (if any)}
    """
    try:
        # حذف السؤال من قاعدة البيانات
        delete_query = "DELETE FROM questions WHERE id = %s"
        
        # أولاً، تحقق من وجود السؤال
        question = find_question_by_id(q_id)
        if not question:
            return jsonify({'success': False, 'error': f'السؤال برقم {q_id} غير موجود'}), 404
        
        # ثم احذفه
        Database.execute_query(delete_query, (q_id,))
        
        return jsonify({'success': True})
    
    except psycopg2.Error as e:
        error_msg = f'خطأ في قاعدة البيانات: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500
    except Exception as e:
        error_msg = f'خطأ سيرفر غير متوقع: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500


@app.route('/api/questions')
def get_questions():
    """
    نقطة API للحصول على جميع الأسئلة
    Get All Questions Endpoint
    
    Returns:
        JSON: قائمة جميع الأسئلة
    """
    try:
        questions = load_questions()
        return jsonify(questions)
    except Exception as e:
        print(f"❌ Error getting questions: {e}")
        return jsonify({'error': 'خطأ في تحميل الأسئلة'}), 500


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


# ==================== تهيئة قاعدة البيانات ====================

def init_database():
    """تهيئة قاعدة البيانات عند بدء التطبيق"""
    try:
        Database.init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")


# ==================== نقطة الدخول ====================

if __name__ == '__main__':
    # تهيئة قاعدة البيانات
    init_database()
    
    # إعدادات التطوير
    # Production: debug=False, use production server (gunicorn)
    app.run(
        debug=os.environ.get('FLASK_ENV') == 'development',
        port=int(os.environ.get('PORT', 5000)),
        host='0.0.0.0',
        use_reloader=False
    )
