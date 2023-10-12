#导入包
from werkzeug.utils import secure_filename
import pickle
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from flask import Flask, request, flash, render_template, redirect, url_for, session
from flask_login import UserMixin, LoginManager, login_required, logout_user, login_user, current_user
from website.utils.check_form import is_null, check_session

#创建APP,导入Pickle文件
app = Flask(__name__)
new_df = pickle.load(open("C:/Users/19928/Desktop/Projects/Project-1/Code/game_data.pkl", 'rb'))
vectors = pickle.load(open("C:/Users/19928/Desktop/Projects/Project-1/Code/vectors.pkl", 'rb'))
cv = pickle.load(open("C:/Users/19928/Desktop/Projects/Project-1/Code/cv.pkl", 'rb'))
similarity = pickle.load(open("C:/Users/19928/Desktop/Projects/Project-1/Code/similarity.pkl", 'rb'))

#LoginManager实例
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Access denied.'
login_manager.init_app(app)

# 初始化应用
login_manager.init_app(app)  

# 定义一个名为 User 的类
class User(object):
    # 构造函数，用于初始化用户对象
    def __init__(self, *args):
        # 初始化四个私有属性，初始值都设置为 None
        self.__id = None
        self.__name = None
        self.__password = None

    # 定义 id 属性的 getter 方法，用于获取用户的ID
    @property
    def id(self):
        return self.__id

    # 定义 id 属性的 setter 方法，用于设置用户的ID，并进行非空检查
    @id.setter
    def id(self, value):
        if value:
            self.__id = value

    # 定义 name 属性的 getter 方法，用于获取用户的姓名
    @property
    def name(self):
        return self.__name

    # 定义 name 属性的 setter 方法，用于设置用户的姓名，并进行非空检查
    @name.setter
    def name(self, value):
        if value:
            self.__name = value

    # 定义 password 属性的 getter 方法，用于获取用户的密码
    @property
    def password(self):
        return self.__password

    # 定义 password 属性的 setter 方法，用于设置用户的密码，并进行非空检查
    @password.setter
    def password(self, value):
        if value:
            self.__password = value


# 模拟数据库查询用户信息
class UserService:
    users = []
    idx = 0
    for line in open(r"database/user.txt", "r+"):
        # user_info = "yolo111" + "\t" + "123" + "\n"
        # user_table.write(user_info)
        if len(line.strip()) != 0 or line == "":
            if line.rstrip != "":
                user_info = line.rstrip().split("\t")
                user = User()
                user.id = user_info[0]
                user.name = user_info[1]
                user.password = user_info[2]
                users.append(user)
                idx += 1

    @classmethod
    def query_user_by_name(self, username):
        for user in self.users:
            if username == user.name:
                return user
        return None

    @classmethod
    def query_user_by_id(self, user_id):
        for user in self.users:
            if user_id == user.id:
                return user
        return None

    @classmethod
    def query_user_by_name_password(self, username, password):
        for user in self.users:
            if username == user.name and password == user.password:
                return user
        return None


user_service = UserService()
#Register,log in,log out设置
@login_manager.user_loader
def user_loader(user_id: str):
    """
    :param user_id:
    :return:
    """
    if UserService.query_user_by_id(int(user_id)) is not None:
        curr_user = User()
        curr_user.id = user_id
        return curr_user


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('login.html')
    else:
        # print(request.form)
        # print(request.get_json())
        username = request.form['name']
        password = request.form['password']
        if is_null(username, password):
            login_massage = "Please input username, password."
            return render_template("login.html", message=login_massage)

        user = UserService.query_user_by_name(username)
        print(user)
        if user is not None:
            login_massage = "User already existed"
            return render_template("login.html", message=login_massage)

        user = User()
        user.id = str(UserService.idx)
        UserService.idx += 1
        user.name = username
        user.password = password
        # elif is_existed(username, password):
        #     return render_template('index.html', username=username)
        # elif exist_user(username):
        #     login_massage = "温馨提示：密码错误，请输入正确密码"
        #     return render_template('login.html', message=login_massage)
        # else:
        #     login_massage = "温馨提示：不存在该用户，请先注册"
        #     return render_template('login.html', message=login_massage)
        with open(r"database/user.txt", "a") as user_table:
            user_info = str(user.id) + "\t" + user.name + "\t" + user.password + "\t" + user.age + "\r\n"
            user_table.write(user_info)
        session["username"] = username
        user = {
            "name": username,
        }
        # return redirect(url_for('index', user))
        return render_template("index.html", user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user_info = check_session(session)

        if user_info:
            return render_template("index.html", user=user_info)
        else:
            username = request.form['name_login']
            password = request.form['password_login']

            user = UserService.query_user_by_name(username)

            if user:
                user = UserService.query_user_by_name_password(username, password)
                if user:
                    user_info = {
                        "name": user.name,
                    }

                    session["username"] = user.name
                    return render_template("index.html", user=user_info)
                else:
                    login_massage = "Password wrong!"
                    return render_template("login.html", message=login_massage)
            else:
                login_massage = "Please register first!"
                return render_template("login.html", message=login_massage)
    else:
        return render_template("login.html")


@app.route('/logout')
def logout():
    # 通过Flask-Login的logout_user方法登出用户
    session.pop("username")
    return render_template("index.html")


@app.route('/' or "index")
def index():
    user_info = check_session(session)
    if user_info:
        return render_template("index.html", user=user_info)
    else:
        return render_template('index.html')
    

