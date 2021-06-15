from django.forms import FileInput


class UserFileInput(FileInput):
    """Shows current file"""
    template_name = 'account/forms/widgets/user_file_input.html'

    def format_value(self, value):
        return getattr(value, 'url', 'profile_images/profile.jpg')
