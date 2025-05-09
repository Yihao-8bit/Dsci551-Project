

# ChatDB

ChatDB is an interactive, ChatGPT-like application that assists users in learning how to query data in various database systems (both SQL and NoSQL). Unlike traditional query interfaces, ChatDB provides a natural language approach to database interactions while still allowing real-time query execution and result display.

 
## 目录

- [上手指南](#上手指南)
  - [开发前的配置要求](#开发前的配置要求)
  - [安装步骤](#安装步骤)
- [文件目录说明](#文件目录说明)
- [开发的架构](#开发的架构)
- [部署](#部署)
- [使用到的框架](#使用到的框架)
- [贡献者](#贡献者)
  - [如何参与开源项目](#如何参与开源项目)
- [版本控制](#版本控制)
- [作者](#作者)
- [鸣谢](#鸣谢)


### Project Structure

```
DSCI551_PROJECT/
├── dsci551/
│ ├── migrations/
│ │ ├── init.py
│ │ ├── 0001_initial.py
│ │ ├── 0002_userqueryhistory.py
│ │ ├── 0003_alter_order_table.py
│ │ ├── 0004_alter_order_table.py
│ │ └── 0005_alter_order_customer_id.py
│ ├── static/
│ │ └── images/
│ │ └── logo.png
│ ├── templates/
│ │ ├── home.html
│ │ ├── login.html
│ │ ├── nosql_query.html
│ │ ├── query_form.html
│ │ ├── query_history.html
│ │ ├── register.html
│ │ └── select_database.html
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── tests.py
│ └── views.py
├── dsci551_project/
│ ├── init.py
│ ├── asgi.py
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── Final Report.docx
├── manage.py
└── requirements.txt
```





### Technology Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Django  
- **Databases**:  
  - MySQL (relational)  
  - MongoDB (NoSQL)  
- **Dependencies**:  
  - `Django==5.0.3`
  - `pymongo==4.12.1`
  - `PyMySQL==1.1.0`
  - `Requests==2.32.3`

### Setup and Installation

1. **Clone the repository**  
   ```bash
   git clone [repository-url]
   ```
2. **Install required dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
3. **Start Django server**  
   ```python
   python manage.py runserver
   ```
4. **Open your browser and navigate to: `http://127.0.0.1:8000`.** 


### Usage

1. **Login**  
2. **Database Selection**
    Choose between MySQL and MongoDB
4. **Natural Language Queries**
    Input the query statement
   

