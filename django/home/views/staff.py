from django.http import Http404, HttpResponse
from django.template import loader
from django.views import generic
from home.models import Department, User
from penguin import mixins
from theme.models import ThemeStaff


class MenuView(mixins.StaffOnlyMixin, generic.TemplateView):
    """スタッフ向け機能一覧
    """
    template_name = 'home/staff_menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 投票テーマ案投票スタッフかどうかを判定
        context['is_theme_staff'] = ThemeStaff.objects.check_perm(
            self.request.user
        )

        return context


class MemberView(mixins.StaffOnlyMixin, generic.TemplateView):
    """スタッフ一覧

    部局担当・学年・五十音順に表示
    """
    template_name = 'home/staff_member.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 部局担当別にユーザーリストを作成
        context['department_dict'] = {
            department.name: department.member.all().order_by('-grade')
            for department in Department.objects.all()
        }

        return context


class DownloadVcfView(mixins.StaffOnlyMixin, generic.View):
    """スタッフ連絡先データ ダウンロード

    スタッフの連絡先を vcf ファイルでダウンロードさせる。
    スマホで読み込めば連絡先として登録できるはず。

    Tips: vcf ファイルの 1 行目を空白にすると文字化けする（iOS 14.2）
    """

    def get(self, request, **kwargs):
        # mode を取得してダウンロードすべきユーザーのリストを作る
        user_list = get_user_list(kwargs['mode'])

        # 'penguin.vcf' としてダウンロードさせる
        response = HttpResponse(content_type='text/x-vcard; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="penguin.vcf"'

        # vcf テンプレートに情報を書き込む
        t = loader.get_template('home/vcf/template.vcf')
        c = {
            'user_list': user_list
        }
        response.write(t.render(c))

        return response


def get_user_list(mode):
    """連絡先をダウンロードすべきユーザーのリストを作成

    Args:
        mode(str): 'all', 'b1', 'b2', 'b3' のいずれか（学年で指定）
    Returns:
        list<User>: DL すべきユーザーのリスト
    """
    if mode == 'all':
        return [
            user for user in User.objects.all()
            if user.is_staff
        ]
    elif mode == 'b1':
        return [
            user for user in User.objects.all()
            if user.is_staff and user.grade == 'B1'
        ]
    elif mode == 'b2':
        return [
            user for user in User.objects.all()
            if user.is_staff and user.grade == 'B2'
        ]
    elif mode == 'b3':
        return [
            user for user in User.objects.all()
            if user.is_staff and user.grade == 'B3'
        ]
    else:
        # 想定されていない mode が指定された場合は 404
        raise Http404
