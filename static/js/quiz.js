/**
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * تطبيق اختبار الحب - وحدة الاختبار
 * Romantic Love Quiz - Quiz Module
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 */

'use strict';

// ==================== تكوين عام ====================

const QuizConfig = {
    API_ENDPOINTS: {
        SUBMIT: '/api/submit',
        QUESTIONS: '/api/questions'
    },
    ELEMENTS: {
        QUIZ_CONTAINER: '#quizContainer',
        QUESTION_CARD: '#questionCard',
        OPTIONS_CONTAINER: '#optionsContainer',
        PROGRESS_BAR: '#progressBar',
        CURRENT_QUESTION: '#currentQuestion',
        TOTAL_QUESTIONS: '#totalQuestions',
        RESULTS_CONTAINER: '#results',
        QUIZ_FORM: '#quizForm'
    },
    MESSAGES: {
        LOVE_MESSAGES: [
            '💕 حبك يملأ قلبي بكل الفرح',
            '💖 أنت أجمل شيء في حياتي',
            '🌹 حبك لا يقدر بثمن',
            '💝 معك أشعر بالسعادة الحقيقية',
            '✨ أنت نجمي اللامع في الليل'
        ]
    }
};

// ==================== متغيرات الحالة ====================

let quizState = {
    currentQuestionIndex: 0,
    questions: [],
    answers: {},
    score: 0,
    isSubmitting: false
};

// ==================== دوال المساعدة ====================

/**
 * عرض رسالة خطأ في واجهة المستخدم
 * Display error message to user
 * 
 * @param {string} message - نص الرسالة
 */
function showError(message) {
    Swal.fire({
        icon: 'error',
        title: 'خطأ',
        text: message,
        confirmButtonText: 'حسناً',
        confirmButtonColor: '#ef4444'
    });
    console.error('Error:', message);
}

/**
 * عرض رسالة نجاح
 * Display success message
 * 
 * @param {string} message - نص الرسالة
 * @param {function} callback - دالة الاستدعاء بعد الإغلاق
 */
function showSuccess(message, callback) {
    Swal.fire({
        icon: 'success',
        title: 'نجح',
        text: message,
        confirmButtonText: 'حسناً',
        confirmButtonColor: '#10b981'
    }).then(() => {
        if (callback) callback();
    });
}

/**
 * تحديث شريط التقدم
 * Update progress bar
 * 
 * @param {number} current - رقم السؤال الحالي
 * @param {number} total - إجمالي الأسئلة
 */
function updateProgressBar(current, total) {
    const percentage = (current / total) * 100;
    const progressBar = document.querySelector(QuizConfig.ELEMENTS.PROGRESS_BAR);

    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
    }

    // تحديث أرقام الأسئلة
    const currentEl = document.querySelector(QuizConfig.ELEMENTS.CURRENT_QUESTION);
    const totalEl = document.querySelector(QuizConfig.ELEMENTS.TOTAL_QUESTIONS);

    if (currentEl) currentEl.textContent = current;
    if (totalEl) totalEl.textContent = total;
}

/**
 * الحصول على رسالة حب عشوائية
 * Get random love message
 * 
 * @returns {string} رسالة عشوائية
 */
function getRandomLoveMessage() {
    const messages = QuizConfig.MESSAGES.LOVE_MESSAGES;
    return messages[Math.floor(Math.random() * messages.length)];
}

/**
 * إظهار تأثير الألعاب الناري
 * Show confetti animation
 */
function showConfetti() {
    try {
        if (typeof confetti === 'function') {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }
    } catch (error) {
        console.warn('تنبيه: لا يمكن تشغيل تأثير الألعاب الناري');
    }
}

// ==================== دوال الأسئلة ====================

/**
 * تحميل الأسئلة من السيرفر
 * Load questions from server
 * 
 * @returns {Promise<Array>} قائمة الأسئلة
 */
async function fetchQuestions() {
    try {
        const response = await fetch(QuizConfig.API_ENDPOINTS.QUESTIONS);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const questions = await response.json();

        if (!Array.isArray(questions) || questions.length === 0) {
            showError('لا توجد أسئلة متاحة حالياً');
            return [];
        }

        return questions;
    } catch (error) {
        showError(`فشل تحميل الأسئلة: ${error.message}`);
        return [];
    }
}

/**
 * عرض سؤال معين
 * Display a specific question
 * 
 * @param {number} index - رقم السؤال (0-based)
 */
