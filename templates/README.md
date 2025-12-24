姓名：于智远
学号：202335450111
班级：23网络工程



一、 项目功能简介
本项目是一个基于 Python Flask 框架和 MySQL 数据库开发的多商家在线购物平台。系统实现了从商品上架、客户浏览、订单拆分、物流流转到销售统计的完整电商闭环。
核心功能模块：
1、用户权限系统 (RBAC)：
顾客 (Customer)：注册登录、浏览商品、使用购物车（支持数量修改）、结算订单、查看订单状态并确认收货。
商家 (Merchant)：管理自有商品（增删改查）、处理所属订单（点击发货）、查看店铺销售统计报表及客户行为日志（浏览/购买）。
超级管理员 (Admin)：管理全站账户，监控平台内所有商家与顾客的信息。
2、多商家订单拆分逻辑：
当顾客一次性购买不同商家的商品时，系统自动按照商家 ID 拆分为多个独立订单，确保商家之间的数据相互隔离，只能看到属于自己的交易记录。
3、订单全生命周期管理：
状态流转：待发货 (结算后) 

 待收货 (商家发货后) 

 已完成 (顾客确认收货后)。
4、销售报表与日志记录：
商家端实时统计总销售额。
自动记录客户的浏览和购买日志，帮助商家进行经营分析。

二、 运行方法 
1. 环境准备
确保你的计算机已安装 Python 3.x 和 MySQL 8.0+。
2. 安装依赖库
在项目根目录下打开终端，执行以下命令安装 Flask 及其扩展插件：
pip install flask flask_sqlalchemy flask_login pymysql
3. 数据库配置
登录 MySQL 终端，创建一个空的数据库：
CREATE DATABASE online_shop DEFAULT CHARACTER SET utf8mb4;
打开 app.py 文件，修改第 10 行 的数据库连接字符串，填入你的 MySQL 用户名和密码：
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://用户名:密码@localhost/online_shop'
4. 启动程序
在终端运行：
python app.py
注意：程序首次运行时，会根据 app.py 中的模型自动创建数据库表，并自动插入超级管理员账号及2个样例商家数据。
5. 访问系统
打开浏览器访问：http://127.0.0.1:5000

三、 测试账户 
角色	    用户名	       密码	            核心操作内容
超级管理员	admin	     super123	   进入“系统管理”查看所有用户
样例商家A	AppleStore	   123	       进行发货、管理 iPhone 商品
样例商家B	XiaomiStore	   123      管理小米系列商品、查看销售报表
普通顾客	(需自行注册) (自行设置)	  加入购物车并完成结算、确认收货
四、 技术栈 (Tech Stack)
后端: Python Flask
数据库: MySQL (SQLAlchemy ORM)
前端: HTML5, Bootstrap 5 (响应式设计)
权限管理: Flask-Login
部署环境: 阿里云/AWS + Gunicorn + Nginx (推荐)
