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
from django.contrib import messages
from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.command_cursor import CommandCursor
from bson.json_util import dumps
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
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
            return JsonResponse({'success': True})

        except pymysql.MySQLError as e:
            return JsonResponse({'error': f"数据库连接失败: {str(e)}"}, status=500)

    return JsonResponse({'error': '无效请求'}, status=400)


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
            "If you understand, output only 'ok. I'm ready.'"
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
        print(user_datalink)
        print(user_input)
        print()
        uri, db_name = str(user_datalink).split(',')
        def get_db_structure(uri, db_name, sample_size=100):

            client = MongoClient(uri)
            db = client[db_name]
            
            structure = {}

            for coll_name in db.list_collection_names():
                collection = db[coll_name]
                fields = set()
                
                # Sample documents to infer fields
                for doc in collection.find().limit(sample_size):
                    fields.update(doc.keys())

                structure[coll_name] = sorted(fields)
            
            return structure

    # Usage

        structure = get_db_structure(uri, db_name)
        print(structure)
        FIREBASE_SYSTEM_INSTRUCTION = (
            f"You are my noSQL database assistant. Here are the database links and the database they are using:\n{user_datalink}\n"
            f"Here is the structure of that databse: \n{structure}\n"
            "using pymongo to connect to the mongodb server"
            "I will give you natural language commands related to exploring the schema, querying, inserting, updating, and deleting. "
            "find (with projection), aggregate (with $match, $group,$sort, $limit, $skip, $project). Note that $match can be before and after $group. You should also allow queries that involve joining of two collections (using $lookup)."
            "Do not output any extra textual explanations or comments, only return executable Python code. I don't need your explanation, just give me pure pure code"
            "I want you to answer my question with real field names that exists in this database, don't assume the id named '_id'."
            "Only return pymongo code that can be directly executed in python. "
            "Make sure each field name and collection name really exist, check the existence of filed name you will use before generating the code"
            "Be careful with name of collection, scan through the database to get a complete structure of the database and collection"
            "store results in a variable named result"
            "If you understand, output only 'ok. I'm ready.'"
        )
        messages = [{"role": "system", "content": FIREBASE_SYSTEM_INSTRUCTION}]
        messages.append({"role": "user", "content": user_input})
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
            my_output = safe_locals['result']
            if isinstance(my_output, CommandCursor):
                my_output = list(my_output)
            if isinstance(my_output, (Cursor, CommandCursor)):
                my_output = list(my_output)
            if isinstance( my_output, InsertOneResult):
                print(f"Insert succeeded! New ID:{ str(my_output.inserted_id)}")
                my_output = f"Insert succeeded! New ID:{ str(my_output.inserted_id)}"
            elif isinstance(my_output, DeleteResult):
                print(f"Delete Success! Deleted {my_output.deleted_count} document(s).")
                my_output = f"Delete Success! Deleted {my_output.deleted_count} document(s)."
            elif isinstance(my_output, UpdateResult):
                print(f"Update Success! Matched {my_output.matched_count}, modified {my_output.modified_count}.")
                my_output = f"Update Success! Matched {my_output.matched_count}, modified {my_output.modified_count}."


            # 返回查询结果
            return JsonResponse({"result": my_output})
        

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return render(request, 'nosql_query.html')


@login_required
def select_database(request):
    history = UserQueryHistory.objects.filter(user=request.user).order_by('-timestamp')
    history_data = [
        {
            'id': h.id,
            'query_text': h.query_text,
            'llm_response': h.llm_response,
            'timestamp': h.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for h in history
    ]

    return render(request, 'select_database.html', {
        'query_history_json': json.dumps(history_data, ensure_ascii=False)
    })


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


def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if User.objects.filter(username=username).exists():
            messages.error(request, "用户名已存在，请换一个！")
            return render(request, "home.html", {"show_register": True})
            # return redirect("register")

        if password != password2:
            messages.error(request, "两次输入的密码不一致")
            return redirect("register")

        User.objects.create_user(username=username, password=password)
        messages.success(request, "注册成功，请登录！")
        return redirect("login")

    return render(request, "home.html")


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
    code_text = code_text.replace("ok. I'm ready.", "").strip()  # 去除 "ok" 以及多余空格
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
            "You must ONLY return valid SQL command for MySQL. "
            "Do not include Python code such as import statements, and do not return any Python code for execution. "
            "Only return SQL queries that can be directly executed in MySQL. "
            "If you understand, output only 'ok. I'm ready.', Don't put anything else, And when you put sql, also only put sql sentences without anything else."
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
            connection.commit()  # 提交事务

            result = cursor.fetchall()
            if not result:
                print("No results found.")
            print(f"Query result: {result}")
            connection.close()

            # 存储用户查询和 LLM 返回的结果
            query_history = UserQueryHistory(user=request.user, query_text=user_input, llm_response=str(result))
            query_history.save()

            # 返回查询结果
            if safe_code.strip().lower().startswith("insert"):
                return JsonResponse({"message": "Data insert successful"})
            elif safe_code.strip().lower().startswith("update"):
                return JsonResponse({"message": "Data update successful"})
            elif safe_code.strip().lower().startswith("delete"):
                return JsonResponse({"message": "Data delete successful"})
            elif safe_code.strip().lower().startswith("select"):
                return JsonResponse({"result": result})
            else:
                return JsonResponse({"message": "The operation was successful, but the operation type could not be recognized。"})
        
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return JsonResponse({"error": "Database error occurred."}, status=500)

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, 'query_form.html')
