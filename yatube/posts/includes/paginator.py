from django.core.paginator import Paginator


def paginator(post_list, count, request):
    paginator = Paginator(post_list, count)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
