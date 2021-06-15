from django.forms import FileInput, PasswordInput


class UserFileInput(FileInput):
    """Shows current file"""
    template_name = 'account/forms/widgets/user_file_input.html'

    def format_value(self, value):
        return getattr(value, 'url', 'profile_images/profile.jpg')


class PasswordInputWithViewToggle(PasswordInput):
    template_name = 'account/forms/widgets/c_password.html'

    class Media:
        css = {
            'all': ('account/css/forms/widgets/c_password.css',)
        }
        js = ('account/js/forms/widgets/cPassword.js',)
