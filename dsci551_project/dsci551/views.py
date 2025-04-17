from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
import json
import pymysql
import requests
import re
from .models import Customer, Order, UserQueryHistory, Product  # 导入新创建的 UserQueryHistory 模型
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import UserQueryHistory
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient

@login_required

def connect_database(request):
    if request.method == 'POST':
        host = request.POST.get('host')
        username = request.POST.get('username')
        password = request.POST.get('password')  # 允许密码为空
        dbname = request.POST.get('dbname')

        try:
            # 尝试连接到用户提供的数据库
            connection = pymysql.connect(
                host=host,
                user=username,
                password=password,
                database=dbname
            )

            # 将数据库连接信息保存到 session 中
            request.session['db_connection'] = {
                'host': host,
                'user': username,
                'password': password,
                'database': dbname
            }

            connection.close()  # 连接成功后立即关闭连接
            return redirect('natural_language_query')  # 连接成功，跳转到查询页面

        except pymysql.MySQLError as e:
            return render(request, 'query_form.html', {'error': f"数据库连接失败: {str(e)}"})

    return render(request, 'query_form.html')


@login_required
def nosql_query(request):
    if request.method == 'POST':
        user_datalink = request.POST.get("datalink")
        user_input = request.POST.get('firebasequery')
        deepseek_api_key = "sk-c6d9cd93a21b418da5adc6ef7fcb2479"
        deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
        # 更新系统提示语
        FIREBASE_SYSTEM_INSTRUCTION = (
            f"You are my noSQL database assistant. Here are the database links:\n{user_datalink}\n"
            "I will give you natural language commands related to exploring the schema, querying, inserting, updating, and deleting. "
             "To splice .json paths, use POST/GET/PATCH/DELETE, etc. for reading and writing."
            "Never use any firebase_admin or other libraries, and never use Service Account."
            "Do not output any extra textual explanations or comments, only return executable Python code."
            "Only return firebase queries that can be directly executed in python. "
            "If you understand, output only 'ok, I'm ready for your query'."
        )

        print(user_datalink)

        messages = [{"role": "system", "content": FIREBASE_SYSTEM_INSTRUCTION}]
        messages.append({"role": "user", "content": user_input})

        # 调用 DeepSeek API
        reasoning, content = call_deepseek(messages, deepseek_api_key, deepseek_api_url)
        if not content:
            return JsonResponse({"error": "Error processing your request."}, status=400)

        # 打印 LLM 返回的 SQL 语句
        print(f"LLM 返回的 SQL 查询语句：\n{content}")

        # 清洗并执行返回的代码
        safe_locals = {}
        safe_code = clean_code_block(content)
        # 打印清洗后的 SQL 语句（如果需要查看清洗后的 SQL） 
        print(f"清洗后的 SQL 查询语句：\n{safe_code}")
        try:
            # 执行 MySQL 代码
            exec(safe_code, {}, safe_locals)
            # 存储用户查询和 LLM 返回的结果
            query_history = UserQueryHistory(user=request.user, query_text=user_input, llm_response=str(safe_locals['response'].json()))
            query_history.save()

            # 返回查询结果
            return JsonResponse({"result": str(safe_locals['response'].json())})
        

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return render(request, 'nosql_query.html') #谢姐靠你了

