

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
- Choose between MySQL and MongoDB
3. **Natural Language Queries**
- Input the query statement
   
### 作者

xxx@xxxx

知乎:xxxx  &ensp; qq:xxxxxx    

 *您也可以在贡献者名单中参看所有参与该项目的开发者。*

### 版权说明

该项目签署了MIT 授权许可，详情请参阅 [LICENSE.txt](https://github.com/shaojintian/Best_README_template/blob/master/LICENSE.txt)

### 鸣谢


- [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
- [Img Shields](https://shields.io)
- [Choose an Open Source License](https://choosealicense.com)
- [GitHub Pages](https://pages.github.com)
- [Animate.css](https://daneden.github.io/animate.css)
- [xxxxxxxxxxxxxx](https://connoratherton.com/loaders)

<!-- links -->
[your-project-path]:shaojintian/Best_README_template
[contributors-shield]: https://img.shields.io/github/contributors/shaojintian/Best_README_template.svg?style=flat-square
[contributors-url]: https://github.com/shaojintian/Best_README_template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/shaojintian/Best_README_template.svg?style=flat-square
[forks-url]: https://github.com/shaojintian/Best_README_template/network/members
[stars-shield]: https://img.shields.io/github/stars/shaojintian/Best_README_template.svg?style=flat-square
[stars-url]: https://github.com/shaojintian/Best_README_template/stargazers
[issues-shield]: https://img.shields.io/github/issues/shaojintian/Best_README_template.svg?style=flat-square
[issues-url]: https://img.shields.io/github/issues/shaojintian/Best_README_template.svg
[license-shield]: https://img.shields.io/github/license/shaojintian/Best_README_template.svg?style=flat-square
[license-url]: https://github.com/shaojintian/Best_README_template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/shaojintian
