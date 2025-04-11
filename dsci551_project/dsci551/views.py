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


from django.db import models

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
            # 登录成功，跳转到查询页面
            return redirect('natural_language_query')  
        else:
            # 登录失败
            return render(request, 'login.html', {'error': '用户名或密码错误！'})
    else:
        return render(request, 'login.html')  # GET 请求直接渲染登录页面

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
    code_text = re.sub(r"```", "", code_text)
    code_text = re.sub(r"^\s*sql\s*", "", code_text)
    # 删除可能出现的 'sql' 字符串
    code_text = re.sub(r"sql", "", code_text)

    code_text = re.sub(r"```sql", "", code_text)

    # 确保清理掉多余的空格和换行，但不影响 SQL 查询的结构
    code_text = code_text.strip()  # 去除两端的空格

    return code_text


# 仅登录用户可以进行查询
@login_required
def natural_language_query(request):
    if request.method == 'POST':
        user_input = request.POST.get('query')
        deepseek_api_key = "sk-c6d9cd93a21b418da5adc6ef7fcb2479"
        deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"

        # 初始系统提示语
        db_schema = get_db_schema()  # 从函数获取动态的数据库结构

        # 更新系统提示语
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
            connection = pymysql.connect(
                host="localhost", user="root", password="", database="dsci551_project"
            )
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