function displayQuestion(index) {
    if (index >= quizState.questions.length) {
        submitQuiz();
        return;
    }

    const question = quizState.questions[index];
    const questionCard = document.querySelector(QuizConfig.ELEMENTS.QUESTION_CARD);
    const optionsContainer = document.querySelector(QuizConfig.ELEMENTS.OPTIONS_CONTAINER);

    if (!questionCard || !optionsContainer) {
        console.error('عناصر الواجهة غير موجودة');
        return;
    }

    // تحديث نص السؤال
    questionCard.innerHTML = `
        <div class="p-6 text-right">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">${escapeHtml(question.question)}</h2>
            <p class="text-sm text-gray-500">الفئة: <span class="font-semibold">${escapeHtml(question.category)}</span></p>
        </div>
    `;

    // عرض الخيارات بناءً على نوع السؤال
    displayOptions(question, optionsContainer);

    // تحديث شريط التقدم - البيانات الصحيحة
    updateProgressBar(index, quizState.questions.length);
}

/**
 * عرض خيارات السؤال
 * Display question options
 * 
 * @param {Object} question - كائن السؤال
 * @param {HTMLElement} container - حاوية الخيارات
 */
function displayOptions(question, container) {
    container.innerHTML = '';

    const questionType = question.type || 'mcq';

    if (questionType === 'tf') {
        // عرض أسئلة صح/خطأ
        displayTrueFalseOptions(question, container);
    } else {
        // عرض أسئلة اختيار متعدد
        displayMultipleChoiceOptions(question, container);
    }
}

/**
 * عرض خيارات اختيار متعدد
 * Display multiple choice options
 * 
 * @param {Object} question - كائن السؤال
 * @param {HTMLElement} container - حاوية الخيارات
 */
function displayMultipleChoiceOptions(question, container) {
    const options = question.options || [];

    options.forEach((option, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `
            w-full p-4 mb-3 text-right rounded-lg
            bg-gray-100 hover:bg-blue-200 transition-colors duration-200
            border-2 border-gray-200 hover:border-blue-400
            font-semibold text-gray-700 hover:text-blue-600
            focus:outline-none focus:ring-2 focus:ring-blue-400
        `;
        button.textContent = escapeHtml(option);

        button.addEventListener('click', () => selectAnswer(question.id, index.toString(), button));

        // تحديد الخيار المختار سابقاً
        if (quizState.answers[question.id] === index.toString()) {
            button.classList.add('bg-blue-400', 'text-white', 'border-blue-500');
            button.classList.remove('bg-gray-100', 'text-gray-700');
        }

        container.appendChild(button);
    });
}

/**
 * عرض خيارات صح/خطأ
 * Display true/false options
 * 
 * @param {Object} question - كائن السؤال
 * @param {HTMLElement} container - حاوية الخيارات
 */
function displayTrueFalseOptions(question, container) {
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'grid grid-cols-2 gap-4';

    const options = [
        { text: '✅ صح', value: '0', color: 'green' },
        { text: '❌ خطأ', value: '1', color: 'red' }
    ];

    options.forEach(option => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `
            p-6 rounded-lg font-bold text-lg transition-all duration-200
            border-2 focus:outline-none focus:ring-2
            hover:scale-105 active:scale-95
        `;

        // تطبيق الألوان الديناميكية
        if (option.color === 'green') {
            button.className += ' bg-green-100 hover:bg-green-200 text-green-700 border-green-300 focus:ring-green-400';
        } else {
            button.className += ' bg-red-100 hover:bg-red-200 text-red-700 border-red-300 focus:ring-red-400';
        }

        button.textContent = option.text;

        // اختيار الإجابة
        button.addEventListener('click', () => selectAnswer(question.id, option.value, button));

        // تحديد الخيار المختار سابقاً
        if (quizState.answers[question.id] === option.value) {
            button.classList.add('ring-2');
            if (option.color === 'green') {
                button.classList.add('ring-green-400');
            } else {
                button.classList.add('ring-red-400');
            }
        }

        buttonsContainer.appendChild(button);
    });

    container.appendChild(buttonsContainer);
}

/**
 * تسجيل إجابة المستخدم
 * Record user answer
 * 
 * @param {number} questionId - معرف السؤال
 * @param {string} answer - الإجابة المختارة
 * @param {HTMLElement} buttonElement - عنصر الزر المضغوط
 */
function selectAnswer(questionId, answer, buttonElement) {
    // تسجيل الإجابة
    quizState.answers[questionId] = answer;

    // تحديث نمط الزر المختار
    const allButtons = buttonElement.parentElement.querySelectorAll('button');
    allButtons.forEach(btn => {
        btn.classList.remove(
            'bg-blue-400', 'text-white', 'border-blue-500',
            'ring-2', 'ring-green-400', 'ring-red-400'
        );
        btn.classList.add('bg-gray-100', 'text-gray-700');
    });

    // تطبيق نمط التحديد
    buttonElement.classList.remove('bg-gray-100', 'text-gray-700');
    if (buttonElement.classList.contains('text-green-700')) {
        buttonElement.classList.add('ring-2', 'ring-green-400');
    } else if (buttonElement.classList.contains('text-red-700')) {
        buttonElement.classList.add('ring-2', 'ring-red-400');
    } else {
        buttonElement.classList.add('bg-blue-400', 'text-white', 'border-blue-500');
    }

    // تحريك إلى السؤال التالي بعد تأخير صغير
    setTimeout(() => {
        nextQuestion();
    }, 300);
}

