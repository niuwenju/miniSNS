# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseServerError
from django.template import Context, loader
from django.shortcuts import get_object_or_404,render_to_response
from django.core.paginator import Paginator
from django.core import serializers
from django.utils.translation import ugettext as _
from django.db.models import Q


from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from shejiao.settings import *
from yonghu.models import Note, UserProfile, Category
from yonghu.feed import RSSRecentNotes, RSSUserRecentNotes
from utils import mailer, formatter, function, uploader, check_code
import io
from django.shortcuts import render
import itertools,random
import cStringIO, string, os, random
from PIL import Image, ImageDraw, ImageFont

# do login
def __do_login(request, _email, _password):
    _state = __check_login(request, _email, _password)
    if _state['success']:
        # save login info to session
        request.session['islogin'] = True
        request.session['userid'] = _state['userid']
        request.session['email'] = _email
    return _state


# get session user id
def __user_id(request):
    return request.session.get('userid', -1)


# get sessio realname
def __e_mail(request):
    return request.session.get('email', '')


# return user login status
def __is_login(request):
    return request.session.get('islogin', False)


def __check_login(request, _email, _password):
    _state = {
        'success': False,
        'message': 'none',
        'userid': -1,
    }

    try:
        _user = UserProfile.objects.get(email=_email)
        # to decide password
        if (_user.password == function.md5_encode(_password)):
            _state['success'] = True
            _state['userid'] = _user.id

        else:
        # password incorrect
            _state['success'] = False
            _state['message'] = _('密码错误！')

    except (UserProfile.DoesNotExist):  # user not exist
        _state['success'] = False
        _state['message'] = _('用户不存在！')

    return _state


# check user was existed
def __check_email_exist(_email):
    _exist = True

    try:
        _user = UserProfile.objects.get(email=_email)
        _exist = True
    except (UserProfile.DoesNotExist):
        _exist = False

    return _exist


# post signup data
def __do_signup(request, _userinfo):
    _state = {
        'success': False,
        'message': '',
        # 'userid': -1,
    }

    # check username exist
    if (_userinfo['email'] == ''):
        _state['success'] = False
        _state['message'] = _('请输入邮箱.')
        return _state

    if (_userinfo['password'] == ''):
        _state['success'] = False
        _state['message'] = _('请输入密码.')
        return _state

    # check username exist
    if (__check_email_exist(_userinfo['email'])):
        _state['success'] = False
        _state['message'] = _('用户已存在.')
        return _state

        # check password & confirm password
    if (_userinfo['password'] != _userinfo['confirm']):
        _state['success'] = False
        _state['message'] = _('密码确认有误.')
        return _state

    session_check_code = request.session['check_code']
    if _userinfo['post_check_code'].lower() != session_check_code.lower():
        _state['success'] = False
        _state['message'] = _('验证码有误.')
        return _state
    a = map("".join, list(itertools.product("abcdefghijklmnopqrstuvwxyz", repeat=5)))
    _user = UserProfile(
        username=a[random.randint(0, 26 ** 5 - 1)],
        password=_userinfo['password'],
        email=_userinfo['email'],
        url='url_list/' + _userinfo['email'],
        # area = Area.objects.get(id=1)
    )
    # try:
    #     _user.password = make_password(_userinfo['password'])
    _user.save()
    _state['success'] = True
    request.session['islogin'] = True
    request.session['userid'] = _user.id
    request.session['email'] = _userinfo['email']
    mailer.send_regist_success_mail(_userinfo)

    return _state


# response result message page
def __result_message(request, _title=_('提示消息'), _message=_('Unknow error,processing interrupted.'), _go_back_url=''):
    _islogin = __is_login(request)

    if _go_back_url == '':
        _go_back_url = function.get_referer_url(request)

    # body content
    _template = loader.get_template('result_message.html')

    _context = Context({
        'page_title': _title,
        'message': _message,
        'go_back_url': _go_back_url,
        'islogin': _islogin
    })

    _output = _template.render(_context)

    return HttpResponse(_output)


# user messages view and page
def url_list(request,_email):
    _islogin = __is_login(request)
    _page_title = _('盟友信息')
    _user = UserProfile.objects.get(email=_email)
    return render(request, "url.html",{'user':_user,'page_title':_page_title,'islogin': _islogin,})


