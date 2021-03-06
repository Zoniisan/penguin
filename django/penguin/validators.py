from django.core.validators import RegexValidator

stid_validator = RegexValidator(
        regex=r'^[0-9]{10}$',
        message='半角数字10桁で入力してください'
    )

tel_validator = RegexValidator(
        regex=r'^[0-9]{10,11}$',
        message='半角数字10桁または11桁で入力してください'
    )

kana_validator = RegexValidator(
    regex=r'^[ぁ-んー]+$',
    message='ひらがなで入力してください'
)

symbol_validator = RegexValidator(
    regex=r'^[A-Z]$',
    message='半角英大文字 1 文字で入力してください'
)