/**
 * الانتقال إلى السؤال التالي
 * Move to next question
 */
function nextQuestion() {
    quizState.currentQuestionIndex++;

    if (quizState.currentQuestionIndex >= quizState.questions.length) {
        submitQuiz();
    } else {
        displayQuestion(quizState.currentQuestionIndex);
    }
}

/**
 * الانتقال إلى السؤال السابق
 * Move to previous question
 */
function previousQuestion() {
    if (quizState.currentQuestionIndex > 0) {
        quizState.currentQuestionIndex--;
        displayQuestion(quizState.currentQuestionIndex);
    }
}

// ==================== إرسال الاختبار ====================

/**
 * إرسال الاختبار والحصول على النتائج
 * Submit quiz and get results
 * 
 * @returns {Promise<void>}
 */
async function submitQuiz() {
    if (quizState.isSubmitting) return;

    quizState.isSubmitting = true;

    try {
        const response = await fetch(QuizConfig.API_ENDPOINTS.SUBMIT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                answers: quizState.answers
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        displayResults(result);
        showConfetti();

    } catch (error) {
        showError(`فشل إرسال الاختبار: ${error.message}`);
    } finally {
        quizState.isSubmitting = false;
    }
}

/**
 * عرض النتائج النهائية
 * Display final results
 * 
 * @param {Object} result - النتيجة من السيرفر
 */
function displayResults(result) {
    const quizContainer = document.querySelector(QuizConfig.ELEMENTS.QUIZ_CONTAINER);
    let resultsContainer = document.querySelector(QuizConfig.ELEMENTS.RESULTS_CONTAINER);

    if (!resultsContainer) {
        console.error('عنصر النتائج غير موجود - جاري إنشاؤه');
        // إذا لم يكن موجوداً، نحاول إنشاؤه
        resultsContainer = document.createElement('div');
        resultsContainer.id = 'results';
        resultsContainer.className = 'quiz-card';
        if (quizContainer && quizContainer.parentElement) {
            quizContainer.parentElement.appendChild(resultsContainer);
        } else {
            document.body.appendChild(resultsContainer);
        }
    }

    // حساب التقييم
    const percentage = result.percentage || 0;
    let rating = '';
    let emoji = '';

    if (percentage === 100) {
        rating = '🌟 مثالي تماماً!';
        emoji = '😍';
    } else if (percentage >= 80) {
        rating = '💕 رائع جداً!';
        emoji = '😊';
    } else if (percentage >= 60) {
        rating = '💖 جيد جداً';
        emoji = '😌';
    } else if (percentage >= 40) {
        rating = '💕 محاولة جيدة';
        emoji = '🙂';
    } else {
        rating = '💔 حاول مرة أخرى';
        emoji = '😢';
    }

    // عرض النتائج
    resultsContainer.innerHTML = `
        <div class="text-center py-8">
            <div class="mb-6">
                <p class="text-6xl mb-4">${emoji}</p>
                <h2 class="text-4xl font-bold text-pink-600 mb-4">${rating}</h2>
            </div>
            
            <div class="bg-gradient-to-r from-pink-100 to-red-100 rounded-lg p-8 mb-6">
                <p class="text-gray-700 mb-2">نتيجتك</p>
                <div class="text-5xl font-bold text-pink-600 mb-2">
                    ${result.score} / ${result.total}
                </div>
                <p class="text-2xl font-semibold text-pink-500">${percentage.toFixed(1)}%</p>
            </div>
            
            <p class="text-lg text-gray-600 mb-8 italic">"${getRandomLoveMessage()}"</p>
            
            <button id="restartBtn" class="
                bg-pink-500 hover:bg-pink-600 text-white font-bold
                py-3 px-8 rounded-lg transition-colors duration-200
                focus:outline-none focus:ring-2 focus:ring-pink-400
            ">
                🔄 إعادة الاختبار
            </button>
        </div>
    `;

    // إخفاء نموذج الاختبار وعرض النتائج
    if (quizContainer) {
        quizContainer.style.display = 'none';
    }
    if (resultsContainer) {
        resultsContainer.style.display = 'block';
        resultsContainer.classList.add('show');
    }

    // إضافة معالج حدث إعادة الاختبار
    const restartBtn = document.getElementById('restartBtn');
    if (restartBtn) {
        restartBtn.addEventListener('click', restartQuiz);
    }
}

/**
 * إعادة تعيين الاختبار
 * Restart quiz
 */
function restartQuiz() {
    // إعادة تعيين الحالة مع الحفاظ على الأسئلة
    quizState = {
        currentQuestionIndex: 0,
        questions: quizState.questions,  // الحفاظ على قائمة الأسئلة
        answers: {},
        score: 0,
        isSubmitting: false
    };

    // إظهار نموذج الاختبار وإخفاء النتائج
    const quizContainer = document.querySelector(QuizConfig.ELEMENTS.QUIZ_CONTAINER);
    const resultsContainer = document.querySelector(QuizConfig.ELEMENTS.RESULTS_CONTAINER);

    if (quizContainer) {
        quizContainer.style.display = 'block';
    }
    if (resultsContainer) {
        resultsContainer.classList.remove('show');
    }

    // التأكد من أن الأسئلة موجودة قبل العرض
    if (quizState.questions && quizState.questions.length > 0) {
        displayQuestion(0);
    } else {
        showError('فشل تحميل الأسئلة');
    }
}

/**
 * حماية من تجاوز XSS
 * Escape HTML to prevent XSS
 * 
 * @param {string} text - النص المراد تنظيفه
 * @returns {string} النص المنظف
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };

    return text.replace(/[&<>"']/g, m => map[m]);
}

// ==================== تهيئة الاختبار ====================

/**
 * التحقق من صحة بيانات الأسئلة
 * Validate questions data structure
 * 
 * @param {Array} questions - قائمة الأسئلة للتحقق
 * @returns {boolean} هل البيانات صحيحة
 */
function validateQuestionsData(questions) {
    if (!Array.isArray(questions) || questions.length === 0) {
        console.error('الأسئلة يجب أن تكون مصفوفة غير فارغة');
        return false;
    }

    for (const q of questions) {
        // التحقق من الحقول المطلوبة
        if (!q.id || !q.question || !Array.isArray(q.options) || q.options.length === 0) {
            console.error('سؤال غير صحيح:', q);
            return false;
        }

        // التحقق من الإجابة الصحيحة
        if (q.correct_answer === undefined || q.correct_answer === null) {
            console.error('الإجابة الصحيحة مفقودة:', q.id);
            return false;
        }

        // التحقق من نوع السؤال
        if (q.type && !['mcq', 'tf'].includes(q.type)) {
            console.warn('نوع سؤال غير معروف:', q.type);
        }
    }

    return true;
}

/**
 * تهيئة الاختبار عند تحميل الصفحة
 * Initialize quiz on page load
 */
async function initializeQuiz() {
    try {
        console.log('بدء التهيئة...', window.preloadedQuestions);
        let questions = [];

        // محاولة استخدام الأسئلة المُحمّلة مسبقاً
        if (window.preloadedQuestions && Array.isArray(window.preloadedQuestions)) {
            // التحقق من صحة البيانات
            if (validateQuestionsData(window.preloadedQuestions)) {
                questions = window.preloadedQuestions;
                console.log('تم استخدام الأسئلة المُحمّلة مسبقاً:', questions.length);
            } else {
                console.warn('البيانات المحملة مسبقاً غير صحيحة، جاري تحميل من API...');
                questions = await fetchQuestions();
            }
        } else {
            // تحميل الأسئلة من API إذا لم تكن محملة مسبقاً
            console.log('جاري تحميل الأسئلة من API...');
            questions = await fetchQuestions();
        }

        // التحقق النهائي من الأسئلة
        if (!questions || questions.length === 0) {
            showError('لا توجد أسئلة متاحة. يرجى التحقق من لوحة التحكم.');
            return;
        }

        // تحديث الحالة
        quizState.questions = questions;

        // تحديث إجمالي الأسئلة في الواجهة
        const totalEl = document.querySelector(QuizConfig.ELEMENTS.TOTAL_QUESTIONS);
        if (totalEl) totalEl.textContent = questions.length;

        // عرض السؤال الأول
        displayQuestion(0);

    } catch (error) {
        showError(`فشل تهيئة الاختبار: ${error.message}`);
        console.error('خطأ التهيئة:', error);
    }
}

// ==================== معالجات الأحداث ====================

document.addEventListener('DOMContentLoaded', () => {
    initializeQuiz();

    // إضافة معالجات الأزرار إن وجدت
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');

    if (nextBtn) {
        nextBtn.addEventListener('click', nextQuestion);
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', previousQuestion);
    }
});