@login_required
def nosql_mongo_query(request):
    if request.method == 'POST':
        user_datalink = request.POST.get("datalink")
        user_input = request.POST.get('mongoquery')
        deepseek_api_key = "sk-c6d9cd93a21b418da5adc6ef7fcb2479"
        deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
        # 更新系统提示语
        FIREBASE_SYSTEM_INSTRUCTION = (
            f"You are my noSQL database assistant. Here are the database links:\n{user_datalink}\n"
            "using pymongo to connect to the mongodb server"
            "I will give you natural language commands related to exploring the schema, querying, inserting, updating, and deleting. "
            "find (with projection), aggregate (with $match, $group,$sort, $limit, $skip, $project). Note that $match can be before and after $group. You should also allow queries that involve joining of two collections (using $lookup)."
            "Do not output any extra textual explanations or comments, only return executable Python code. I don't need your explanation, just give me pure pure code"
            "Only return pymongo code that can be directly executed in python. "
            "store results in a variable named result"
            "If you understand, output only 'ok, I'm ready for your query'."
        )

        print(user_datalink)
        print(user_input)
        messages = [{"role": "system", "content": FIREBASE_SYSTEM_INSTRUCTION}]
        messages.append({"role": "user", "content": user_input})

        # 调用 DeepSeek API
        reasoning, content = call_deepseek(messages, deepseek_api_key, deepseek_api_url)
        if not content:
            return JsonResponse({"error": "Error processing your request."}, status=400)

        # 打印 LLM 返回的 SQL 语句
        print(f"LLM 返回的 SQL 查询语句：\n{content}")
        # 清洗并执行返回的代码
        safe_locals = {}
        safe_code = clean_code_block(content)
        # 打印清洗后的 SQL 语句（如果需要查看清洗后的 SQL） 
        print(f"清洗后的 SQL 查询语句：\n{safe_code}")
        try:
            # 执行 MySQL 代码
            #client = MongoClient("mongodb://localhost:27017/")
            exec(safe_code, {}, safe_locals)
            # 存储用户查询和 LLM 返回的结果
            query_history = UserQueryHistory(user=request.user, query_text=user_input, llm_response=str(safe_locals['result']))
            query_history.save()

            # 返回查询结果
            return JsonResponse({"result": str(safe_locals['result'])})
        

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return render(request, 'nosql_query.html')

@login_required
def select_database(request):
    return render(request, 'select_database.html')  # 渲染数据库选择页面


def get_db_schema():
    schema = []
    for model in [Customer, Order, Product]:  # 列出你的所有模型
        table_name = model._meta.db_table
        columns = [field.name for field in model._meta.fields]
        schema.append(f"Table: {table_name}\nColumns:\n" + "\n".join([f"  {col}: {get_column_type(model, col)}" for col in columns]))
    return "\n\n".join(schema)

def get_column_type(model, column_name):
    field = model._meta.get_field(column_name)
    return str(field.get_internal_type())  # 获取字段类型


# 仅限登录用户查看自己的查询历史
@login_required
def user_query_history(request):
    # 获取当前登录用户的查询历史
    query_history = UserQueryHistory.objects.filter(user=request.user).order_by('-timestamp')

    return render(request, 'query_history.html', {'query_history': query_history})


# 主页选择页面
def home(request):
    return render(request, 'home.html')

# 用户注册视图
def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')  # 确认密码字段
        
        if password == password2:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            return redirect('login')  # 注册成功后，跳转到登录页面
        else:
            return render(request, 'register.html', {'error': '两次输入的密码不一致。'})
    
    return render(request, 'register.html')



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 登录成功后，重定向到选择数据库页面
            return redirect('select_database')  
        else:
            return render(request, 'login.html', {'error': '用户名或密码错误！'})
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


# 调用 DeepSeek API
def call_deepseek(messages, deepseek_api_key: str, deepseek_api_url: str, model="deepseek-chat"):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {deepseek_api_key}"
    }
    payload = {
        "model": model,
        "messages": messages
    }
    
    resp = requests.post(deepseek_api_url, headers=headers, data=json.dumps(payload))
    if resp.status_code != 200:
        print("[DeepSeek] Call Error:", resp.text)
        return None, None
    
    data = resp.json()
    try:
        message_dict = data["choices"][0]["message"]
        reasoning = message_dict.get("reasoning_content")
        content = message_dict.get("content")
        return reasoning, content
    except (KeyError, IndexError):
        print("[DeepSeek] return format不符合预期:", data)
        return None, None

