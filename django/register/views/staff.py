from django.views import generic
from penguin import mixins


class MenuView(mixins.StaffOnlyMixin, generic.TemplateView):
    """機能一覧
    """
    template_name = 'register/staff_menu.html'


class WindowOpenView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録会 窓口業務 開始

    窓口名と対応する企画種別を選択
    """
    template_name = 'register/staff_window_open.html'


class WindowView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録会 窓口業務

    登録企画を選択→呼出・保留・受理・却下が可能
    """
    template_name = 'register/staff_window.html'


class SignageView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録会 案内表示

    企画登録 QR コードと各窓口の対応状況を表示
    """
    template_name = 'register/staff_signage.html'


class AdminProcessingView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録会 監督業務

    現在進行中（待機・対応中・保留）の企画登録について表示
    """
    template_name = 'register/staff_admin_processing.html'


class AdminFinishedView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録情報管理

    終了済（受理・却下）の企画登録について表示
    """
    template_name = 'register/staff_admin_finished.html'


class AdminStaffView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録担当スタッフを選択する

    企画登録会 監督業務や企画登録情報管理にアクセスできるスタッフを決定する
    """
    template_name = 'register/staff_admin_staff.html'


class AdminSlackView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録 slack ch. を指定する
    """
    template_name = 'register/staff_admin_slack.html'