def search_friends(request):
    _islogin = __is_login(request)
    _page_title = _('搜索用户')
    try:
        # get post params
        _search = request.POST['search']
        _is_post = True
    except (KeyError):
        _is_post = False

    if _is_post:
        # check login
        if not _islogin:
            return HttpResponseRedirect('/signin/')

        try:
            _user = UserProfile.objects.filter(username__icontains=_search)
        except:
            return HttpResponseRedirect('/signin/')

        try:
         page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(_user, 2, request=request)
        users = p.page(page)
        _template = loader.get_template('friend_list.html')

        _context = {
            'page_title': _page_title,
            'islogin': _islogin,
            'userid': __user_id(request),
            'users': users,
        }

        _output = _template.render(_context)

        return HttpResponse(_output)
    else:
        _page_title = _('盟友圈')

        _login_user = None

        if _islogin:
            # get friend messages if user is logined
            _login_user = UserProfile.objects.get(email=__e_mail(request))
            _friends = _login_user.friend.all()
        else:
            _login_user = None

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(_friends, 2, request=request)
        friends = p.page(page)
        _template = loader.get_template('users_list.html')

        _context = {
            'page_title': _page_title,
            'islogin': _islogin,
            'userid': __user_id(request),
            'friends': friends,
        }

        _output = _template.render(_context)

        return HttpResponse(_output)
# def index_user(reqeest)


def index(request):
    # get user login status
    _islogin = __is_login(request)
    _page_title = _('主页')

    try:
        # get post params
        _message = request.POST['message']
        _is_post = True
    except (KeyError):
        _is_post = False

    # save message
    if _is_post:
        # check login
        if not _islogin:
            return HttpResponseRedirect('/signin/')

        # save messages
        (_category, _is_added_cate) = Category.objects.get_or_create(name=u'网页')

        try:
            _user = UserProfile.objects.get(id=__user_id(request))
        except:
            return HttpResponseRedirect('/signin/')

        _note = Note(message=_message, category=_category, user=_user)
        _note.save()

        return HttpResponseRedirect('/user/')

    _userid = -1

    if _islogin:
        # get friend messages if user is logined
        _login_user = UserProfile.objects.get(email=__e_mail(request))
    else:
        _login_user = None
    if _login_user:
        _query_users = [_login_user]
        _query_users.extend(_login_user.friend.all())
        _notes = Note.objects.filter(user__in=_query_users).order_by('-addtime')
    else:
            # can't get  message
            _notes = []  # Note.objects.order_by('-addtime')

    # body content
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    p = Paginator(_notes, 2, request=request)
    no_te = p.page(page)
    _template = loader.get_template('index.html')

    _context = {
        'page_title': _page_title,
        'notes': no_te,
        'islogin': _islogin,
        'userid': __user_id(request),
        # 'self_home': _self_home,
    }

    _output = _template.render(_context)

    return HttpResponse(_output)


# detail view
def detail(request, _id):
    # get user login status
    _islogin = __is_login(request)

    _note = get_object_or_404(Note, id=_id)

    # body content
    _template = loader.get_template('detail.html')

    _context = {
        'page_title': _('%s\'s message %s') % (_note.user.realname, _id),
        'item': _note,
        'islogin': _islogin,
        'userid': __user_id(request),
    }

    _output = _template.render(_context)

    return HttpResponse(_output)


def detail_delete(request, _id):
    # get user login status
    _islogin = __is_login(request)

    _note = get_object_or_404(Note, id=_id)

    _message = ""

    try:
        _note.delete()
        _message = _('Message deleted.')
    except:
        _message = _('Delete failed.')

    return __result_message(request, _('Message %s') % _id, _message)


# signin view
def signin(request):
    # get user login status
    _islogin = __is_login(request)

    try:
        # get post params
        _e_mail = request.POST['email']
        _password = request.POST['password']
        # post_check_code = request.POST.get('check_code')
        # # session_check_code = request.session['check_code']
        _is_post = True
    except (KeyError):
        _is_post = False

    # check username and password
    if _is_post:
        _state = __do_login(request, _e_mail, _password)
    else:
        _state = {
            'success': False,
            'message': ""
        }
    if _state['success']:
            return index(request)
    else:
        _template = loader.get_template('signin.html')
        _context = {
            'page_title': _('登录'),
            'state': _state
        }
        _output = _template.render(_context)
    return HttpResponse(_output)


