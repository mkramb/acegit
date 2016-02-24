from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect


class LoginRequiredMixin(object):
    redirect_field_name = REDIRECT_FIELD_NAME
    login_url = None

    @method_decorator(login_required(
        redirect_field_name=redirect_field_name, login_url=login_url
    ))
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect('/root')

        return super(LoginRequiredMixin, self). \
            dispatch(request, *args, **kwargs)
