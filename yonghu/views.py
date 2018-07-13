# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseServerError
from django.template import Context, loader
from django.shortcuts import get_object_or_404,render_to_response
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils.translation import ugettext as _
from django.db.models import Q


from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from shejiao.settings import *
from yonghu.models import Note, UserProfile, Category, Event
from yonghu.feed import RSSRecentNotes, RSSUserRecentNotes
from utils import mailer, formatter, function, uploader, check_code
from .tasks import send_regist_success_mail, send_changeemail_success_mail
import io
from django.shortcuts import render
import itertools
import cStringIO, string, os, random
from PIL import Image, ImageDraw, ImageFont

# do login
def __do_login(request, _email, _password):
    _state = __check_login(request, _email, _password)
    if _state['success']:
        # save login info to session
        request.session['userip'] = _state['userip']
        request.session['islogin'] = True
        request.session['userid'] = _state['userid']
        request.session['email'] = _email
    return _state


# get session user id
def __user_id(request):
    return request.session.get('userid', -1)


# get sessio realname
def __id(request):
    return request.session.get('id', '')


# return user login status
def __is_login(request):
    return request.session.get('islogin', False)


# def __is_ip(request):
#     # if request.META.has_key('HTTP_X_FORWARDED_FOR'):
#     #     userip = request.META['HTTP_X_FORWARDED_FOR']
#     # else:
#     #     userip = request.META['REMOTE_ADDR']
#     # if userip == request.session.get('userip'):
#     _user = UserProfile.objects.get(id=request.session.get('userid'))
#     if _user.userip == request.session.get('userip'):
#         pass
#     else:
#         signout(request)
#         return


def __check_login(request, _email, _password):
    _state = {
        'success': False,
        'message': 'none',
        'userid': -1,
        'userip': ''
    }

    try:
        _user = UserProfile.objects.get(email=_email)
        # to decide password
        if (_user.password == function.md5_encode(_password)):
            _state['success'] = True
            _state['userid'] = _user.id
            # if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            #     _state['userip'] = request.META['HTTP_X_FORWARDED_FOR']
            # else:
            #     _state['userip'] = request.META['REMOTE_ADDR']
        else:
        # password incorrect
            _state['success'] = False
            _state['message'] = _(u'密码错误！')

    except (UserProfile.DoesNotExist):  # user not exist
        _state['success'] = False
        _state['message'] = _(u'用户不存在！')

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
        _state['message'] = _(u'请输入邮箱.')
        return _state

    if (_userinfo['password'] == ''):
        _state['success'] = False
        _state['message'] = _(u'请输入密码.')
        return _state

    # check username exist
    if (__check_email_exist(_userinfo['email'])):
        _state['success'] = False
        _state['message'] = _(u'用户已存在.')
        return _state

        # check password & confirm password
    if (_userinfo['password'] != _userinfo['confirm']):
        _state['success'] = False
        _state['message'] = _(u'密码确认有误.')
        return _state

    session_check_code = request.session['check_code']
    if _userinfo['post_check_code'].lower() != session_check_code.lower():
        _state['success'] = False
        _state['message'] = _(u'验证码有误.')
        return _state
    a = map("".join, list(itertools.product("abcdefghijklmnopqrstuvwxyz", repeat=5)))
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        _userip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        _userip = request.META['REMOTE_ADDR']
    _user = UserProfile(
        username=a[random.randint(0, 26 ** 5 - 1)],
        password=function.md5_encode(_userinfo['password']),
        email=_userinfo['email'],
        url=_userinfo['email'],
        userip=_userip
        # area = Area.objects.get(id=1)
    )
    # try:
    #     _user.password = make_password(_userinfo['password'])
    _user.save()
    _state['success'] = True
    request.session['islogin'] = True
    request.session['userid'] = _user.id
    request.session['email'] = _userinfo['email']
    request.session['userip'] = _userip
    send_regist_success_mail.delay(_userinfo)

    return _state


# response result message page
def __result_message(request, _title=_(u'提示消息'), _message=_('Unknow error,processing interrupted.'), _go_back_url=''):
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
    _page_title = _(u'盟友信息')
    _user = UserProfile.objects.get(email=_email)
    return render(request, "url.html",{'user':_user,'page_title':_page_title,'islogin': _islogin,})

@csrf_exempt
def friends(request):
    _islogin = __is_login(request)
    _page_title = _(u'盟友圈')
    if _islogin:
        # get friend messages if user is logined
        _login_user = UserProfile.objects.get(id=__user_id(request))
        _friends = _login_user.friend.all()
    else:
        return HttpResponseRedirect('/signin/')

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    p = Paginator(_friends, 2, request=request)
    friends = p.page(page)
    _context = {
        'page_title': _page_title,
        'islogin': _islogin,
        'userid': __user_id(request),
        'friends': friends,
    }
    return render(request,'users_list.html', _context)