def signup(request):
    # check is login
    _islogin = __is_login(request)

    if (_islogin):
        return HttpResponseRedirect('/')

    _userinfo = {
        'email': '',
        'password': '',
        'confirm': '',
        'check_code':'',
        # 'realname': '',
        # 'email': '',
    }

    try:
        # get post params
        # _userinfo = {
        #     'username': request.POST.get('username',""),
        #     'password': request.POST.get('password',""),
        #     'confirm': request.POST.get('confirm',""),
        #     'post_check_code' : request.POST.get('check_code',""),
        # }
        _userinfo = {
            'email': request.POST['email'],
            'password': request.POST['password'],
            'confirm': request.POST['confirm'],
            'post_check_code' : request.POST['check_code'],
        }
        _is_post = True
    except (KeyError):
        _is_post = False

    if (_is_post):
        _state = __do_signup(request, _userinfo)
    else:
        _state = {
            'success': False,
            'message': ""
        }

    if (_state['success']):
        return index(request)
        #return __result_message(request, _('Signup successed'), _('Your account was registed success.'))

    _result = {
        'success': _state['success'],
        'message': _state['message'],
        'form': {
            # 'username': _userinfo['username'],
            # 'realname': _userinfo['realname'],
             'email': _userinfo['email'],
        }
    }

    # body content
    _template = loader.get_template('signup.html')
    _context = {
        'page_title': _('注册'),
        'state': _result,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


# signout view
def signout(request):
    request.session['islogin'] = False
    request.session['userid'] = -1
    request.session['username'] = ''

    return HttpResponseRedirect('/')


def settings(request):
    # check is login
    _islogin = __is_login(request)

    if(not _islogin):
        return HttpResponseRedirect('/signin/')

    _user_id = __user_id(request)
    try:
        _user = UserProfile.objects.get(id=_user_id)
    except:
        return HttpResponseRedirect('/signin/')

    if request.method == "POST":
        # get post params
        _userinfo = {
            'face': request.FILES.get('face', None),
            'username': request.POST['username'],
            'sex': request.POST['sex'],
            'email': request.POST['email'],
            "about": request.POST['about'],
            "phone": request.POST['phone'],
        }
        _is_post = True
    else:
        _is_post = False

    _state = {
        'message': ''
    }

    # save user info
    if _is_post:
        _user.username = _userinfo['username']
        _user.sex = _userinfo['sex']
        _user.email = _userinfo['email']
        _user.about = _userinfo['about']
        _user.phone = _userinfo['phone']
        _file_obj = _userinfo['face']
        # try:
        if _file_obj:
            _upload_state = uploader.upload_face(_file_obj)
            if _upload_state['success']:
                _user.face = _upload_state['message']
            else:
                return __result_message(request, _('头像上传失败'), _upload_state['message'])

        _user.save(False)
        mailer.send_changeemail_success_mail(_userinfo)
        _state['message'] = _('修改成功.')
        # except:
        # return __result_message(request,u'错误','提交数据时出现异常，保存失败。')

    # body content
    _template = loader.get_template('settings.html')
    _context = {
        'page_title': _('修改个人信息'),
        'state': _state,
        'islogin': _islogin,
        'user': _user,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


def __do_changepassword(request, _userinfo):
    _state = {
        'success': False,
        'message': '',
    }


    if (_userinfo['newpassword'] == ''):
        _state['success'] = False
        _state['message'] = _('请输入密码.')
        return _state

        # check password & confirm password
    if (_userinfo['newpassword'] != _userinfo['confirm']):
        _state['success'] = False
        _state['message'] = _('密码确认有误.')
        return _state

    _user = UserProfile.objects.get(username=request.session['username'])
    _user.password = _userinfo['newpassword']
    # try:
    _user.save()
    _state['success'] = True
    _state['message'] = _('Successed.')

    return _state


def __do_forgetpwd(request, _userinfo):
    _state = {
        'success': False,
        'message': '',
    }

    if (_userinfo['email'] == ''):
        _state['success'] = False
        _state['message'] = _('请输入邮箱.')
        return _state

    if (_userinfo['newpassword'] == ''):
        _state['success'] = False
        _state['message'] = _('请输入密码.')
        return _state

        # check password & confirm password
    if (_userinfo['newpassword'] != _userinfo['confirm']):
        _state['success'] = False
        _state['message'] = _('密码确认有误.')
        return _state

    _user = UserProfile.objects.get(email=request.session['email'])
    _user.password = _userinfo['newpassword']
    # try:
    _user.save()
    _state['success'] = True
    _state['message'] = _('Successed.')
    # except:
    # _state['success'] = False
    # _state['message'] = '程序异常,注册失败.'

    # send regist success mail

    return _state


def forgetpwd(request):
    _userinfo = {
        'email': '',
        'newpassword': '',
        'confirm': '',
    }

    try:
        # get post params
        _userinfo = {
            'email': request.POST['email'],
            'newpassword': request.POST['newpassword'],
            'confirm': request.POST['confirm'],

        }
        _is_post = True
    except (KeyError):
        _is_post = False

        # check username and password
    if _is_post:
        _state = __do_forgetpwd(request, _userinfo)
        if _state['success']:
            return __result_message(request, _('修改密码'), _('密码修改成功！'))
    else:
        _state = {
            'success': False,
            'message': _('')
        }
    _template = loader.get_template('forgetpwd.html')
    _context = {
        'page_title': _('修改密码'),
        'state': _state,
        # 'islogin': _islogin,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


def changepassword(request):
    # check is login
    _islogin = __is_login(request)

    if (not _islogin):
        return HttpResponseRedirect('/signin/')

    _user_id = __user_id(request)
    try:
        _user = UserProfile.objects.get(id=_user_id)
    except:
        return HttpResponseRedirect('/signin/')
    _userinfo = {
        # 'username': '',
        'newpassword': '',
        'confirm': '',
    }

    try:
        # get post params
        _userinfo = {
            # 'username': request.POST['username'],
            'newpassword': request.POST['newpassword'],
            'confirm': request.POST['confirm'],

        }
        _is_post = True
    except (KeyError):
        _is_post = False

        # check username and password
    if _is_post:
        _state = __do_changepassword(request, _userinfo)
        if _state['success']:
            return __result_message(request, _('Change successed'), _('密码修改成功！'))
    else:
        _state = {
            'success': False,
            'message': _('')
        }
    _template = loader.get_template('changepassword.html')
    _context = {
        'page_title': _('Changepassword'),
        'state': _state,
        'islogin': _islogin,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


# all users list
def edit(request):
    _islogin = __is_login(request)

    if (not _islogin):
        return HttpResponseRedirect('/signin/')

        # _user_id = __user_id(request)
        # try:
        #   _user = UserProfile.objects.get(id=_user_id)
        # except:
        # return HttpResponseRedirect('/signin/')
    _template = loader.get_template('edit.html')
    _context = {
        'page_title': _('账户信息'),
        'islogin': _islogin,
        # 'state': _state,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


# def users_index(request):
#     return users_list(request)


# all users list
def users_list(request):
    # check is login
    _islogin = __is_login(request)

    _page_title = _('通信录')
    _users = UserProfile.objects.order_by('-addtime')
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    p = Paginator(_users,2, request=request)
    us_er = p.page(page)

    _login_user = None
    _login_user_friend_list = None
    if _islogin:
        try:
            _login_user = UserProfile.objects.get(id=__user_id(request))
            _login_user_friend_list = _login_user.friend.all()
        except:
            _login_user = None


    return render_to_response('users_list.html', {
        'page_title': _page_title,
        'users': us_er,
        # 'login_user_friend_list': _login_user_friend_list,
        'islogin': _islogin,
        'userid': __user_id(request),
        })


    # add friend
def friend_add(request, _username):
    # check is login
    _islogin = __is_login(request)

    if (not _islogin):
        return HttpResponseRedirect('/signin/')

    _state = {
        "success": False,
        "message": "",
    }

    _user_id = __user_id(request)
    try:
        _user = UserProfile.objects.get(id=_user_id)
    except:
        return __result_message(request, _('对不起'), _('用户不存在.'))

    # check friend exist
    try:
        _friend = UserProfile.objects.get(username=_username)
        _user.friend.add(_friend)
        return __result_message(request, _('成功'), _('添加成功.'))
    except:
        return __result_message(request, _('对不起'), _('用户不存在.'))


def friend_remove(request, _username):
    """
    summary:
        解除与某人的好友关系
    """
    # check is login
    _islogin = __is_login(request)

    if (not _islogin):
        return HttpResponseRedirect('/signin/')

    _state = {
        "success": False,
        "message": "",
    }

    _user_id = __user_id(request)
    try:
        _user = UserProfile.objects.get(id=_user_id)
    except:
        return __result_message(request, _('对不起'), _('用户不存在.'))

    # check friend exist
    try:
        _friend = UserProfile.objects.get(username=_username)
        _user.friend.remove(_friend)
        return __result_message(request, _('Successed'), u'删除成功.')
    except:
        return __result_message(request, _('Undisposed'), u'盟友不存在.')


def api_note_add(request):
    # get querystring params
    _username = request.GET['uname']
    _password = function.md5_encode(request.GET['pwd'])
    _message = request.GET['msg']
    _from = request.GET['from']

    # Get user info and check user
    try:
        _user = UserProfile.objects.get(username=_username, password=_password)
    except:
        return HttpResponse("-2")

    # Get category info ,If it not exist create new
    (_cate, _is_added_cate) = Category.objects.get_or_create(name=_from)

    try:
        _note = Note(message=_message, user=_user, category=_cate)
        _note.save()
        return HttpResponse("1")
    except:
        return HttpResponse("-1")


# 将check_code包放在合适的位置，导入即可，我是放在utils下面


def create_code_img(request):
    f = io.BytesIO()  # 直接在内存开辟一点空间存放临时生成的图片
    img, code = check_code.create_validate_code()  # 调用check_code生成照片和验证码
    request.session['check_code'] = code  # 将验证码存在服务器的session中，用于校验
    img.save(f, 'PNG')  # 生成的图片放置于开辟的内存中
    return HttpResponse(f.getvalue())  # 将内存的数据读取出来，并以HttpResponse返回