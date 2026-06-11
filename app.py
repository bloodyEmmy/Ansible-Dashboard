from flask import Flask, jsonify, request, render_template
import database

app = Flask(__name__)

# При старте приложения проверяем, создана ли база
database.init_db()

@app.route('/')
def index():
    # Эта функция просто отдает HTML страницу при заходе в браузер
    return render_template('index.html')

@app.route('/api/history', methods=['GET'])
def api_history():
    # Получаем параметры из URL (например: ?user=admin&start_date=2026-05-01)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user = request.args.get('user')
    
    try:
        # Идем в базу за данными
        runs = database.get_runs(start_date, end_date, user)
        # Flask сам превратит список словарей в правильный JSON
        return jsonify({
            "status": "success",
            "count": len(runs),
            "data": runs
        }), 200
        
    except Exception as e:
        # Если что-то пошло не так (например, кривой SQL), вернем ошибку
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Запуск сервера в режиме отладки
    app.run(debug=True, host='0.0.0.0', port=5000)