# 清洗代码块
def clean_code_block(code_text: str) -> str:
    # 删除代码块标记
    code_text = code_text.replace("ok", "").strip()  # 去除 "ok" 以及多余空格
    code_text = re.sub(r"```python\s*", "", code_text)
    code_text = re.sub(r"```Python\s*", "", code_text)
    code_text = re.sub(r"```", "", code_text)
    code_text = re.sub(r"^\s*sql\s*", "", code_text)
    # 删除可能出现的 'sql' 字符串
    code_text = re.sub(r"sql", "", code_text)

    code_text = re.sub(r"```sql", "", code_text)

    code_text = code_text.strip()  # 去除两端的空格

    return code_text


def get_db_schema(db_connection):
    schema = []
    try:
        # 获取数据库连接
        connection = pymysql.connect(**db_connection)
        cursor = connection.cursor()

        # 获取所有表的名称
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            # 获取每个表的列信息
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()

            schema.append(f"Table: {table_name}\nColumns:")
            for col in columns:
                col_name = col[0]
                col_type = col[1]
                schema.append(f"  {col_name}: {col_type}")

        connection.close()
    except pymysql.MySQLError as e:
        print(f"Error fetching schema: {str(e)}")
        return None

    return "\n\n".join(schema)


# 仅登录用户可以进行查询
@login_required
def natural_language_query(request):
    if request.method == 'POST':
        user_input = request.POST.get('query')
        deepseek_api_key = "sk-c6d9cd93a21b418da5adc6ef7fcb2479"
        deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"

        db_connection = request.session.get('db_connection')  # 从 session 中获取数据库连接信息
        
        if db_connection is None:
            return JsonResponse({"error": "未连接到数据库，请先提供数据库连接信息。"})

        # 动态获取数据库 schema
        db_schema = get_db_schema(db_connection)
        
        if db_schema is None:
            return JsonResponse({"error": "无法获取数据库 schema。"})

        # LLM 提示词
        MYSQL_SYSTEM_INSTRUCTION = (
            f"You are my MySQL database assistant. Here is the database schema:\n{db_schema}\n"
            "I will give you natural language commands related to exploring the schema, querying, inserting, updating, and deleting. "
            "You must ONLY return valid SQL queries for MySQL. "
            "Do not include Python code such as import statements, and do not return any Python code for execution. "
            "Only return SQL queries that can be directly executed in MySQL. "
            "If you understand, output only 'ok'."
        )

        print(db_schema)

        messages = [{"role": "system", "content": MYSQL_SYSTEM_INSTRUCTION}]
        messages.append({"role": "user", "content": user_input})

        # 调用 DeepSeek API
        reasoning, content = call_deepseek(messages, deepseek_api_key, deepseek_api_url)
        if not content:
            return JsonResponse({"error": "Error processing your request."}, status=400)

        # 打印 LLM 返回的 SQL 语句
        print(f"LLM 返回的 SQL 查询语句：\n{content}")

        # 清洗并执行返回的代码
        safe_code = clean_code_block(content)
        
        # 打印清洗后的 SQL 语句（如果需要查看清洗后的 SQL） 
        print(f"清洗后的 SQL 查询语句：\n{safe_code}")

        try:
            # 执行 MySQL 代码
            print("Connecting to the database...")
            connection = pymysql.connect(**db_connection)
            print("Connection successful!")
            cursor = connection.cursor()
            cursor.execute(safe_code)
            result = cursor.fetchall()
            if not result:
                print("No results found.")
            print(f"Query result: {result}")
            connection.close()

            # 存储用户查询和 LLM 返回的结果
            query_history = UserQueryHistory(user=request.user, query_text=user_input, llm_response=str(result))
            query_history.save()

            # 返回查询结果
            return JsonResponse({"result": result})
        
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return JsonResponse({"error": "Database error occurred."}, status=500)

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, 'query_form.html')

