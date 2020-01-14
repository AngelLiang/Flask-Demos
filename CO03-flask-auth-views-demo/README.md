# 基于Flask的登录认证等页面示例

## 准备工作

首先需要编译sb-admin-2前端代码

安装npm和bower：

```
$ npm install -g bower
```

编译：

```
$ cd app/static/sb-admin-2
$ bower install
```

## 快速开始

```
$ pipenv install
$ pipenv run flask run
```

## 主要功能

- [X] 用户登录
- [X] 用户注册
- [X] 登录时要填验证码
- [X] 注册时要填验证码
- [X] 用户登录错误 X 次后需要填验证码
- [ ] 验证码输入框清空按钮