def news(request):
    news = []
    for j in range(5):
        cur_events = []
        id = []
        for i in range(2):
            cur = random.randint(1, 4)
            id.append(str(cur))
            cur_event = Event.objects.get(id=cur)
            cur_events.append(cur_event.e_name.strip())
        news.append({'name': ' '.join(cur_events), 'ids': '@'.join(id)})
    content = {
        'events': news,
        'islogin': __is_login(request)
    }
    # key = str(i)
    # content[key] = {'name':' '.join(events),'ids':'@'.join(id)}
    return render(request, 'show.html', content)

def add(request,ids):
    _user = UserProfile.objects.get(id=__user_id(request))
    id = ids.split('@')
    for i in id:
        try:
            _user.associate.add(i)
        except:
            pass
    event = []
    for curid in id:
        cur_event = Event.objects.get(id=curid)
        event.append(cur_event.e_name)
    content = {
        'events':','.join(event),
        'islogin': __is_login(request)
    }
    return render(request,'add.html',content)


def showevent(request):
    _islogin = __is_login(request)
    _page_title = _(u'参与事件')
    user = UserProfile.objects.get(id=__user_id(request))
    # events = user.associate.all
    content = {
        'islogin':_islogin,
        'page_title':_page_title,
        'user':user
    }
    return render(request,'showevents.html',content)

def index(request):
    # get user login status
    _islogin = __is_login(request)
    _page_title = _(u'主页')

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
        _login_user = UserProfile.objects.get(id =__user_id(request))
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
    # _template = loader.get_template('index.html')

    context = {
        'page_title': _page_title,
        'notes': no_te,
        'islogin': _islogin,
        'userid': __user_id(request),
        # 'self_home': _self_home,
    }

    # _output = _template.render(_context)

    return render(request,'index.html',context)


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
@csrf_exempt
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
            'page_title': _(u'登录'),
            'state': _state
        }
        _output = _template.render(_context)
    return HttpResponse(_output)


def signup(request):
    # check is login
    _islogin = False

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
    # _template = loader.get_template('signup.html')
    _context = {
        'page_title': _(u'注册'),
        'state': _result,
    }
    # _output = _template.render(_context)
    return render(request,'signup.html',_context)


# signout view
def signout(request):
    _user = UserProfile.objects.get(id=request.session.get('userid'))
    _user.userip = ''
    _user.save(False)
    request.session['islogin'] = False
    request.session['userid'] = -1
    request.session['username'] = ''

    return HttpResponseRedirect('/signin')


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
            'gender': request.POST['gender'],
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
        _user.gender = _userinfo['gender']
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
                return __result_message(request, _(u'头像上传失败'), _upload_state['message'])

        _user.save(False)
        send_changeemail_success_mail.delay(_userinfo['email'])
        _state['message'] = _(u'修改成功.')
        # except:
        # return __result_message(request,u'错误','提交数据时出现异常，保存失败。')

    # body content
    # _template = loader.get_template('settings.html')
    _context = {
        'page_title': _(u'修改个人信息'),
        'state': _state,
        'islogin': _islogin,
        'user': _user,
    }
    return render(request, 'settings.html',_context)


def __do_changepassword(request, _userinfo):
    _state = {
        'success': False,
        'message': '',
    }


    if (_userinfo['newpassword'] == ''):
        _state['success'] = False
        _state['message'] = _(u'请输入密码.')
        return _state

        # check password & confirm password
    if (_userinfo['newpassword'] != _userinfo['confirm']):
        _state['success'] = False
        _state['message'] = _(u'密码确认有误.')
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
        _state['message'] = _(u'请输入邮箱.')
        return _state

    if (_userinfo['newpassword'] == ''):
        _state['success'] = False
        _state['message'] = _(u'请输入密码.')
        return _state

        # check password & confirm password
    if (_userinfo['newpassword'] != _userinfo['confirm']):
        _state['success'] = False
        _state['message'] = _(u'密码确认有误.')
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
            return __result_message(request, _(u'修改密码'), _(u'密码修改成功！'))
    else:
        _state = {
            'success': False,
            'message': _('')
        }
    _template = loader.get_template('forgetpwd.html')
    _context = {
        'page_title': _(u'修改密码'),
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
            return __result_message(request, _('Change successed'), _(u'密码修改成功！'))
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
        'page_title': _(u'账户信息'),
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

    _page_title = _(u'通信录')
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
        return __result_message(request, _(u'对不起'), _(u'用户不存在.'))

    # check friend exist
    try:
        _friend = UserProfile.objects.get(username=_username)
        _user.friend.add(_friend)
        return __result_message(request, _(u'成功'), _(u'添加成功.'))
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
        return __result_message(request, _(u'对不起'), _(u'用户不存在.'))

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

