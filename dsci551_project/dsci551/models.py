from django.db import models

from django.contrib.auth.models import User

class UserQueryHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 关联用户
    query_text = models.TextField()  # 用户的查询文本
    llm_response = models.TextField()  # LLM 返回的查询结果
    timestamp = models.DateTimeField(auto_now_add=True)  # 查询时间

    def __str__(self):
        return f"Query by {self.user.username} at {self.timestamp}"


class Customer(models.Model):
    customer_id = models.CharField(max_length=50, primary_key=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    segment = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.customer_name

class Order(models.Model):
    row_id = models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=50, null=True, blank=True)
    order_date = models.DateField(null=True, blank=True)
    ship_date = models.DateField(null=True, blank=True)
    ship_mode = models.CharField(max_length=50, null=True, blank=True)
    sales = models.FloatField(null=True, blank=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', db_column='customer_id')
    product_id = models.CharField(max_length=50, null=True, blank=True)


    def __str__(self):
        return self.order_id


class Product(models.Model):
    product_id = models.CharField(max_length=50, primary_key=True)
    product_name = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    sub_category = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.product_name
